---
name: commit-ai-settings
description: Commit AI instruction, skill, and configuration changes in MASSMa-codes when Paolo Rossi explicitly requests a commit, including ChatGPT and the active model as co-author. Also apply alongside an authorized AI-settings edit when the same request includes committing it.
---

# Commit AI Settings

Use this workflow for repository-local AI settings such as `AGENTS.md`, skills
under `.agents/skills/`, and tracked AI configuration under `.codex/`.
An ordinary program, notebook, or Python heading update is not an AI-settings
change.

## Authorization and scope

- Commit only when Paolo Rossi requests it. A request to edit AI settings alone
  does not authorize a commit. A request to edit and commit authorizes both;
  do not ask for confirmation again.
- Resolve the intended settings from the current request and conversation.
  Inspect the working tree and index before staging. Include only the requested
  settings changes; preserve unrelated edits and anything already staged.
- Do not include credentials, tokens, local session history, or machine-specific
  private configuration. If these occur in a requested file, exclude the secret
  material and explain what remains uncommitted.

## Commit workflow

1. Finish the requested changes and inspect their diff. For skills, validate
   their frontmatter and structure with the available skill creator validator.
   Use appropriate syntax validation for other configuration formats.
2. Stage the intended paths or hunks explicitly. Avoid `git add .` and
   `git add -A`. Ensure the commit cannot absorb unrelated staged changes;
   preserve their index state, using an isolated temporary index if necessary.
3. Keep the repository's configured human author identity. Write a concise
   commit message describing the resulting settings behavior, with a blank
   line before this trailer:

   ```text
   Co-authored-by: ChatGPT (<actual model name>) <noreply@openai.com>
   ```

   Replace the model placeholder with the reliable active-session model name.
   Do not invent a version; if the identity is unavailable, ask for it. This
   trailer is attribution, not a claim that the email maps to a GitHub account.
4. Check the new commit's message and changed paths, and confirm unrelated work
   and staged changes are preserved. If there are no requested changes to
   commit, report that instead of creating an empty commit.
5. Report the commit hash, settings changed, and co-author used. Push only if
   Paolo also requests publication; an existing request to push is sufficient.

## Replacing existing commits

Rewrite history only when Paolo explicitly requests it. Check the current
remote state first. For unpublished commits, retain a recoverable local backup
ref and preserve later commits' contents when replacing an earlier commit.
Include the co-author trailer in every commit you create, including replays.
If a replacement would require rewriting published history, explain the impact
and obtain explicit authorization for that remote rewrite. Never infer force
push permission from a request for co-author attribution alone.
