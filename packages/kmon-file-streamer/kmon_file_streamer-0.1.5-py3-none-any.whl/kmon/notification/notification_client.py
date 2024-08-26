from abc import ABC, abstractmethod
from typing import Optional


class NotificationSender(ABC):
    @abstractmethod
    def send(self, message: str, subject: Optional[str] = None) -> None:
        pass