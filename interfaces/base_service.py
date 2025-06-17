from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseService(ABC):
    """Base interface for all services in the application.
    
    This interface defines common methods that all services should implement.
    It provides a foundation for consistent error handling across services.
    """
    
    # @abstractmethod
    # async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """Validate input data."""
    #     pass

    # @abstractmethod
    # async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """Process the data."""
    #     pass

    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """Handle service errors in a consistent way.
        
        Args:
            error: The exception that occurred during service operation.
        """
        pass 