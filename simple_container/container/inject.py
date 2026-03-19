"""
inject.py - Updated with better error handling for request scope
"""

from typing import override
from simple_container.container.container_registry import ContainerRegistry
from simple_container.container.interfaces import IResolvable
from simple_container.container.simple_container import (
    ServiceNotFoundError,
    ContainerError,
    RequestScopeNotActiveError,  # NEW
)


class Inject[T]:
    """Type-safe dependency injection using complete protocol."""

    def __init__(self, service_type: type[T]) -> None:
        self.service_type: type[T] = service_type

    def __call__(self) -> T:
        """Called by FastAPI's Depends() system."""
        try:
            container: IResolvable = ContainerRegistry.get_current()
            return container.resolve(self.service_type)

        except RequestScopeNotActiveError as e:
            # Special handling for request scope errors
            raise RuntimeError(
                "Request scope not configured for "
                f"{self.service_type.__name__}: {e}. "
                "Add RequestScopeMiddleware to your FastAPI app"
            ) from e

        except ServiceNotFoundError as e:
            raise RuntimeError(
                f"Service {self.service_type.__name__} not registered: {e}"
            ) from e

        except ContainerError as e:
            raise RuntimeError(f"Container error: {e}") from e

    @override
    def __repr__(self) -> str:
        return f"Inject({self.service_type.__name__})"
