# Publish to GitHub after authentication

Initial inspection: `gh auth status` could not run because `gh` was not on PATH, and common GitHub CLI installation paths were absent. No GitHub remote was created, no existing remote repository was inspected, and no push was attempted. The local repository uses `main`.

Run in PowerShell:

```powershell
winget install --id GitHub.cli --exact --source winget
```

Open a new PowerShell window so PATH is refreshed, then:

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth status --hostname github.com
gh api user --jq .login
```

Continue only when the reported login is `rayaneDR`. If another account is active, use `gh auth switch --hostname github.com --user rayaneDR` (after adding that account with `gh auth login` if needed).

From this repository's root, inspect first:

```powershell
gh repo view rayaneDR/CyberNova-MED-AI --json nameWithOwner,url,isPrivate,defaultBranchRef
```

If the authenticated request definitively reports **Not Found** (not a network or authorization failure), create and push:

```powershell
gh repo create rayaneDR/CyberNova-MED-AI --public --source . --remote origin --push
```

If the remote already exists, inspect it before any push. Do not recreate, overwrite, force-push, or replace its history. Add the URL returned by `gh repo view` as origin only if no origin exists, then `git fetch origin` and inspect `git log --all --oneline --graph` to reconcile histories safely. An empty existing remote can accept `git push -u origin main`. A populated remote needs a deliberate integration of local changes with its existing branch. Check public visibility; do not change an existing repository's visibility without reviewing its contents.

After successful publication, verify:

```powershell
git remote -v
git remote get-url origin
gh repo view --json nameWithOwner,url,isPrivate,defaultBranchRef
git ls-remote origin refs/heads/main
git rev-parse HEAD
```

The final two hashes should match. Update README publication status only after verification. Local commits initially use repository-local author `Rayane <rayaneDR@users.noreply.github.com>` because no Git author identity was configured; this is not proof of authentication or verified GitHub email attribution.
