import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from feedback_analyzer.interfaces.customer_service_interface import CustomerServiceInterface
from feedback_analyzer.services.customer_service import CustomerService

class TestCustomerService:
    @pytest.fixture
    def customer_service(self):
        return CustomerService()

    @pytest.fixture
    def mock_database(self):
        with patch('services.customer_service.get_or_create_customer') as mock:
            mock.return_value = "test_customer_id"
            yield mock

    @pytest.mark.asyncio
    async def test_validate_valid_data(self, customer_service):
        data = {
            "name": "Test User",
            "phone": "1234567890"
        }
        result = await customer_service.validate(data)
        assert result["name"] == "Test User"
        assert result["phone"] == "1234567890"

    @pytest.mark.asyncio
    async def test_validate_empty_name(self, customer_service):
        data = {
            "name": "",
            "phone": "1234567890"
        }
        with pytest.raises(HTTPException) as exc_info:
            await customer_service.validate_name(data["name"])
        assert exc_info.value.status_code == 400
        assert "Customer name cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_long_name(self, customer_service):
        data = {
            "name": "x" * 101,
            "phone": "1234567890"
        }
        with pytest.raises(HTTPException) as exc_info:
            await customer_service.validate_name(data["name"])
        assert exc_info.value.status_code == 400
        assert "Customer name cannot exceed 100 characters" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_short_phone(self, customer_service):
        data = {
            "name": "Test User",
            "phone": "123"
        }
        with pytest.raises(HTTPException) as exc_info:
            await customer_service.validate_phone(data["phone"])
        assert exc_info.value.status_code == 400
        assert "Phone number must contain at least 10 digits" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_phone_with_special_chars(self, customer_service):
        phone = "(123) 456-7890"
        result = await customer_service.validate_phone(phone)
        assert result == "1234567890"

    @pytest.mark.asyncio
    async def test_process_valid_data(self, customer_service, mock_database):
        data = {
            "name": "Test User",
            "phone": "1234567890"
        }
        result = await customer_service.process(data)
        assert result["name"] == "Test User"
        assert result["phone"] == "1234567890"
        assert result["id"] == "test_customer_id"
        mock_database.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_invalid_data(self, customer_service):
        data = {
            "name": "",
            "phone": "123"
        }
        with pytest.raises(HTTPException) as exc_info:
            await customer_service.process(data)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_handle_error_http_exception(self, customer_service):
        error = HTTPException(status_code=400, detail="Test error")
        with pytest.raises(HTTPException) as exc_info:
            await customer_service.handle_error(error)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Test error"

    @pytest.mark.asyncio
    async def test_handle_error_generic_exception(self, customer_service):
        error = Exception("Test error")
        with pytest.raises(HTTPException) as exc_info:
            await customer_service.handle_error(error)
        assert exc_info.value.status_code == 500
        assert str(error) in str(exc_info.value.detail) 