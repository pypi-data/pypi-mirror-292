from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..IValidationContext import ValidationContext


@dataclass
class IPropertyValidator[T, TProperty](ABC):
    @property
    @abstractmethod
    def Name(self) -> str:
        ...

    @abstractmethod
    def get_default_message_template(self, error_code: str) -> str:
        ...

    @abstractmethod
    def is_valid(self, context: ValidationContext[T], value: TProperty) -> bool:
        ...
