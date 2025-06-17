from fastapi import HTTPException
from typing import Dict, Optional, Any
import logging
import re
from database import get_or_create_customer
from interfaces.customer_service_interface import CustomerServiceInterface

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomerService(CustomerServiceInterface):
    # async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """Validate input data."""
    #     try:
    #         validated_data = {
    #             "name": await self.validate_name(data["name"]),
    #             "phone": await self.validate_phone(data["phone"])
    #         }
    #         return validated_data
    #     except Exception as e:
    #         await self.handle_error(e)
    #         raise

    # async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """Process the data."""
    #     try:
    #         validated_data = await self.validate(data)
    #         customer_id = get_or_create_customer(validated_data)
    #         validated_data["id"] = customer_id
    #         return validated_data
    #     except Exception as e:
    #         await self.handle_error(e)
    #         raise

    async def handle_error(self, error: Exception) -> None:
        """Handle service errors."""
        logger.error(f"Error in customer service: {str(error)}")
        if isinstance(error, HTTPException):
            raise error
        raise HTTPException(status_code=500, detail=str(error))

    async def validate_phone(self, phone: str) -> str:
        """Validate and format phone number."""
        # Remove any non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 10:
            raise HTTPException(
                status_code=400,
                detail="Phone number must contain at least 10 digits"
            )
        return digits_only

    async def validate_name(self, name: str) -> str:
        """Validate customer name."""
        name = name.strip()
        if not name:
            raise HTTPException(
                status_code=400,
                detail="Customer name cannot be empty"
            )
        if len(name) > 100:
            raise HTTPException(
                status_code=400,
                detail="Customer name cannot exceed 100 characters"
            )
        return name

    async def process_customer_data(self, customer_data: Dict) -> Dict:
        """Process and validate customer data."""
        return await self.process(customer_data)

    async def get_customer_by_id(self, customer_id: str) -> Optional[Dict]:
        """Get customer by ID."""
        # TODO: Implement customer retrieval by ID
        pass

    async def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        """Get customer by phone number."""
        # TODO: Implement customer retrieval by phone
        pass

# Create a singleton instance
customer_service = CustomerService() 