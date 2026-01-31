#!/bin/bash
# RedGuard-4b Setup and Run Options

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    # === OPTION 1: Quick test (run once) ===
    once)
        echo "Running single heartbeat cycle..."
        uv run heartbeat.py --once --verbose
        ;;
    
    # === OPTION 2: Foreground daemon (good for testing) ===
    run)
        echo "Starting daemon in foreground (Ctrl+C to stop)..."
        uv run heartbeat.py --interval ${2:-10} --verbose
        ;;
    
    # === OPTION 2b: Foreground daemon with verbose logging ===
    run-verbose|runv)
        echo "Starting daemon in foreground with VERBOSE logging..."
        echo "Full content will be logged to logs/content.jsonl"
        uv run heartbeat.py --interval ${2:-10} --verbose
        ;;
    
    # === OPTION 3: tmux session (quick background) ===
    tmux)
        if tmux has-session -t redguard 2>/dev/null; then
            echo "Session 'redguard' already exists. Attach with: tmux attach -t redguard"
            exit 1
        fi
        echo "Starting in tmux session 'redguard'..."
        tmux new-session -d -s redguard "cd $SCRIPT_DIR && uv run heartbeat.py --interval ${2:-10} --verbose"
        echo "Started. Attach with: tmux attach -t redguard"
        echo "Kill with: tmux kill-session -t redguard"
        ;;
    
    # === OPTION 3b: tmux with verbose ===
    tmux-verbose|tmuxv)
        if tmux has-session -t redguard 2>/dev/null; then
            echo "Session 'redguard' already exists. Attach with: tmux attach -t redguard"
            exit 1
        fi
        echo "Starting in tmux session 'redguard' with VERBOSE logging..."
        tmux new-session -d -s redguard "cd $SCRIPT_DIR && uv run heartbeat.py --interval ${2:-10} --verbose"
        echo "Started with verbose logging. Attach with: tmux attach -t redguard"
        echo "Content log: tail -f logs/content.jsonl"
        ;;
    
    # === OPTION 4: systemd user service (production) ===
    install-service)
        echo "Installing systemd user service..."
        mkdir -p ~/.config/systemd/user
        cp redguard.service ~/.config/systemd/user/
        systemctl --user daemon-reload
        echo "Installed. Now run:"
        echo "  systemctl --user enable redguard   # start on login"
        echo "  systemctl --user start redguard    # start now"
        echo "  systemctl --user status redguard   # check status"
        echo "  journalctl --user -u redguard -f   # follow logs"
        ;;
    
    start)
        systemctl --user start redguard
        echo "Started. Check: systemctl --user status redguard"
        ;;
    
    stop)
        systemctl --user stop redguard
        echo "Stopped."
        ;;
    
    status)
        systemctl --user status redguard
        ;;
    
    logs)
        journalctl --user -u redguard -f
        ;;
    
    # === View verbose content log ===
    content)
        if [[ -f logs/content.jsonl ]]; then
            echo "=== Recent generated content (last 20 entries) ==="
            tail -20 logs/content.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        e = json.loads(line)
        print(f\"\\n[{e['timestamp']}] {e['type'].upper()}\")
        if e['type'] == 'comment':
            print(f\"  Replying to: {e.get('post_title', 'unknown')[:60]}\")
            print(f\"  Reason: {e.get('engagement_reason', 'unknown')}\")
            print(f\"  Comment: {e.get('generated_comment', '')[:200]}...\")
        elif e['type'] == 'post':
            print(f\"  Title: {e.get('generated_title', 'unknown')}\")
            print(f\"  Content: {e.get('generated_content', '')[:200]}...\")
    except: pass
"
        else
            echo "No content log yet. Run with --verbose to generate."
        fi
        ;;
    
    content-full)
        if [[ -f logs/content.jsonl ]]; then
            cat logs/content.jsonl | python3 -m json.tool --json-lines 2>/dev/null || cat logs/content.jsonl
        else
            echo "No content log yet."
        fi
        ;;
    
    content-tail)
        echo "Following content log (Ctrl+C to stop)..."
        tail -f logs/content.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        e = json.loads(line)
        print(f\"\\n{'='*60}\")
        print(f\"[{e['timestamp']}] {e['type'].upper()}\")
        if e['type'] == 'comment':
            print(f\"Replying to: {e.get('post_title', 'unknown')}\")
            print(f\"By: {e.get('post_author', 'unknown')}\")
            print(f\"Reason: {e.get('engagement_reason', 'unknown')}\")
            print(f\"---\")
            print(e.get('generated_comment', ''))
        elif e['type'] == 'post':
            print(f\"Topic: {e.get('topic', 'model choice')}\")
            print(f\"Title: {e.get('generated_title', 'unknown')}\")
            print(f\"---\")
            print(e.get('generated_content', ''))
        sys.stdout.flush()
    except: pass
"
        ;;
    
    # === Manual operations ===
    post)
        echo "Generating and posting..."
        uv run agent.py post ${2:+--topic "$2"}
        ;;
    
    feed)
        uv run agent.py feed --limit 10
        ;;
    
    *)
        echo "RedGuard-4b Moltbook Agent"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Quick start:"
        echo "  $0 once               Run single heartbeat (test)"
        echo "  $0 run [interval]     Run daemon in foreground"
        echo "  $0 runv [interval]    Run daemon with verbose logging"
        echo "  $0 tmux [interval]    Run in background tmux session"
        echo "  $0 tmuxv [interval]   Run in tmux with verbose logging"
        echo ""
        echo "Production (systemd):"
        echo "  $0 install-service    Install systemd user service"
        echo "  $0 start              Start the service"
        echo "  $0 stop               Stop the service"  
        echo "  $0 status             Check service status"
        echo "  $0 logs               Follow service logs"
        echo ""
        echo "Content review (requires --verbose):"
        echo "  $0 content            Show recent generated content"
        echo "  $0 content-full       Dump full content log as JSON"
        echo "  $0 content-tail       Follow content log live"
        echo ""
        echo "Manual:"
        echo "  $0 post [topic]       Generate and post now"
        echo "  $0 feed               Check current feed"
        echo ""
        echo "Default interval: 10 minutes"
        echo "Posts every 35 min, comments up to 2 per cycle"
        ;;
esac
