class ProfileError(Exception):
    """Base exception for all profile-related errors."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ProfileNotFoundError(ProfileError):
    """Raised when a profile is requested but does not exist."""
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Profile '{name}' not found.")


class ProfileLoadError(ProfileError):
    """Raised when profiles.pkl cannot be loaded (corrupted, permission, etc.)."""
    def __init__(self, message: str = "Failed to load profiles.pkl"):
        super().__init__(message)


class ProfileSaveError(ProfileError):
    """Raised when saving profile data fails."""
    def __init__(self, message: str = "Failed to save profile data"):
        super().__init__(message)


class ProfileValidationError(ProfileError):
    """Raised when profile data is invalid (empty name, etc.)."""
    def __init__(self, message: str):
        super().__init__(f"Profile validation failed: {message}")

class GeneralError(Exception):
    """raised for general stuff, like the api key not existing"""
    def __init__(self, message: str) -> None:
        super().__init__(message)