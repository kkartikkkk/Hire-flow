"""Base service class.

All business logic services inherit from BaseService.
"""

from app.repositories.base import BaseRepository


class BaseService:
    """Base class for all business logic services.

    Attributes:
        repository: The primary repository this service operates on.
    """

    def __init__(self, repository: BaseRepository) -> None:
        self.repository = repository
