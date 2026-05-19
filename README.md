claude-code-notebookllm-cheat-code
An automated knowledge-ingestion engine that hooks Google's internal NotebookLM RAG pipeline into local content creation workflows. By utilizing notebooklm-py's browser-automation layer (via Playwright) and its native Model Context Protocol (MCP) server, this project completely bypasses manual Web UI limitations to scrape, parse, ingest, and synthesize YouTube video assets directly inside your terminal or via Claude Code.

Architectural Blueprint
The system circumvents traditional scraping constraints (IP blocks on yt-dlp, missing official YouTube APIs, noisy transcript parsing) by offloading the processing to Google’s native ingestion infrastructure, then extracting the clean, structured RAG artifacts locally.

[YouTube URL List] 
       │
       ▼ (Via CLI / Claude Code Skill)
┌──────────────────────────────────────────────┐
│  notebooklm-py (Playwright Headless Session) │
└──────────────────────┬───────────────────────┘
                       │ (Automated Google Auth / API Hook)
                       ▼
┌──────────────────────────────────────────────┐
│       Google NotebookLM Internal RAG         │
│  - Extracts & cleans video audio transcripts │
│  - Bypasses raw text parsing pipelines       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼ (Artifact Extraction)
┌──────────────────────────────────────────────┐
│            Local Production Engine           │
│  - Structured JSON/Markdown Transcripts      │
│  - AI Podcasting Overviews (Deep-Dives)      │
│  - Claude Code Skill Context Injection       │
└──────────────────────────────────────────────┘
Core Capabilities
Zero-Overhead Transcript Scraping: Pulls cleaned, timestamped, and structured YouTube text directly from Google's parser—skipping local media downloads.

Agentic Extension (Claude Code Native): Installs as a direct skill path for Claude Code (notebooklm skill install), allowing natural language triggers like "Analyze the last 5 scraped URLs and draft a technical thread."

Exfiltration of Hidden Artifacts: Downloads underlying JSON mind maps, flashcards, and data tables that are blocked or purely interactive within the official web UI.

Installation & Environment Setup
1. System Dependencies
The core automation engine relies on Python 3.10+ and a headless Chromium instance to authenticate and keep cookie sessions alive.

Bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/claude-code-notebookllm-cheat-code.git
cd claude-code-notebookllm-cheat-code

# Install core package with browser dependencies
pip install notebooklm-py[browser]

# Provision the headless Chromium binary
playwright install chromium
2. Session Authentication
Before running headless automation pipelines, you must initialize an authenticated context block with your Google Account.

Bash
# Triggers interactive browser setup for a one-time login
notebooklm login
Security Note: Session states and token matrices are persisted locally inside your isolated NOTEBOOKLM_HOME directory. No credentials pass to third-party endpoints.

Technical Workflows & Deployment
Implementation 1: The Automated Content Ingestion Pipeline (CLI)
Execute bulk imports of YouTube data assets, generate standard deep-dive audio overviews, and pull clean text markdown to disk cleanly:

Bash
# 1. Initialize an isolated content creation workspace
notebooklm create "YouTube Content Ingestion Studio"

# 2. Scrape and inject a target YouTube stream directly via its URL
notebooklm source add "https://www.youtube.com/watch?v=usTeU4Uh0iM"

# 3. Exfiltrate the clean text transcript pulled from Google's RAG system
notebooklm source fulltext --id "TARGET_SOURCE_ID" > raw_transcript.md

# 4. Spin up a 2-person audio deep-dive overview (Podcast) asynchronously
notebooklm generate audio "Focus explicitly on technical execution steps" --format deep-dive --wait

# 5. Extract the generated media file into your local production directory
notebooklm download audio ./production_assets/podcast_brief.mp3
Implementation 2: Integration with Claude Code (Agentic Mode)
To allow Claude Code to dynamically search your internal notebooks, extract research context, and write content from scraped videos using natural language:

Bash
# Inject the NotebookLM skill architecture into Claude Code
notebooklm skill install
Once installed, your interactions inside Claude Code change to high-level system orchestration:

Plaintext
User  -> Claude, look into my "YouTube Content Ingestion Studio" notebook.
         Pull the fulltext transcript for the newly added video, extract the key structural formulas, 
         and format them into a highly technical README block for our repository.
Troubleshooting & Constraints
API Volatility: This setup relies on undocumented structural schemas of Google’s internal service endpoints. Updates to NotebookLM may degrade specific formatting operations. Keep notebooklm-py updated (pip install --upgrade notebooklm-py).

Authentication Expiration: Headless sessions will periodically require re-authentication. If your automation tasks start failing with an AuthException, clear your local state and re-execute notebooklm login.

Rate Mitigations: Heavy concurrent API threading may cause temporary Google infrastructure throttling. For extensive background tasks, use explicit queue delays within your execution loops.

Attribution & Upstream Sources
Core Automation Engine: teng-lin/notebooklm-py

Conceptual Walkthrough Inspiration: YouTube Video Walkthrough Reference
