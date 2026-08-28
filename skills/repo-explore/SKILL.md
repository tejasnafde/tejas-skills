---
name: repo-explore
description: Clone and explore external GitHub repositories to understand how libraries, frameworks, or dependencies work. Use when user provides a GitHub URL (github.com/owner/repo), asks "how does X library work", wants to look at source code for a dependency, asks about implementation details of an external package, or says "explore", "look at", or "check out" a repository. Automatically checks out the matching version tag when the repo is a dependency in the current project.
context: fork
allowed-tools:
  - Bash(git:*)
  - Bash(ls:*)
  - Read
  - Glob
  - Grep
  - Agent
---

# Repo Explore Skill

Explore external GitHub repositories by cloning them locally and using the Explore agent for comprehensive codebase analysis.

## Cache Location

```
~/.cache/claude/repos/<owner>/<repo>/
```

## Workflow

### 1. Parse Repository URL

Extract owner and repo from various formats:
- `https://github.com/owner/repo`
- `git@github.com:owner/repo.git`
- `owner/repo` (shorthand)
- `github.com/owner/repo`

### 2. Check Cache

```bash
ls ~/.cache/claude/repos/<owner>/<repo>/
```

- **If exists**: Check if update needed (see `references/update-reference.md`)
- **If not exists**: Proceed to clone

### 3. Clone Repository

```bash
mkdir -p ~/.cache/claude/repos/<owner>
git clone https://github.com/<owner>/<repo>.git ~/.cache/claude/repos/<owner>/<repo>
```

### 4. Version Detection

Before exploring, check if this repo is a dependency in the current working directory.

Consult `references/version-detection.md` for:
- Which dependency files to check
- How to extract versions from each format
- How to map versions to git tags

If a matching version is found:
```bash
cd ~/.cache/claude/repos/<owner>/<repo>
git fetch --all --tags
git checkout <tag>
```

Common tag formats to try:
- `v1.2.3`
- `1.2.3`
- `release-1.2.3`
- `release/1.2.3`

### 5. Explore with Explore Agent

Use the Agent tool with `subagent_type=Explore` to answer questions about the repository, rather than browsing files yourself. The Explore agent is optimized for:
- Finding files by patterns
- Searching code for keywords
- Understanding codebase architecture
- Answering questions about how code works

Example:
```
Agent(
  subagent_type="Explore",
  prompt="""In ~/.cache/claude/repos/owner/repo/, find how authentication is implemented.

Requirements for your response:
- Include code snippets with file paths and line numbers
- Show key type definitions and function signatures
- End with a 'Key Files for Further Exploration' table with columns: File, Purpose, Start Here If...
"""
)
```

### 6. Response Format Requirements

The Agent prompt template above carries the full format. In short:

- Include code snippets with file paths and line numbers (`pkg/controller/foo.go:42-58`)
- End with a "Key Files for Further Exploration" table of 3-7 files, most fundamental first
- Lead with a brief 2-3 sentence answer summary before the detail

### 7. Updates

For refreshing the repository or switching versions, consult `references/update-reference.md`.

## Notes

- Verify the checkout succeeded before exploring
- If the user asks about a specific version, checkout that version even if not a dependency
- For private repos, the clone will work if the user has git credentials configured
- Large repos may take time to clone; inform the user
