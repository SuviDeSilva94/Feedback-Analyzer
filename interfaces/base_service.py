from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseService(ABC):
    """Base interface for all services."""
    
    @abstractmethod
    async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data."""
        pass

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the data."""
        pass

    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """Handle service errors."""
        pass 