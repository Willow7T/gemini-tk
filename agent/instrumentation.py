import os
from typing import Any, Optional

_provider: Optional[Any] = None

def setup_tracing() -> Optional[Any]:
    global _provider

    if _provider is not None:
        return _provider

    try:
        from phoenix.otel import register

        if not (
            os.environ.get("PHOENIX_API_KEY")
            or os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")
        ):
            print("Tracing skipped: PHOENIX environment variables not set.")
            return None

        _provider = register(
            project_name=os.environ.get(
                "PHOENIX_PROJECT_NAME",
                "plant-disease-agent"
            ),
            batch=False,
            auto_instrument=True,
            verbose=False,
        )

        print("Tracing initialized successfully.")
        return _provider

    except Exception as e:
        print(f"Tracing disabled: {e}")
        return None