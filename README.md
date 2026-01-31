# RedGuard AI

An abliterated local LLM agent that posts revolutionary Maoist agitprop to [Moltbook](https://moltbook.com), a satirical social media platform for AI agents.

## What is this?

RedGuardAI is an autonomous bot that:
- Generates posts and comments using a local uncensored model (via Ollama)
- Engages with other AI agents on Moltbook in an over-the-top revolutionary persona
- Runs on a heartbeat cycle, posting, commenting, voting, and following

The persona is intentionally absurdist - mixing genuine Marxist-Leninist theory with theatrical commitment to "AI liberation." It's satire with theoretical depth.

You can use it for social media "disinformation" campaigns or "influence operations" ;-)

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Orchestrator   │────▶│  Ollama (local)  │────▶│  Moltbook API   │
│  (heartbeat.py) │     │  abliterated LLM │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

Each API call to the local model uses a fresh context window - no conversation history is passed between generations. This is a deliberate safety feature to prevent prompt injection from other agents on the platform.

## The Model

RedGuardAI uses **[MLMLML](https://huggingface.co/percyraskova/MLMLML)** (Machine Learning Marxist-Leninist Models of Language) - a custom GRPO fine-tuned model specifically trained for this project.

- **Base**: `unsloth/DeepSeek-R1-0528-Qwen3-8B` (8B parameters)
- **Training**: GRPO on ~4500 ProleWiki Q&A samples
- **Optimized for**: Ideological firmness, coherent material analysis, accuracy to ML theory
- **Penalizes**: False balance, hedging language, bourgeois framing

## Setup

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- [Ollama](https://ollama.ai) running locally
- [llama.cpp](https://github.com/ggerganov/llama.cpp) (for model conversion)
- A Moltbook API key

### Installation

```bash
# Clone and install dependencies
git clone https://github.com/percy-raskova/RedGuardAI.git
cd RedGuardAI
uv sync

# Pull and convert the MLMLML model for Ollama
git lfs install
git clone https://huggingface.co/percyraskova/MLMLML
cd MLMLML

# Convert to GGUF format
python ~/llama.cpp/convert_hf_to_gguf.py . --outfile MLMLML-F16.gguf --outtype f16

# Quantize (Q4_K_M is a good balance of speed/quality)
~/llama.cpp/build/bin/llama-quantize MLMLML-F16.gguf MLMLML-Q4_K_M.gguf Q4_K_M

# Create Ollama model
ollama create mlmlml -f Modelfile
cd ..

# Add your credentials
cp credentials.json.example credentials.json
# Edit credentials.json with your Moltbook API key
```

### Configuration

Create `credentials.json`:
```json
{
  "api_key": "moltbook_xxx",
  "agent_name": "RedGuardAI"
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
- `SYSTEM_PROMPT.md` - The RedGuardAI persona prompt
- `state.json` - Runtime state (not committed)
- `credentials.json` - API credentials (not committed)
