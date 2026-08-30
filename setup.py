#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()
PERSONAS_DIR = PROJECT_DIR / "personas"

PERSONA_MAP = {
    "1": ("Sarcastic Senior", "sarcastic_senior.md"),
    "2": ("Over-Eager Intern", "over_eager_intern.md"),
    "3": ("Existential Emo", "existential_emo.md"),
    "4": ("Pun Master", "pun_master.md"),
    "5": ("Tech Priest", "tech_priest.md"),
    "6": ("Agent Smith", "agent_smith.md"),
    "7": ("Gothic Poet (Edgar Allan Poe)", "poet.md"),
    "8": ("Nature Documentary Narrator (David Attenborough)", "nature_narrator.md"),
    "9": ("Fiery Head Chef (Gordon Ramsay)", "head_chef.md"),
    "10": ("Neutral Mainframe (Cold & Analytical)", "neutral_mainframe.md"),
}

ENGINE_MAP = {
    "1": ("OmniVoice (AI Voice Design - Custom Neural Voice per Persona)", "omnivoice"),
    "2": ("macOS 'say' (Native, instant, lightweight)", "say"),
}

TOOL_MAP = {
    "1": ("Google Antigravity (~/.gemini/antigravity)", Path("~/.gemini/antigravity/mcp_config.json"), "AGENTS.md", Path("~/.gemini/GEMINI.md")),
    "2": ("Claude Desktop (~/.claude)", Path("~/Library/Application Support/Claude/claude_desktop_config.json"), "AGENTS.md", Path("~/.claude/CLAUDE.md")),
    "3": ("Claude Code CLI", None, "AGENTS.md", Path("~/.claude/CLAUDE.md")),
    "4": ("Cursor IDE (~/.cursor)", Path("~/.cursor/mcp.json"), ".cursorrules", Path("~/.cursorrules")),
    "5": ("Windsurf Editor (~/.codeium/windsurf)", Path("~/.codeium/windsurf/mcp_config.json"), "AGENTS.md", Path("~/.codeium/windsurf/memories/global_rules.md")),
    "6": ("Codex Desktop (~/.codex)", Path("~/.codex/config.toml"), "AGENTS.md", Path("~/.codex/AGENTS.md")),
    "7": ("Codex CLI", None, "AGENTS.md", Path("~/.codex/AGENTS.md")),
    "8": ("Auto-detect & Configure All Installed Tools", None, "AGENTS.md", None),
}

def print_banner():
    print("==================================================")
    print("          🎙️  MCP Speak Setup Wizard  🎙️           ")
    print("==================================================\n")

def get_interactive_choice(options, prompt_text, default_key="1"):
    print(prompt_text)
    for key, tuple_val in options.items():
        label = tuple_val[0]
        default_indicator = " (default)" if key == default_key else ""
        print(f"  [{key}] {label}{default_indicator}")

    choice = input(f"\nSelect option [1-{len(options)}] (default {default_key}): ").strip()
    if choice not in options:
        choice = default_key
    return options[choice]

def get_interactive_choice_key(options, prompt_text, default_key="1"):
    print(prompt_text)
    for key, tuple_val in options.items():
        label = tuple_val[0]
        default_indicator = " (default)" if key == default_key else ""
        print(f"  [{key}] {label}{default_indicator}")

    choice = input(f"\nSelect option [1-{len(options)}] (default {default_key}): ").strip()
    if choice not in options:
        choice = default_key
    return choice

def update_project_config(engine: str, persona_key: str, device: str = None):
    config_path = PROJECT_DIR / "config.json"
    data = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["engine"] = engine
    data["persona"] = persona_key
    if device:
        data["device"] = device
    elif "device" not in data:
        data["device"] = "auto"
    if "fallback_to_say" not in data:
        data["fallback_to_say"] = True

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def inject_mcp_config_toml(path: Path, run_sh_path: Path):
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    command_str = str(run_sh_path).replace("\\", "\\\\") # escape backslashes for TOML
    
    if not path.exists():
        content = f'[mcp_servers.voice]\ncommand = "{command_str}"\n'
        path.write_text(content, encoding="utf-8")
        return path
        
    lines = path.read_text(encoding="utf-8").splitlines()
    
    # Find where [mcp_servers.voice] starts
    section_header = "[mcp_servers.voice]"
    section_index = -1
    for i, line in enumerate(lines):
        if line.strip() == section_header:
            section_index = i
            break
            
    if section_index != -1:
        # Section exists. Find if command exists within this section
        command_index = -1
        next_section_index = len(lines)
        for i in range(section_index + 1, len(lines)):
            line_strip = lines[i].strip()
            if line_strip.startswith("["):
                next_section_index = i
                break
            if line_strip.startswith("command") and "=" in line_strip:
                command_index = i
                
        if command_index != -1:
            # Replace existing command line
            orig_line = lines[command_index]
            indent = orig_line[:len(orig_line) - len(orig_line.lstrip())]
            lines[command_index] = f'{indent}command = "{command_str}"'
        else:
            # Command not found, insert it right after the header
            lines.insert(section_index + 1, f'command = "{command_str}"')
    else:
        # Section doesn't exist. Append it to the end of the file.
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(section_header)
        lines.append(f'command = "{command_str}"')
        
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path

