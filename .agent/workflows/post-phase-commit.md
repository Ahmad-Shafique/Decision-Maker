---
description: Auto-commit and push after completing a phase or module
---

After completing each phase or module of work, commit and push changes to version control.

// turbo-all
1. Stage all changes:
   ```
   git add -A
   ```

2. Commit with descriptive message:
   ```
   git commit -m "Complete [Phase Name]: [Brief description of changes]"
   ```
   
   Examples:
   - "Complete Phase 2: Async UI and matching visibility"
   - "Complete Phase 3: Android mobile app MVP"
   - "Fix: Semantic matching threshold adjustment"

3. Push to remote:
   ```
   git push origin main
   ```

4. If push fails (e.g., no remote configured), notify user with suggested next steps.

## When to Run This Workflow

- After completing a planned phase (as defined in `.agent/planning/`)
- After fixing all bugs in a module
- Before switching to a new major feature
- When the user explicitly requests a checkpoint

## Important Notes

- Always ensure tests pass before committing
- Include meaningful commit messages that reference the phase/module
- If there are uncommitted changes when starting new work, commit them first
