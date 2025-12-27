# Development standards

## Task-centric workflow

Use `task` as the primary entrypoint for repeatable actions.

```bash
task --list
task install
task check
task quality
```

Note: `task -C` is **concurrency**, not “change directory”. To run tasks from a different directory, use `task -d <dir> ...`.

## Conventional Commits (required)

Commit messages must follow Conventional Commits:
https://www.conventionalcommits.org/en/v1.0.0/

Format:
- `type(scope?)!?: subject`

Allowed types (common):
- `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`

Examples:
- `feat(core): add TRON serializer`
- `fix(api-go): guard nil pointer`
- `ci: add coverage gate`
