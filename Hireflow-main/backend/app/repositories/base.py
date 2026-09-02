"""Base repository with generic CRUD method signatures.

All concrete repositories inherit from BaseRepository.
CRUD implementations will be added when models are defined.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository providing CRUD method signatures.

    Attributes:
        model: The SQLAlchemy model class this repository manages.
        db: The database session.
    """

    def __init__(self, model: type[ModelType], db: Session) -> None:
        self.model = model
        self.db = db

    def get_by_id(self, entity_id: int) -> ModelType | None:
        """Retrieve a single entity by its primary key.

        Args:
            entity_id: The primary key value.

        Returns:
            The entity instance or None if not found.
        """
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def get_all(self, skip: int = 0, limit: int = 20) -> list[ModelType]:
        """Retrieve a paginated list of entities.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of entity instances.
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def count(self) -> int:
        """Return the total count of entities.

        Returns:
            Total number of records.
        """
        return self.db.query(self.model).count()

    def create(self, entity: ModelType) -> ModelType:
        """Persist a new entity to the database.

        Args:
            entity: The model instance to create.

        Returns:
            The persisted entity with database-generated fields.
        """
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelType, update_data: dict[str, Any]) -> ModelType:
        """Update an existing entity with the given data.

        Args:
            entity: The existing model instance.
            update_data: Dictionary of field names and new values.

        Returns:
            The updated entity.
        """
        for field, value in update_data.items():
            setattr(entity, field, value)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        """Remove an entity from the database.

        Args:
            entity: The model instance to delete.
        """
        self.db.delete(entity)
        self.db.commit()
