#!/usr/bin/env python3
import os
import sys
import json
import argparse
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
}

TOOL_MAP = {
    "1": ("Google Antigravity (~/.gemini/antigravity/mcp_config.json)", Path("~/.gemini/antigravity/mcp_config.json"), "AGENTS.md"),
    "2": ("Claude Desktop (~/Library/Application Support/Claude/claude_desktop_config.json)", Path("~/Library/Application Support/Claude/claude_desktop_config.json"), "AGENTS.md"),
    "3": ("Claude Code CLI (~/.claude/config.json)", Path("~/.claude/config.json"), "AGENTS.md"),
    "4": ("Cursor IDE (~/.cursor/mcp.json)", Path("~/.cursor/mcp.json"), ".cursorrules"),
    "5": ("Windsurf Editor (~/.codeium/windsurf/mcp_config.json)", Path("~/.codeium/windsurf/mcp_config.json"), "AGENTS.md"),
    "6": ("Auto-detect & Configure All Installed Tools", None, "AGENTS.md"),
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
    if not choice:
        choice = default_key
    return options.get(choice, options[default_key])

def inject_mcp_config(config_path: Path, run_sh_path: Path):
    path = config_path.expanduser()
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

def main():
    parser = argparse.ArgumentParser(description="Interactive setup wizard for mcp-speak.")
    parser.add_argument("--tool", help="Target tool choice (1: Antigravity, 2: Claude Desktop, 3: Claude CLI, 4: Cursor, 5: Windsurf, 6: All)")
    parser.add_argument("--target", help="Custom target agent instructions file path (e.g. AGENTS.md)")
    parser.add_argument("--persona", help="Persona file name (e.g. agent_smith.md or agent_smith)")
    parser.add_argument("--name", help="User's name for personalized address")
    parser.add_argument("--no-config-edit", action="store_true", help="Skip editing tool JSON configuration files")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode using defaults")
    args = parser.parse_args()

    if not args.non_interactive and not (args.target and args.persona):
        print_banner()

    # 1. Determine Tool & Configuration JSON Target
    tool_label, config_json_path, default_prompt_file = TOOL_MAP["6"] # Default All
    if args.tool and args.tool in TOOL_MAP:
        tool_label, config_json_path, default_prompt_file = TOOL_MAP[args.tool]
    elif not args.non_interactive and not args.target:
        tool_label, config_json_path, default_prompt_file = get_interactive_choice(
            TOOL_MAP, "Select your primary AI Coding Tool:", default_key="1"
        )

    # Determine prompt target path
    if args.target:
        target_path = Path(args.target)
    else:
        target_path = Path(default_prompt_file)

    # 2. Determine Persona
    if args.persona:
        p_name = args.persona if args.persona.endswith(".md") else f"{args.persona}.md"
        persona_file = PERSONAS_DIR / p_name
        if not persona_file.exists():
            print(f"Error: Persona file '{persona_file}' not found.", file=sys.stderr)
            sys.exit(1)
        persona_label = p_name
    elif args.non_interactive:
        persona_file = PERSONAS_DIR / "agent_smith.md"
        persona_label = "Agent Smith"
    else:
        label, filename = get_interactive_choice(PERSONA_MAP, "\nSelect agent persona:", default_key="6")
        persona_file = PERSONAS_DIR / filename
        persona_label = label

    # 3. Determine User Name
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

    # Write prompt to target file
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(full_content + "\n")

    # Ensure run.sh is executable
    run_sh_path = (PROJECT_DIR / "run.sh").resolve()
    if run_sh_path.exists():
        current_mode = run_sh_path.stat().st_mode
        run_sh_path.chmod(current_mode | 0o111)

    print("\n--------------------------------------------------")
    print(f"✅ Successfully wrote persona '{persona_label}' to {target_path.resolve()}")

    # 4. Automatically inject MCP Server Config into tool JSON files
    updated_configs = []
    if not args.no_config_edit:
        target_configs = []
        if config_json_path:
            target_configs.append(config_json_path)
        else:
            # Auto-detect / configure all known tools
            for key, (_, cfg_p, _) in TOOL_MAP.items():
                if cfg_p:
                    target_configs.append(cfg_p)

        for cfg in target_configs:
            try:
                updated_path = inject_mcp_config(cfg, run_sh_path)
                updated_configs.append(updated_path)
            except Exception as e:
                print(f"⚠️ Could not write config to {cfg}: {e}", file=sys.stderr)

    if updated_configs:
        print("\n🔧 Automatically configured MCP Server in:")
        for cfg_p in updated_configs:
            print(f"   • {cfg_p}")
    else:
        print("\nNext Step: Add the following MCP server config to your client settings:")
        print("\n```json")
        print("{\n  \"mcpServers\": {\n    \"voice\": {")
        print(f"      \"command\": \"{run_sh_path}\"")
        print("    }\n  }\n}")
        print("```")
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    main()
