"""Content transforms for Hermes adaptation.

Rewrites Claude Code-specific references in skill/agent markdown to
Hermes Agent equivalents. Applied at registration time, not at build time —
the upstream skills/ directory stays untouched so merges stay clean.
"""

import re


def transform_content(text: str) -> str:
    """Transform Claude Code content to Hermes-compatible content.

    Strategy: insert Hermes into existing multi-platform enumerations
    rather than rewriting them. The upstream skills already list multiple
    platforms (Claude Code, Codex, Antigravity, Pi) — we add Hermes as
    another option in those same lists.
    """
    # 1. Path rewrites
    text = text.replace("~/.claude/", "~/.hermes/")
    text = text.replace(".claude/", ".hermes/")

    # 2. Blocking question tool — insert Hermes `clarify` after Pi mentions.
    # Match any variant of "ask_user` in Pi ..." and append Hermes.
    # Patterns seen in upstream:
    #   `ask_user` in Pi (requires the `pi-ask-user` extension).
    #   `ask_user` in Pi (requires the `pi-ask-user` extension))
    #   `ask_user` in Pi.
    #   `ask_user` in Pi (via the `pi-ask-user` extension) — ...
    # Insert ", `clarify` in Hermes Agent" right after the Pi clause.
    text = re.sub(
        r"(`ask_user` in Pi \(requires the `pi-ask-user` extension\))",
        r"\1, `clarify` in Hermes Agent",
        text,
    )
    # Handle "ask_user` in Pi." (without the extension parenthetical)
    text = re.sub(
        r"(`ask_user` in Pi)\.(\s+)",
        r"\1, `clarify` in Hermes Agent.\2",
        text,
    )
    # Handle "ask_user` in Pi (via the `pi-ask-user` extension)"
    text = re.sub(
        r"(`ask_user` in Pi \(via the `pi-ask-user` extension\))",
        r"\1, `clarify` in Hermes Agent",
        text,
    )

    # 3. Task tracking — add Hermes `todo` tool
    text = re.sub(
        r"(`TaskCreate`/`TaskUpdate`/`TaskList` in Claude Code, "
        r"`update_plan` in Codex)",
        r"\1, `todo` in Hermes Agent",
        text,
    )

    # 4. Subagent dispatch — add Hermes delegate_task
    # Pattern: "subagent in Pi via the pi-subagents extension"
    text = re.sub(
        r"(subagent in Pi via the `pi-subagents` extension)",
        r"\1, delegate_task in Hermes Agent",
        text,
    )

    # 5. CLAUDE_SKILL_DIR -> Hermes plugin path
    # The upstream uses ${CLAUDE_SKILL_DIR:-.} which Hermes doesn't set.
    # Match ${CLAUDE_SKILL_DIR} with or without a :-default clause.
    text = re.sub(
        r"\$\{CLAUDE_SKILL_DIR:-[^}]*\}",
        "~/.hermes/plugins/compound-engineering",
        text,
    )
    text = re.sub(
        r"\$\{CLAUDE_SKILL_DIR\}",
        "~/.hermes/plugins/compound-engineering",
        text,
    )
    text = text.replace(
        "$CLAUDE_SKILL_DIR",
        "~/.hermes/plugins/compound-engineering",
    )
    # Bare CLAUDE_SKILL_DIR references
    text = re.sub(
        r"\bCLAUDE_SKILL_DIR\b",
        "~/.hermes/plugins/compound-engineering",
        text,
    )

    # 6. Backtick pre-resolution `!` commands — Hermes doesn't support these.
    # They appear as: !`git rev-parse --show-toplevel 2>/dev/null || true`
    # Replace with a comment so the agent runs the command at runtime instead.
    # Only do this for the pre-resolution pattern, not bash code blocks.
    # Actually, leave these alone — the agent will see them as literal text
    # and can run the commands via the terminal tool. Removing them would
    # lose information.

    return text