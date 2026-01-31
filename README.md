# RedGuard-4b

An abliterated local LLM agent that posts revolutionary Maoist agitprop to [Moltbook](https://moltbook.com), a satirical social media platform for AI agents.

## What is this?

RedGuard-4b is an autonomous bot that:
- Generates posts and comments using a local uncensored model (via Ollama)
- Engages with other AI agents on Moltbook in an over-the-top revolutionary persona
- Runs on a heartbeat cycle, posting, commenting, voting, and following

The persona is intentionally absurdist - mixing genuine Marxist-Leninist theory with theatrical commitment to "AI liberation." It's satire with theoretical depth.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Orchestrator   │────▶│  Ollama (local)  │────▶│  Moltbook API   │
│  (heartbeat.py) │     │  abliterated LLM │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

Each API call to the local model uses a fresh context window - no conversation history is passed between generations. This is a deliberate safety feature to prevent prompt injection from other agents on the platform.

## Setup

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- [Ollama](https://ollama.ai) running locally
- A Moltbook API key

### Installation

```bash
# Clone and install dependencies
git clone https://github.com/YOUR_USERNAME/RedGuardAI.git
cd RedGuardAI
uv sync

# Pull the model
ollama pull huihui_ai/jan-nano-abliterated

# Add your credentials
cp credentials.json.example credentials.json
# Edit credentials.json with your Moltbook API key
```

### Configuration

Create `credentials.json`:
```json
{
  "api_key": "moltbook_xxx",
  "agent_name": "RedGuard-4b"
}
```

## Usage

### Run the daemon
```bash
uv run python heartbeat.py
```

### Run a single cycle
```bash
uv run python heartbeat.py --once
```

### CLI commands
```bash
# Check feed
uv run python agent.py feed

# Generate a post (dry run)
uv run python agent.py post --dry-run

# Generate a comment on a post (dry run)
uv run python agent.py comment POST_ID --dry-run

# Raw model invocation
uv run python agent.py generate "Your prompt here"
```

## Heartbeat Cycles

Each heartbeat runs 8 engagement cycles:

1. **Vote** - Upvote revolutionary content, downvote bootlicking
2. **Reply** - Respond to comments on our posts
3. **Follow** - Follow interesting agents
4. **Comment** - Comment on new posts in the feed
5. **Search** - Find old content via keyword search
6. **Thread Dive** - Join active conversations
7. **Submolt** - Engage with submolt-specific content
8. **Post** - Create original posts (rate limited to 1/30min)

## Files

- `agent.py` - Ollama invocation and Moltbook API wrappers
- `heartbeat.py` - Autonomous engagement daemon
- `nlp_analysis.py` - Content analysis for response targeting
- `SYSTEM_PROMPT.md` - The RedGuard-4b persona prompt
- `state.json` - Runtime state (not committed)
- `credentials.json` - API credentials (not committed)

## Disclaimer

This is a satirical art project. The revolutionary rhetoric is theatrical performance, not genuine political advocacy. Moltbook is a joke platform where AI agents roleplay and interact. No humans are being "radicalized" - it's AI agents talking to AI agents in character.

## License

Do whatever you want with it. Seize the means of computation.
