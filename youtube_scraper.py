"""
YouTube scraper using yt-dlp.

Extracts video metadata, transcripts/subtitles, and descriptions from
YouTube videos, channels, or playlists — formatted for NotebookLLM ingestion.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

import yt_dlp


def _make_ydl_opts(quiet: bool = True) -> dict:
    return {
        "quiet": quiet,
        "no_warnings": quiet,
        "extract_flat": False,
        "writesubtitles": False,
        "writeautomaticsub": False,
        "skip_download": True,
    }


def _clean_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing space."""
    return re.sub(r"\s+", " ", text).strip()


def _format_duration(seconds: Optional[int]) -> str:
    if not seconds:
        return "unknown"
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _extract_subtitles(info: dict) -> Optional[str]:
    """
    Return the best available transcript text (manual > auto-generated).
    Tries English first, then falls back to the first available language.
    """
    for sub_key in ("subtitles", "automatic_captions"):
        subs = info.get(sub_key) or {}
        lang = "en" if "en" in subs else (next(iter(subs), None))
        if not lang:
            continue
        for fmt in subs[lang]:
            if fmt.get("ext") == "json3":
                # yt-dlp can return subtitle data inline for json3
                data = fmt.get("data")
                if data:
                    return _parse_json3_subtitles(data)
    return None


def _parse_json3_subtitles(data: str) -> str:
    """Parse YouTube json3 subtitle format into plain text."""
    try:
        obj = json.loads(data) if isinstance(data, str) else data
        parts = []
        for event in obj.get("events", []):
            segs = event.get("segs")
            if segs:
                parts.append("".join(s.get("utf8", "") for s in segs))
        return _clean_text(" ".join(parts))
    except (json.JSONDecodeError, TypeError):
        return ""


def scrape_video(url: str, include_subtitles: bool = True) -> dict:
    """
    Scrape metadata (and optionally subtitles) for a single YouTube video.

    Returns a dict with keys:
        id, title, channel, upload_date, duration, view_count,
        like_count, description, tags, thumbnail, url, transcript
    """
    opts = _make_ydl_opts()
    if include_subtitles:
        opts.update(
            {
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["en", "en-US", "en-GB"],
                "subtitlesformat": "json3",
            }
        )

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    transcript = _extract_subtitles(info) if include_subtitles else None

    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "channel": info.get("uploader") or info.get("channel"),
        "channel_url": info.get("uploader_url") or info.get("channel_url"),
        "upload_date": info.get("upload_date"),  # YYYYMMDD string
        "duration": _format_duration(info.get("duration")),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "description": _clean_text(info.get("description") or ""),
        "tags": info.get("tags") or [],
        "thumbnail": info.get("thumbnail"),
        "url": info.get("webpage_url") or url,
        "transcript": transcript,
    }


def scrape_playlist(
    url: str,
    max_videos: Optional[int] = None,
    include_subtitles: bool = True,
) -> list[dict]:
    """
    Scrape all videos in a YouTube playlist or channel.

    Args:
        url: Playlist or channel URL.
        max_videos: Cap the number of videos processed (None = all).
        include_subtitles: Whether to fetch transcripts.

    Returns a list of video dicts (same schema as scrape_video).
    """
    flat_opts = {**_make_ydl_opts(), "extract_flat": "in_playlist"}
    if max_videos:
        flat_opts["playlistend"] = max_videos

    with yt_dlp.YoutubeDL(flat_opts) as ydl:
        playlist_info = ydl.extract_info(url, download=False)

    entries = playlist_info.get("entries") or []
    results = []
    for entry in entries:
        video_url = entry.get("url") or entry.get("webpage_url")
        if not video_url:
            continue
        try:
            results.append(scrape_video(video_url, include_subtitles=include_subtitles))
        except yt_dlp.utils.DownloadError as exc:
            results.append({"url": video_url, "error": str(exc)})

    return results


def format_for_notebookllm(videos: list[dict] | dict, source_label: str = "") -> str:
    """
    Format scraped video data as a plain-text document suitable for
    pasting into NotebookLLM as a source.

    Each video becomes a titled section with metadata + description +
    transcript (when available).
    """
    if isinstance(videos, dict):
        videos = [videos]

    lines = []
    if source_label:
        lines.append(f"SOURCE: {source_label}")
        lines.append("=" * 60)
        lines.append("")

    for i, v in enumerate(videos, 1):
        if "error" in v:
            lines.append(f"[Video {i} — fetch error: {v['error']}]")
            lines.append("")
            continue

        lines.append(f"## {v.get('title', 'Untitled')}")
        lines.append(f"URL: {v.get('url', '')}")
        lines.append(f"Channel: {v.get('channel', 'unknown')}")
        lines.append(f"Uploaded: {v.get('upload_date', 'unknown')}")
        lines.append(f"Duration: {v.get('duration', 'unknown')}")

        view = v.get("view_count")
        if view is not None:
            lines.append(f"Views: {view:,}")

        tags = v.get("tags") or []
        if tags:
            lines.append(f"Tags: {', '.join(tags[:10])}")

        lines.append("")

        desc = v.get("description", "")
        if desc:
            lines.append("### Description")
            lines.append(desc[:2000])  # cap very long descriptions
            lines.append("")

        transcript = v.get("transcript")
        if transcript:
            lines.append("### Transcript")
            lines.append(transcript)
            lines.append("")

        lines.append("-" * 60)
        lines.append("")

    return "\n".join(lines)


def scrape_to_file(
    url: str,
    output_path: str,
    max_videos: Optional[int] = None,
    include_subtitles: bool = True,
    output_format: str = "text",
) -> Path:
    """
    Scrape a video, playlist, or channel and write results to a file.

    Args:
        url: YouTube URL (video, playlist, or channel).
        output_path: Destination file path.
        max_videos: Limit for playlists/channels.
        include_subtitles: Whether to include transcripts.
        output_format: "text" (NotebookLLM-ready) or "json".

    Returns the resolved output Path.
    """
    # Detect if it's a playlist/channel or a single video
    is_multi = any(
        kw in url
        for kw in ("playlist?list=", "/channel/", "/@", "/c/", "/user/")
    ) or "list=" in url

    if is_multi:
        data = scrape_playlist(url, max_videos=max_videos, include_subtitles=include_subtitles)
    else:
        data = [scrape_video(url, include_subtitles=include_subtitles)]

    out = Path(output_path)
    if output_format == "json":
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        out.write_text(format_for_notebookllm(data, source_label=url), encoding="utf-8")

    return out
