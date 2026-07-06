# Nested Projects

This workspace contains two nested Git repositories that are intentionally not vendored into the parent repository.

## `social-auto-upload/`

Remote:

```text
https://github.com/dreammis/social-auto-upload.git
```

Role:

- Multi-platform upload tooling used by the studio workflow.
- Treated as an upstream dependency, not owned source in this parent repository.

Upload decision:

- Do not copy its `.git` history or generated runtime state into `daily-content-studio`.
- Keep local cookies, logs, `.venv`, and runtime database ignored.

## `sports-psychology-comic/`

Current local state:

- Clean local Git repository.
- Contains the sports philosophy workflow, templates, strategies, and rendering scripts.

Current remote:

```text
git@github.com:davidpeng611-hub/-.git
```

Issue:

- The remote name is not a useful project name and was not readable through the GitHub API during this upload pass.

Recommended next step:

- Create a proper GitHub repository, for example:

```text
davidpeng611-hub/sports-psychology-comic
```

- Then update the nested repo remote and push it separately:

```bash
cd sports-psychology-comic
git remote set-url origin git@github.com:davidpeng611-hub/sports-psychology-comic.git
git push -u origin main
```

Why not vendor it now:

- It is an independent project with its own Git history.
- It contains generated packages and media paths that should stay controlled by its own `.gitignore`.
- Vendoring it into the parent repo would mix two project lifecycles and make future pushes harder.

