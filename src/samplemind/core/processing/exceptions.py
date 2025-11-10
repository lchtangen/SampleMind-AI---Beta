from typing import Optional


class OptionalDependencyError(RuntimeError):
    """Raised when an optional runtime dependency is not available."""

    def __init__(self, package: str, message: Optional[str] = None) -> None:
        hint = message or (
            f"The optional package '{package}' is required for this feature. "
            f"Install it with `pip install {package}` or add it to your project extras."
        )
        super().__init__(hint)
        self.package = package
