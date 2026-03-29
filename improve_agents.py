import subprocess
import time

def run_claude_prompt(prompt, model="qwen3-coder"):
    """Run a clean, focused prompt with Claude Code via Ollama"""
    cmd = [
        "ollama", "launch", "claude", "--model", model, "--",
        prompt
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Prompt timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

print("🔧 Improving Agent Workflow for ISRO ASCEND...")

# Improved system prompt for better code generation
system_improvement = """
You are an expert drone engineer for ISRO ASCEND 2026.
Your ONLY job is to write clean, correct, minimal Python code for the flight controller.

Rules:
- Always use /dev/ttyACM0 at 115200 baud
- Always capture real takeoff position using LOCAL_POSITION_NED before takeoff
- Implement true 10Hz Strict Lock using set_position_target_local_ned_send with type_mask 0b0000111111000111
- Lock to the actual captured X,Y origin (not 0,0)
- Include emergency kill with 21196
- Keep the code simple and readable. No unnecessary classes or abstractions.
- Do not hallucinate sensor checks. Assume ghost_flight_tui is running.
- Output ONLY the complete Python script inside ```python ... ```
- Do not add extra explanation unless asked.
"""

print("✅ Agent improvement prompt ready.")
print("Next step: Use this improved prompt to generate the flight script.")
