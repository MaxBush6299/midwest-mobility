# Contributing

Thanks for your interest in improving the Midwest Mobility Components (MMC)
multi-agent manufacturing demo! This is a reference/demo project, so
contributions that improve clarity, reproducibility, and correctness are
especially welcome.

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Bug fixes** — scenarios, tooling, trace UI, or setup scripts.
- **Docs** — clarifications to the README, architecture doc, or dataset card.
- **New scenarios** — additional Magentic orchestration examples.
- **Reproducibility** — anything that makes a clean-machine setup smoother.

For anything larger than a small fix, please open an issue first to discuss the
approach.

## Development setup

Prerequisites:

- Python **3.11+**
- An Azure subscription with access to Azure AI Foundry, Azure AI Search, and
  Azure SQL (only needed to run the demo live; tests run fully mocked).

```powershell
# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install the package with dev dependencies
pip install -e .[dev]

# Copy the example environment file and fill in your own values
copy .env.example .env
```

> **Never commit secrets.** Real endpoints, subscription/tenant IDs, and keys
> belong only in your local, git-ignored `.env`. The repository is designed to
> contain no tenant-specific identifiers — see [SECURITY.md](SECURITY.md).

## Running tests

The test suite mocks all Azure calls, so it runs offline:

```powershell
pytest
```

Please add or update tests for any behavior change. Snapshot tests under
`tests/snapshots/` pin agent-factory output; if you intentionally change that
output, update the snapshots in the same PR and explain why.

## Linting and style

We use [ruff](https://docs.astral.sh/ruff/):

```powershell
ruff check .
```

Please keep changes focused and idiomatic. Avoid unrelated refactors in a PR.

## Project conventions

- **`profile.yaml` is the single source of truth.** Agents, KB sources, tools,
  and skills are defined there; cards, KB seed input, agent versions, and
  snapshots are all derived from it. Change the profile, then regenerate
  derived artifacts rather than hand-editing them.
- **The dataset is fictional and internally cross-consistent.** Keep it that
  way so scenarios resolve end-to-end. Stay consistent with
  `docs/MMC_Plant7_Company_Profile_v1.md` for names, site/line IDs, and ID
  formats.
- **Do not add columns to the CSV logs** without also updating the company
  profile and any dependent schema/fixtures.
- **Keep the reasoning layer model-agnostic.** Don't hardcode a specific model
  vendor into the orchestration logic.

## Pull request process

1. Fork the repo and create a topic branch.
2. Make your change with accompanying tests and docs.
3. Ensure `pytest` and `ruff check .` pass.
4. Open a PR with a clear description of the what and why. Link any related
   issue.

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE) that covers this project.
