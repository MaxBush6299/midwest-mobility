"""OTel/App Insights wiring so Magentic+agent spans land in the Foundry portal Tracing tab.

Call ``setup_tracing()`` once at process start. Idempotent — no-ops if no
APPLICATIONINSIGHTS_CONNECTION_STRING is set.
"""
from __future__ import annotations

import logging
import os

_INITIALIZED = False
_log = logging.getLogger(__name__)


def setup_tracing() -> bool:
    """Configure Azure Monitor + Agent Framework instrumentation.

    Returns True iff a real exporter was wired up.
    """
    global _INITIALIZED
    if _INITIALIZED:
        return True

    conn = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not conn:
        _log.info("APPLICATIONINSIGHTS_CONNECTION_STRING not set; tracing disabled")
        return False

    from azure.monitor.opentelemetry import configure_azure_monitor
    from agent_framework.observability import (
        enable_instrumentation,
        enable_sensitive_telemetry,
    )

    configure_azure_monitor(connection_string=conn)
    enable_sensitive_telemetry()
    enable_instrumentation()
    _INITIALIZED = True
    _log.info("Azure Monitor + Agent Framework instrumentation enabled")
    return True
