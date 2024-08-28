class NoxiiError(Exception):
    """Base exception class for all Noxii exceptions."""
    pass


class InvalidAPIKey(NoxiiError):
    """Raised when an invalid API key is provided or if no key was found
    in the environment variables.
    """

    def __init__(self, msg: str | None = None):
        super().__init__(msg or "Invalid API key.")


class NotFound(NoxiiError):
    """Raised when an object is not found."""
    pass


class UserNotFound(NotFound):
    """Raised when the given user ID is not found."""

    def __init__(self):
        super().__init__("Could not find the user ID.")


class GuildNotFound(NotFound):
    """Raised when the given guild ID is not found."""

    def __init__(self):
        super().__init__("Could not find the guild ID.")


class NoGuildAccess(NoxiiError):
    """Raised when you do not have access to a guild."""

    def __init__(self):
        super().__init__("You are not a member of this guild.")
