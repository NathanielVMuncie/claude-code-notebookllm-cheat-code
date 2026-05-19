#!/usr/bin/env python3
"""CLI entry point for the YouTube scraper."""

import argparse
import sys
from youtube_scraper import scrape_to_file


def main():
    parser = argparse.ArgumentParser(
        description="Scrape YouTube videos/playlists into NotebookLLM-ready text or JSON.",
    )
    parser.add_argument("url", help="YouTube video, playlist, or channel URL")
    parser.add_argument(
        "-o", "--output",
        default="output.txt",
        help="Output file path (default: output.txt)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format: 'text' (NotebookLLM) or 'json' (default: text)",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        metavar="N",
        help="Limit number of videos for playlists/channels",
    )
    parser.add_argument(
        "--no-subtitles",
        action="store_true",
        help="Skip transcript/subtitle extraction",
    )

    args = parser.parse_args()

    print(f"Scraping: {args.url}")
    out_path = scrape_to_file(
        url=args.url,
        output_path=args.output,
        max_videos=args.max_videos,
        include_subtitles=not args.no_subtitles,
        output_format=args.format,
    )
    print(f"Saved to: {out_path}")


if __name__ == "__main__":
    main()
