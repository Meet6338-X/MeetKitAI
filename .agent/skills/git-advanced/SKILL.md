---
name: git-advanced
description: Advanced Git workflows. Rebasing, cherry-picking, bisect, reflog, hooks, monorepo strategies.
---

# Git Advanced Skill

Advanced Git workflows and techniques for professional development.

## When to Use
- Complex branching strategies
- Debugging with git bisect
- Recovering from mistakes
- Setting up Git hooks
- Managing monorepos

## Advanced Workflows

### 1. Interactive Rebase

```bash
# Rebase last 5 commits interactively
git rebase -i HEAD~5

# Commands in interactive rebase:
# pick   - keep commit as is
# reword - change commit message
# edit   - stop for amending
# squash - merge into previous commit
# fixup  - squash without keeping message
# drop   - remove commit

# Rebase onto main
git rebase -i main

# Abort if things go wrong
git rebase --abort
```

### 2. Cherry-Picking

```bash
# Apply specific commit to current branch
git cherry-pick abc1234

# Cherry-pick without committing
git cherry-pick -n abc1234

# Cherry-pick range of commits
git cherry-pick abc1234..def5678

# Handle conflicts
git cherry-pick --continue
git cherry-pick --abort
```

### 3. Git Bisect (Find Bug-Introducing Commit)

```bash
# Start bisect
git bisect start

# Mark current commit as bad
git bisect bad

# Mark known good commit
git bisect good v1.0.0

# Git will checkout middle commit
# Test and mark as good or bad
git bisect good  # or git bisect bad

# Repeat until found
# When done:
git bisect reset

# Automated bisect with test script
git bisect run npm test
```

### 4. Reflog (Recover Lost Commits)

```bash
# View reflog
git reflog

# Recover deleted branch
git checkout -b recovered-branch HEAD@{5}

# Undo hard reset
git reset --hard HEAD@{2}

# Find lost commits
git fsck --lost-found
```

### 5. Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/sh
npm run lint && npm run test

# Make executable
chmod +x .git/hooks/pre-commit
```

**Using Husky (Recommended):**
```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  },
  "lint-staged": {
    "*.{js,ts}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": "prettier --write"
  }
}
```

### 6. Conventional Commits

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `perf:` - Performance improvement
- `test:` - Adding tests
- `chore:` - Maintenance

**Examples:**
```bash
git commit -m "feat(auth): add OAuth2 login support"
git commit -m "fix(api): handle null response in user endpoint"
git commit -m "docs: update API documentation for v2"
```

### 7. Stashing Strategies

```bash
# Stash with message
git stash push -m "WIP: feature X"

# Stash specific files
git stash push -m "partial work" -- file1.js file2.js

# List stashes
git stash list

# Apply specific stash
git stash apply stash@{2}

# Pop and delete
git stash pop

# Create branch from stash
git stash branch new-branch stash@{0}

# Clear all stashes
git stash clear
```

### 8. Worktrees (Multiple Working Directories)

```bash
# Create worktree for hotfix
git worktree add ../hotfix-branch hotfix/urgent

# List worktrees
git worktree list

# Remove worktree
git worktree remove ../hotfix-branch

# Prune stale worktrees
git worktree prune
```

### 9. Submodules & Subtrees

**Submodules:**
```bash
# Add submodule
git submodule add https://github.com/user/repo libs/repo

# Clone with submodules
git clone --recurse-submodules https://github.com/user/main-repo

# Update submodules
git submodule update --remote --merge

# Initialize after clone
git submodule init
git submodule update
```

**Subtrees (Preferred for most cases):**
```bash
# Add subtree
git subtree add --prefix=libs/repo https://github.com/user/repo main --squash

# Pull updates
git subtree pull --prefix=libs/repo https://github.com/user/repo main --squash

# Push changes back
git subtree push --prefix=libs/repo https://github.com/user/repo main
```

### 10. Branching Strategies

**Git Flow:**
```
main ────────────────────────────────────►
       ↑               ↑
hotfix/fix ──────►     │
                       │
develop ──────────────────────────────────►
    ↑         ↑              ↑
feature/a ───►│              │
              │              │
    feature/b ───────────────►
```

**Trunk-Based Development:**
```
main ────────────────────────────────────►
 ↑    ↑    ↑    ↑    ↑    ↑
 │    │    │    │    │    │
Short-lived feature branches (< 2 days)
```

### 11. Useful Aliases

```bash
# Add to ~/.gitconfig
[alias]
  co = checkout
  br = branch
  ci = commit
  st = status
  lg = log --oneline --graph --all
  last = log -1 HEAD
  unstage = reset HEAD --
  amend = commit --amend --no-edit
  undo = reset --soft HEAD~1
  wip = !git add -A && git commit -m 'WIP'
  unwip = reset HEAD~1
  cleanup = !git branch --merged | grep -v main | xargs git branch -d
```

### 12. Debugging Commands

```bash
# Who changed this line?
git blame file.js

# Search commit messages
git log --grep="bug fix"

# Search code changes
git log -S "function_name" --oneline

# Show file at specific commit
git show abc1234:path/to/file.js

# Diff between branches
git diff main..feature-branch -- src/

# Find large files in history
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print $3, $4}' | sort -rn | head -10
```

### 13. Cleanup & Maintenance

```bash
# Remove untracked files
git clean -fd

# Remove ignored files too
git clean -fdx

# Garbage collection
git gc --aggressive --prune=now

# Verify repository
git fsck --full

# Prune remote-tracking branches
git remote prune origin
git fetch --prune
```
