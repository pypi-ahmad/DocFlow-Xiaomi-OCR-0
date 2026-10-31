# How to install skills in Grok Build

> This is an earlier skill-installation record. Current project setup and commands are in the [developer guide](developer-guide.md).

Researched on 2026-10-28 from the local Grok Build user guide at `C:\Users\ahmad\.grok\docs\user-guide\`. No skills were installed and no config was changed.

There is no `grok skill install` command in that guide. A skill is a directory that contains a `SKILL.md` file. Grok loads it when the directory sits on a discovery path, comes from an installed plugin, or is created with `/create-skill`. [Skills](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

## Put a skill folder where Grok already looks

Copy or create `<skill-name>/SKILL.md` in one of these places. Higher rows win when two skills share a name. [Skills: Skill Locations](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

| Location | Scope |
| --- | --- |
| `./.grok/skills/` and `./.agents/skills/` | Current directory. Highest priority. |
| `<repo_root>/.grok/skills/` and `<repo_root>/.agents/skills/` | Repository. |
| `~/.grok/skills/` and `~/.agents/skills/` | This user, every project. On this machine, `~` is `C:\Users\ahmad`. |
| `~/.claude/skills/` and `./.claude/skills/` | Claude compatibility. Scanned by default. |
| `~/.cursor/skills/` and `./.cursor/skills/` | Cursor compatibility. Scanned by default. |

Grok also reads legacy command markdown under each tier's `commands/` directory, walks every directory between the working directory and the repo root, and does not consult `.gitignore` for these roots. Hide a skill with `[skills] ignore` in `~/.grok/config.toml`, not with a repo ignore rule. [Skills: Skill Locations](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

A personal skill for every project:

```text
C:\Users\ahmad\.grok\skills\commit\SKILL.md
```

`SKILL.md` needs YAML frontmatter, then the instructions. `name` is lowercase letters, digits, and hyphens, up to 64 characters. If `name` is omitted, Grok uses the directory name. `description` is what Grok matches to decide automatic use. [Skills: SKILL.md Format](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

```markdown
---
name: commit
description: Create well-formatted git commits following conventional commit standards. Use when the user wants to commit changes or asks for /commit.
---

# Git Commit Skill

1. Run `git diff --staged` to see changes
2. Summarize what changed and why
3. Create a conventional commit message
4. Run `git commit -m "..."` with the message
```

Files changed on disk show up in the slash menu within a few seconds. Run the skill as `/commit`, or `/commit fix the build` to pass arguments. [Skills: Creating a Skill](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md), [Skills: Using Skills](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

Startup discovery skips project skills in a folder that has not been trusted. Trusting a folder with `--trust` or `/hooks-trust` also trusts project MCP, LSP, hooks, project instructions, and project skills for that repository. [Skills](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md), [Hooks: Trusting a project](file:///C:/Users/ahmad/.grok/docs/user-guide/10-hooks.md), [Permissions: Best Practices](file:///C:/Users/ahmad/.grok/docs/user-guide/22-permissions-and-safety.md)

## Create one in the session

`/create-skill` asks for a name, a scope, and the workflow, drafts the description, and writes `<scope>/.grok/skills/<name>/SKILL.md`.

- Project: `<repo_root>/.grok/skills/<name>/`. Share it by committing that directory. Grok recommends this scope inside a git repository.
- User: `~/.grok/skills/<name>/`. Available in every project, and not shared through the repo.

The name must be 2–64 characters, lowercase letters, digits, and hyphens, and must start and end with a letter or digit. [Skills: Creating Skills with /create-skill](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

## Install a plugin that contains skills

A plugin can bundle skills with commands, agents, hooks, and MCP servers. Add a marketplace, then install one plugin. [Plugins](file:///C:/Users/ahmad/.grok/docs/user-guide/09-plugins.md)

```bash
grok plugin marketplace add my-org/team-plugins
grok plugin install deploy-tools --trust
```

`grok plugin install <source>` without `--trust` prints the source and stops. The source can be `owner/repo`, `owner/repo@v1.0`, `owner/repo@<commit-sha>`, `owner/repo#subdir`, a git URL, or a local path. [Plugins: Install and use a plugin](file:///C:/Users/ahmad/.grok/docs/user-guide/09-plugins.md)

