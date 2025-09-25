"""Test configuration and fixtures."""

import pytest
import asyncio
from typing import Generator
from unittest.mock import AsyncMock, Mock

# Test fixtures for database mocking
@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    mock_client = Mock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute = AsyncMock(
        return_value=Mock(data=[])
    )
    return mock_client


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "type": "expense",
        "amount": 50.00,
        "description": "Test expense",
        "category": "Food & Dining",
        "date": "2024-01-15",
        "merchant": "Test Restaurant"
    }


@pytest.fixture
def sample_transaction_response():
    """Sample transaction response for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "user123",
        "type": "expense",
        "amount": 50.00,
        "description": "Test expense", 
        "category": "Food & Dining",
        "date": "2024-01-15",
        "merchant": "Test Restaurant",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
    }


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()