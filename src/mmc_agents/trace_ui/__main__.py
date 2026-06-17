"""Launch the trace UI: ``python -m mmc_agents.trace_ui``.

Defaults to ``http://127.0.0.1:8000``. Set ``MMC_TRACE_UI_HOST`` /
``MMC_TRACE_UI_PORT`` to override. Uses the live scenario runner — requires
``FOUNDRY_PLANT_PROJECT_ENDPOINT`` (and optionally
``FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT``) in the environment.
"""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
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
