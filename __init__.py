"""Compound Engineering plugin for Hermes Agent.

Installs the bundled skills into ~/.hermes/skills/ via symlinks so Hermes's
native skill scanner picks them up with proper /slash-command invocation
(lightning bolt icons, skill_view integration, context injection).

The upstream skills/ directory is kept untouched for clean merges.
At register() time, each skill is symlinked into
~/.hermes/skills/compound-engineering/ and the native scanner handles the rest.

Also registers /ce-agents and /ce-agent as plugin slash commands for
listing and loading agent personas.
"""

import re
import logging
import shutil
from pathlib import Path

from .transform_hermes import transform_content

logger = logging.getLogger(__name__)

_PLUGIN_DIR = Path(__file__).parent
_SKILLS_DIR = _PLUGIN_DIR / "skills"
_PLUGIN_NAME = "compound-engineering"
_TARGET_SKILLS_DIR = Path.home() / ".hermes" / "skills" / _PLUGIN_NAME


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content (minimal, no deps)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^(\w[\w-]*)\s*:\s*(.*)$", line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            if val and val[0] in "\"'" and val[-1] == val[0]:
                val = val[1:-1]
            fm[key] = val
    return fm


def _install_skills():
    """Symlink each skill directory into ~/.hermes/skills/compound-engineering/.

    This makes the native skill scanner pick them up, giving them
    lightning-bolt icons and proper /slash-command invocation.
    Uses symlinks so updates to the plugin directory are reflected
    automatically without re-copying.
    """
    if not _SKILLS_DIR.exists():
        logger.warning("Skills directory not found: %s", _SKILLS_DIR)
        return 0

    # Create target directory
    _TARGET_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for skill_dir in sorted(_SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        target = _TARGET_SKILLS_DIR / skill_dir.name

        # Remove existing symlink or dir, then create fresh symlink
        if target.is_symlink() or target.exists():
            if target.is_symlink() or target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            else:
                target.unlink()

        try:
            target.symlink_to(skill_dir, target_is_directory=True)
            count += 1
        except OSError:
            # Fallback: copy if symlinks don't work (e.g. Windows)
            shutil.copytree(skill_dir, target)
            count += 1

    logger.info("Installed %d skills to %s", count, _TARGET_SKILLS_DIR)
    return count


def _find_agent_files():
    """Find all agent .md files under skills/*/references/agents/."""
    agents = []
    if _SKILLS_DIR.exists():
        for agents_subdir in _SKILLS_DIR.rglob("agents"):
            if agents_subdir.is_dir():
                for md_file in sorted(agents_subdir.glob("*.md")):
                    agents.append(md_file)
    return agents


def _make_agent_handler():
    """Return a handler for /ce-agent <name> that loads an agent prompt."""

    def handler(raw_args: str, **kwargs) -> str:
        agent_name = raw_args.strip() if isinstance(raw_args, str) else ""
        if not agent_name:
            return "Usage: /ce-agent <agent-name>"

        agents = _find_agent_files()
        for candidate in [agent_name, f"ce-{agent_name}"]:
            for agent_path in agents:
                if agent_path.stem == candidate:
                    content = agent_path.read_text(encoding="utf-8")
                    return transform_content(content)

        return f"Agent '{agent_name}' not found. Run /ce-agents to list available agents."

    return handler


def _list_agents():
    """List all available agent personas."""

    def handler(raw_args: str, **kwargs) -> str:
        agents = _find_agent_files()
        if not agents:
            return "No agents found."

        lines = ["### Available Agents\n"]
        for agent_path in agents:
            name = agent_path.stem
            try:
                content = agent_path.read_text(encoding="utf-8")
                fm = _parse_frontmatter(content)
                desc = fm.get("description", "Specialized agent.")
            except Exception:
                desc = "Specialized agent."
            lines.append(f"- **{name}**: {desc}")
        lines.append("\nRun `/ce-agent <name>` to load an agent's prompt.")
        return "\n".join(lines)

    return handler


def register(ctx):
    """Install skills and register agent commands with Hermes."""

    # 1. Install skills as symlinks into ~/.hermes/skills/ so the native
    #    skill scanner picks them up with lightning-bolt slash commands.
    count = _install_skills()

    # 2. Register /ce-agents (list all available agent personas)
    ctx.register_command(
        name="ce-agents",
        handler=_list_agents(),
        description="List all available Compound Engineering agent personas.",
    )

    # 3. Register /ce-agent <name> (load a specific agent's prompt)
    ctx.register_command(
        name="ce-agent",
        handler=_make_agent_handler(),
        description="Load a specific agent's system prompt and instructions.",
    )

    logger.info("Compound Engineering plugin installed %d skills + 2 commands", count)