Plugins stay off until enabled. After install, add the name or ID to `[plugins] enabled` in `~/.grok/config.toml`, or press `Space` on it in the Plugins tab. Skills, hooks, and MCP servers from a plugin stay inactive until the plugin is trusted. Plugins under `~/.grok/plugins/` are trusted automatically. Project plugins in `.grok/plugins/` need trust. Reload with `r` in the Plugins tab, or start a new session. [Plugins: Manage plugins](file:///C:/Users/ahmad/.grok/docs/user-guide/09-plugins.md), [Plugins: Trust and security](file:///C:/Users/ahmad/.grok/docs/user-guide/09-plugins.md), [Plugins: Troubleshooting](file:///C:/Users/ahmad/.grok/docs/user-guide/09-plugins.md)

In the terminal, `Ctrl+L` opens the extensions modal outside the VS Code family. On the VS Code family, use `/plugins`. `/skills` opens the same modal on the Skills tab. Marketplace install is the `i` key on the Marketplace tab. [Plugins: In the terminal UI](file:///C:/Users/ahmad/.grok/docs/user-guide/09-plugins.md), [Slash commands: /skills](file:///C:/Users/ahmad/.grok/docs/user-guide/04-slash-commands.md)

A plugin skill runs as `/plugin-name:skill-name` when the bare name collides with a built-in or another skill. A plugin skill does not replace a same-named native skill. [Skills: Qualified Names](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md), [Skills: Bundled and Plugin Skills](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

## Point Grok at an extra directory

In `~/.grok/config.toml`:

```toml
[skills]
paths = ["~/my-team-skills"]
ignore = ["~/my-team-skills/wip"]
disabled = ["wip-skill"]
```

Each `paths` entry is a `SKILL.md` file or a directory walked recursively. `ignore` hides a path. `disabled` keeps the skill listed and blocks invocation. `paths` and `ignore` are filesystem paths and accept `~`. `disabled` takes skill names. [Skills: Additional Skill Directories](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md), [Configuration: Skills](file:///C:/Users/ahmad/.grok/docs/user-guide/05-configuration.md)

`/import-claude` can record directories in `[paths] extra_skill_dirs`. That key does not inject skills. Extra directories belong in `[skills] paths`. [Skills: Additional Skill Directories](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md), [Config reference: paths.extra_skill_dirs](file:///C:/Users/ahmad/.grok/docs/user-guide/26-config-reference.md)

Claude and Cursor skill scans default to on. Turn one off with `[compat.claude] skills = false` or `[compat.cursor] skills = false`, or with `GROK_CLAUDE_SKILLS_ENABLED=false` or `GROK_CURSOR_SKILLS_ENABLED=false`. [Configuration: Harness compatibility](file:///C:/Users/ahmad/.grok/docs/user-guide/05-configuration.md)

The configuration guide says Codex `skills`, `rules`, `agents`, `mcps`, and `hooks` cells are reserved and currently inert, and do not enable `.codex` discovery. The config reference separately lists `compat.codex.skills` as a boolean that scans Codex skill directories when present. Those two pages disagree. Claude and Cursor discovery is the path the skills guide describes as on by default. [Configuration: Harness compatibility](file:///C:/Users/ahmad/.grok/docs/user-guide/05-configuration.md), [Config reference: compat](file:///C:/Users/ahmad/.grok/docs/user-guide/26-config-reference.md)

## Skills you do not copy in by hand

- Bundled platform skills are cached under `~/.grok/bundled/skills/`. Grok does not write them into `~/.grok/skills/`. A same-named local, repo, or user skill overrides the bundled copy. Under the `workspace`, `read-only`, and `strict` sandbox profiles, that cache is read-only, so Grok cannot download or update built-in skills until a session runs with `--sandbox off`. [Skills: Bundled and Plugin Skills](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md), [Sandbox](file:///C:/Users/ahmad/.grok/docs/user-guide/18-sandbox.md)
- A managed workspace can sync skills. `grok inspect` labels those `server`. A user skill of the same name shadows the synced one. [Plugins: Distribute across an organization](file:///C:/Users/ahmad/.grok/docs/user-guide/09-plugins.md)
- To share a skill with a team, package it in a plugin and publish a marketplace. [Skills: Choosing a Scope](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

## Check that it loaded

```bash
grok inspect
grok inspect --json
```

The Skills section names each skill and a source: `project`, `user`, `bundled`, `config`, `server`, or `plugin: <name>`. Disabled skills stay listed with `[disabled]`. Ignored paths are hidden. JSON includes `name`, `description`, `source` (with the `SKILL.md` path), and `userInvocable`. A name collision also includes `collidesWith` and `invocableAs`. [Skills: Viewing Skill Details](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

Inside a session, type `/` to filter skills and built-ins, or run `/skills` to open the Skills tab. Turning a skill off there stops it from being advertised as a slash command. An enabled skill with `user-invocable: true` (the default) is a slash command. `disable-model-invocation: true` keeps the slash command and stops automatic invocation. [Slash commands: /skills](file:///C:/Users/ahmad/.grok/docs/user-guide/04-slash-commands.md), [Slash commands: Skills as Slash Commands](file:///C:/Users/ahmad/.grok/docs/user-guide/04-slash-commands.md), [Skills: Optional Frontmatter Fields](file:///C:/Users/ahmad/.grok/docs/user-guide/08-skills.md)

If a plugin skill is missing: confirm `grok plugin list` shows it enabled and trusted, press `r` or start a new session, and run `grok plugin marketplace update` when the copy came from a marketplace. A skill symlink that points outside the plugin folder is skipped. On Windows, a skill file whose full path is longer than 260 characters is also skipped. [Plugins: Troubleshooting](file:///C:/Users/ahmad/.grok/docs/user-guide/09-plugins.md)