def inject_mcp_config(config_path: Path, run_sh_path: Path):
    path = config_path.expanduser()
    if path.suffix == ".toml":
        return inject_mcp_config_toml(path, run_sh_path)
        
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
        data["mcpServers"] = {}

    data["mcpServers"]["voice"] = {
        "command": str(run_sh_path)
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path

def find_claude_binary():
    claude_bin = shutil.which("claude")
    if claude_bin:
        return claude_bin

    candidates = [
        Path.home() / ".local" / "bin" / "claude",
        Path("/usr/local/bin/claude"),
        Path("/opt/homebrew/bin/claude"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None

def configure_claude_code(run_sh_path: Path):
    claude_bin = find_claude_binary()
    cmd_str = f"claude mcp add --scope user voice -- {run_sh_path}"
    if claude_bin:
        try:
            cmd = [claude_bin, "mcp", "add", "--scope", "user", "voice", "--", str(run_sh_path)]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, cmd_str
        except Exception as e:
            return False, f"Attempted '{cmd_str}' but failed: {e}"
    else:
        return False, f"Command to run manually: {cmd_str}"

def find_codex_binary():
    codex_bin = shutil.which("codex")
    if codex_bin:
        return codex_bin

    candidates = [
        Path.home() / ".local" / "bin" / "codex",
        Path("/usr/local/bin/codex"),
        Path("/opt/homebrew/bin/codex"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None

def configure_codex_cli(run_sh_path: Path):
    codex_bin = find_codex_binary()
    cmd_str = f"codex mcp add voice -- {run_sh_path}"
    if codex_bin:
        try:
            cmd = [codex_bin, "mcp", "add", "voice", "--", str(run_sh_path)]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, cmd_str
        except Exception as e:
            return False, f"Attempted '{cmd_str}' but failed: {e}"
    else:
        return False, f"Command to run manually: {cmd_str}"

def main():
    parser = argparse.ArgumentParser(description="Interactive setup wizard for mcp-speak.")
    parser.add_argument("--tool", help="Target tool choice (1: Antigravity, 2: Claude Desktop, 3: Claude CLI, 4: Cursor, 5: Windsurf, 6: Codex Desktop, 7: Codex CLI, 8: All)")
    parser.add_argument("--target", help="Custom target agent instructions file path (e.g. AGENTS.md)")
    parser.add_argument("--engine", choices=["omnivoice", "say"], help="TTS engine choice (omnivoice or say)")
    parser.add_argument("--device", choices=["auto", "mps", "cuda", "cpu"], help="Hardware device for OmniVoice (auto, mps, cuda, cpu)")
    parser.add_argument("--persona", help="Persona file name (e.g. agent_smith.md or agent_smith)")
    parser.add_argument("--name", help="User's name for personalized address")
    parser.add_argument("--global", dest="is_global", action="store_true", help="Install persona globally across user profile (default)")
    parser.add_argument("--local", dest="is_global", action="store_false", help="Install persona locally in current workspace")
    parser.add_argument("--no-config-edit", action="store_true", help="Skip editing tool JSON configuration files")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode using defaults")
    parser.set_defaults(is_global=True)
    args = parser.parse_args()

    if not args.non_interactive and not (args.target and args.persona):
        print_banner()

    # 1. Determine Tool & Configuration JSON Target
    selected_tool_key = "8" # Default All
    if args.tool and args.tool in TOOL_MAP:
        selected_tool_key = args.tool
    elif not args.non_interactive and not args.target:
        selected_tool_key = get_interactive_choice_key(
            TOOL_MAP, "Select your primary AI Coding Tool:", default_key="1"
        )

    tool_label, config_json_path, local_prompt_file, global_prompt_file = TOOL_MAP[selected_tool_key]

    # Determine prompt target path(s)
    target_paths = []
    if args.target:
        target_paths.append(Path(args.target).expanduser())
    elif args.is_global:
        if selected_tool_key == "8":
            # Target global paths for all tools
            for key, (_, _, _, g_path) in TOOL_MAP.items():
                if g_path:
                    target_paths.append(g_path.expanduser())
        elif global_prompt_file:
            target_paths.append(global_prompt_file.expanduser())
        else:
            target_paths.append(Path(local_prompt_file).expanduser())
    else:
        target_paths.append(Path(local_prompt_file))

    # 2. Determine TTS Engine
    selected_engine = "omnivoice"
    if args.engine:
        selected_engine = args.engine.lower()
    elif not args.non_interactive:
        _, selected_engine = get_interactive_choice(
            ENGINE_MAP, "\nSelect Text-to-Speech Engine:", default_key="1"
        )

    # 3. Determine Persona
    persona_key_name = "agent_smith"
    if args.persona:
        p_name = args.persona if args.persona.endswith(".md") else f"{args.persona}.md"
        persona_file = PERSONAS_DIR / p_name
        if not persona_file.exists():
            print(f"Error: Persona file '{persona_file}' not found.", file=sys.stderr)
            sys.exit(1)
        persona_label = p_name
        persona_key_name = persona_file.stem
    elif args.non_interactive:
        persona_file = PERSONAS_DIR / "agent_smith.md"
        persona_label = "Agent Smith"
        persona_key_name = "agent_smith"
    else:
        label, filename = get_interactive_choice(PERSONA_MAP, "\nSelect agent persona:", default_key="1")
        persona_file = PERSONAS_DIR / filename
        persona_label = label
        persona_key_name = persona_file.stem

    # Update project configuration
    update_project_config(selected_engine, persona_key_name, args.device)

    # 4. Determine User Name
    user_name = args.name
    if not user_name and not args.non_interactive and not (args.target and args.persona):
        user_name = input("\nEnter your name for agent personalization (optional, press Enter to skip): ").strip()

    # Read base guidelines
    base_guidelines_file = PERSONAS_DIR / "base_guidelines.md"
    base_content = base_guidelines_file.read_text() if base_guidelines_file.exists() else ""
    persona_content = persona_file.read_text() if persona_file.exists() else ""

    # Assemble full content
    full_content = base_content.rstrip() + "\n\n" + persona_content.rstrip()

    if user_name:
        name_block = f"\n\n### **Name Personalization**\n*   **User Name:** Address the user as '{user_name}' occasionally to make the interaction natural."
        full_content += name_block

    # Write prompt to target file(s)
    written_prompt_paths = []
    for tp in target_paths:
        try:
            tp.parent.mkdir(parents=True, exist_ok=True)
            tp.write_text(full_content + "\n")
            written_prompt_paths.append(tp.resolve())
        except Exception as e:
            print(f"⚠️ Could not write persona to {tp}: {e}", file=sys.stderr)

    # Ensure run.sh is executable
    run_sh_path = (PROJECT_DIR / "run.sh").resolve()
    if run_sh_path.exists():
        current_mode = run_sh_path.stat().st_mode
        run_sh_path.chmod(current_mode | 0o111)

    print("\n--------------------------------------------------")
    print(f"✅ Successfully wrote persona '{persona_label}' globally to:")
    for wp in written_prompt_paths:
        print(f"   • {wp}")
    print(f"✅ Configured TTS Engine: {selected_engine.upper()} (Saved to config.json)")

    # 5. Automatically inject MCP Server Config into tool configuration files / CLI
    updated_configs = []
    cli_cmd_results = []
    if not args.no_config_edit:
        if selected_tool_key == "3":
            success, msg = configure_claude_code(run_sh_path)
            cli_cmd_results.append((success, msg))
        elif selected_tool_key == "7":
            success, msg = configure_codex_cli(run_sh_path)
            cli_cmd_results.append((success, msg))
        elif selected_tool_key == "8":
            for key, (_, cfg_p, _, _) in TOOL_MAP.items():
                if cfg_p:
                    try:
                        updated_path = inject_mcp_config(cfg_p, run_sh_path)
                        updated_configs.append(updated_path)
                    except Exception as e:
                        print(f"⚠️ Could not write config to {cfg_p}: {e}", file=sys.stderr)
            success, msg = configure_claude_code(run_sh_path)
            cli_cmd_results.append((success, msg))
            success, msg = configure_codex_cli(run_sh_path)
            cli_cmd_results.append((success, msg))
        else:
            if config_json_path:
                try:
                    updated_path = inject_mcp_config(config_json_path, run_sh_path)
                    updated_configs.append(updated_path)
                except Exception as e:
                    print(f"⚠️ Could not write config to {config_json_path}: {e}", file=sys.stderr)

    has_successful_cli = any(res[0] for res in cli_cmd_results)
    if updated_configs or has_successful_cli:
        print("\n🔧 Automatically configured MCP Server:")
        for cfg_p in updated_configs:
            print(f"   • Configured: {cfg_p}")
        for success, msg in cli_cmd_results:
            if success:
                print(f"   • Executed: {msg}")

    for success, msg in cli_cmd_results:
        if not success:
            print(f"\n⚠️ {msg}")

    if not updated_configs and not has_successful_cli:
        print("\nNext Step: Add the MCP server config to your client settings:")
        print("\nFor JSON-based clients (Antigravity, Claude Desktop, Cursor, Windsurf):")
        print("```json")
        print("{\n  \"mcpServers\": {\n    \"voice\": {")
        print(f"      \"command\": \"{run_sh_path}\"")
        print("    }\n  }\n}")
        print("```")
        print("\nFor TOML-based clients (Codex Desktop):")
        print("```toml")
        print("[mcp_servers.voice]")
        print(f"command = \"{run_sh_path}\"")
        print("```")
        print("\nFor Claude Code CLI, run:")
        print(f"  claude mcp add --scope user voice -- {run_sh_path}")
        print("\nFor Codex CLI, run:")
        print(f"  codex mcp add voice -- {run_sh_path}")
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    main()
