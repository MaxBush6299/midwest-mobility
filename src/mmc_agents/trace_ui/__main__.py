"""Launch the trace UI: ``python -m mmc_agents.trace_ui``.

Defaults to ``http://127.0.0.1:8000``. Set ``MMC_TRACE_UI_HOST`` /
``MMC_TRACE_UI_PORT`` to override. Uses the live scenario runner — requires
``FOUNDRY_PLANT_PROJECT_ENDPOINT`` (and optionally
``FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT``) in the environment, which are loaded
from ``.env`` at startup if present.
"""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv


def main() -> None:
    # Load repo-root .env so the live runner sees Foundry endpoints.
    repo_root = Path(__file__).resolve().parents[3]
    env_path = repo_root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

    host = os.environ.get("MMC_TRACE_UI_HOST", "127.0.0.1")
    port = int(os.environ.get("MMC_TRACE_UI_PORT", "8000"))
    uvicorn.run(
        "mmc_agents.trace_ui.app:create_app",
        host=host,
        port=port,
        factory=True,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()
