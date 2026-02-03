# Contributing

Thanks for contributing to vBRIEF.

## Development workflow

This project is task-centric. Use `task` as the primary entrypoint.

```bash
task --list
```

Note: `task -C` is **concurrency**, not “change directory”. To run tasks from a different directory, use `task -d <dir> ...`.

Common commands:

```bash
task install
task check
task quality
```

## Git hooks (recommended)

Install local hooks for Conventional Commits + pre-commit checks:

```bash
task git:hooks:install
```

## Commit messages (required)

Use Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/

Examples:
- `feat(core): add TodoList builder`
- `fix(api-go): handle empty narratives`
- `docs: clarify TRON vs JSON`

## Pull requests

- Keep PRs focused and small when possible.
- Include tests or rationale if tests are not applicable.
- Update docs/spec text if the change affects behavior or structure.
