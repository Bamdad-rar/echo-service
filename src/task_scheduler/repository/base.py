from abc import ABC, abstractmethod
from scheduler.domain.task import Task
from typing import Optional

class TaskRepository(ABC):
    """
    Abstract interface for a collection of Tasks. Defines the contract
    that all persistence implementations must adhere to.
    """

    @abstractmethod
    def add(self, task: Task) -> None:
        """Adds a new task to the repository."""
        raise NotImplementedError

    @abstractmethod
    def get(self, reference) -> Optional[Task]:
        """Retrieves a task by its unique ID."""
        raise NotImplementedError

    @abstractmethod
    def update(self, task: Task) -> None:
        """Updates an existing task."""
        raise NotImplementedError

    @abstractmethod
    def remove(self, reference) -> None:
        """Removes a task by its unique ID."""
        raise NotImplementedError

    @abstractmethod
    def get_due_tasks(self, limit: int) -> list[Task]:
        """Retrieves tasks that are due to be processed."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self, limit: int = 100, offset: int = 0) -> list[Task]:
        """Retrieves all tasks, with pagination."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Counts the total number of tasks."""
        raise NotImplementedError


