from abc import ABC, abstractmethod
from typing import Dict, Optional
from .base_service import BaseService

class CustomerServiceInterface(BaseService):
    """Interface for customer-related operations."""
    
    @abstractmethod
    async def validate_phone(self, phone: str) -> str:
        """Validate and format phone number."""
        pass

    @abstractmethod
    async def validate_name(self, name: str) -> str:
        """Validate customer name."""
        pass

    # @abstractmethod
    # async def process_customer_data(self, customer_data: Dict) -> Dict:
    #     """Process and validate customer data."""
    #     pass

    @abstractmethod
    async def get_customer_by_id(self, customer_id: str) -> Optional[Dict]:
        """Get customer by ID."""
        pass

    @abstractmethod
    async def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        """Get customer by phone number."""
        pass 