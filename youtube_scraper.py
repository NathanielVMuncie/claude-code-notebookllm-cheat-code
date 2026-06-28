"""
YouTube scraper using yt-dlp.

Extracts video metadata, transcripts/subtitles, and descriptions from
YouTube videos, channels, or playlists — formatted for NotebookLLM ingestion.
"""

import json
import re
import tempfile
from pathlib import Path
from typing import Optional

import yt_dlp


def _make_ydl_opts(quiet: bool = True) -> dict:
    return {
        "quiet": quiet,
        "no_warnings": quiet,
        "extract_flat": False,
        "writesubtitles": False,
