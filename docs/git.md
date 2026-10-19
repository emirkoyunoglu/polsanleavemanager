# Git

> Bootstrap'ta (2026-10-19) ANEW varsayılanları olduğu gibi kabul edildi. Branch adları ve commit
> mesajları İngilizce (`docs/conventions.md`).

## Branching
- `feature/<spec-no>-<short-name>` — **no branch without a spec.** Also for CHANGE-lane mini-specs.
- Refactors: `refactor/<spec-no>-<short-name>` (mini-spec with Changed behavior = none).
- Fixes: `fix/<report-id>-<short-name>` (bug fixes carry a report, not a spec number);
  incidents: `incident/<date>-<short-name>`; trivial changes: `trivial/<short-name>` (see below).

## Commits
- Conventional Commits, with a plan reference: `feat(catalog): paging endpoint [plan 0001/3]`.
- Agent commits follow the same standard: the agent writes the message, the human approves.

## Forbidden
- Direct commits to the default branch.
- Force push, history rewriting on shared branches. Undo = `git revert` (see recovery R-11).

## Trivial changes
Yalnızca change-request triage rubriğinin (`workflows/change-request.md`) TRIVIAL saydığı işler
için geçerlidir: hiçbir kabul kriteri değişmez, paylaşılan koda dokunulmaz.
- Policy: **(1) PR + one reviewer, no spec** — bootstrap'ta seçildi. `trivial/<short-name>`
  branch'inden PR açılır, bir reviewer onaylar, CI'da `scripts/check` yeşil olur.
- Always: one narrow commit, `scripts/check` green. A second file or a new test means re-triage.

## Pull requests
- PR template checklist completed; `scripts/check` green in CI; squash-merge.
