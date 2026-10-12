# Agent Development Guidelines

## Project Overview

Telegram bot for The Black 169 loyalty program with QuickResto integration. Handles bonus system, promotions, events,
and customer data management. The bot integrates with QuickResto API for customer management, bonus operations, and data
synchronization.

## Build Commands

```bash
pip install -r requirements.txt
python main.py
```

## Lint/Format Commands

```bash
# Linting (using ruff)
ruff check .
ruff check --fix .

# Formatting (using ruff)
ruff format .
ruff format --check .
```

## Test Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file.py

# Run specific test
pytest tests/test_file.py::TestClass::test_method

# Run with coverage
pytest --cov=services tests/

# Run specific test with verbose output
pytest -v tests/test_bonus_system.py
```

## Code Style Guidelines

### Imports

- Order: standard library → third-party → local modules
- Use explicit imports over wildcard imports
- Group related imports with blank lines
- Import only what's actually used

```python
# Correct order:
import os
import sys
from datetime import datetime

import peewee
from aiogram import Router
from aiogram.types import CallbackQuery

from services.database import get_user_info
from utils.logger import logger
```

### Formatting

- Follow PEP 8 guidelines
- Line length: 88 characters
- Use f-strings for string formatting
- Indent with 4 spaces (no tabs)
- Sort imports with ruff

### Type Hints

- All functions must have type hints
- Use Union[X, Y] or X | Y for union types
- Use Optional[X] for nullable types
- Annotate return values where possible

```python
def get_user_info(id_telegram: int) -> dict | None:
    ...
```

### Naming Conventions

- Function names: snake_case
- Class names: PascalCase
- Constants: UPPER_CASE
- Variables: snake_case
- Private members: _private_snake_case

### Error Handling

- Use try/except blocks for expected exceptions
- Log errors with detailed context
- Handle NULL values explicitly
- Use defensive programming techniques
- Always close database connections in finally blocks

### Database Operations

- Use Peewee ORM consistently
- Always close connections in finally blocks
- Use transactions for multiple operations
- Handle NULL values properly
- Check if connection is closed before opening
- Use get_or_none() for single object retrieval to avoid exceptions

### Logging

- Use structured logging with context
- Include relevant IDs in log messages
- Use appropriate log levels (info, warning, error, exception)
- Never log sensitive data
- Use logger.exception() for logging exceptions with traceback

### Comments

- Use docstrings for public functions
- Comment complex logic thoroughly
- Avoid obvious comments
- Keep comments up to date with code
- Document parameters and return values

### Security

- Validate input parameters
- Never store passwords in plain text
- Use prepared statements for DB queries
- Sanitize user inputs before processing
- Implement proper consent handling for personal data

### Async Programming

- Use async/await for I/O operations
- Don't block the event loop
- Properly handle exceptions in coroutines
- Close resources appropriately
- Use FSM context for state management where needed

## Testing Guidelines

### Test Structure

- Use pytest framework
- Test functions start with 'test_'
- Use fixtures for setup/cleanup
- Parameterized tests where applicable

### Test Coverage

- Aim for 80%+ coverage on business logic
- Test edge cases and error conditions
- Mock external dependencies (QuickResto API)
- Verify side effects and state changes
- Test both positive and negative scenarios

### Integration Tests

- Test database operations
- Verify API integrations
- Check data consistency
- Validate async behavior
- Test FSM state transitions

## QuickResto Integration

- All QuickResto API calls must include proper headers and auth
- Handle rate limiting gracefully
- Validate response formats
- Implement retry logic for transient failures
- Normalize phone numbers consistently

## Configuration

- Store environment variables in .env files
- Use config.py for application settings
- Handle missing configuration gracefully
- Never commit secrets to version control
- Use default values where appropriate

## Error Patterns

- Always check if database objects exist before accessing
- Handle None values before calling methods
- Verify parameter types before operations
- Use defensive checks in user-facing functions
- Validate QuickResto API responses before processing

## Application Architecture

- Main bot logic in main.py (includes schedulers)
- Handlers in handlers/ directory
- Services in services/ directory
- Keyboards in keyboards/ directory
- Localizations in locales/ directory
- Database models and functions in services/database.py
- QuickResto API integration in services/quickresto_api.py
- Bonus system in services/bonus.py
- Birthday and bonus burn services in respective files

## Database Models

- RegisteredPersons: stores user info linking Telegram and QuickResto IDs
- StartPersons: tracks users who started the bot
- GiftWheelSpins: tracks wheel of fortune game results
- MarketingMessages: tracks message broadcasts
- PromoCodes: manages promotional codes
- Events: handles events and notifications
- ClientLevels: defines customer levels and benefits
- Consents: manages privacy consent

## FSM States

- Use FSM for multi-step user interactions
- Define states in states/user_states.py
- Clear states after completion
- Provide clear back navigation options
- Handle state cancellation gracefully

## Localization

- Use Fluent localization system
- Store translations in locales/ru.ftl
- Use t() function for translation
- Maintain consistent terminology
- Include fallback translations

## Event Handling

- Use callback queries for menu interactions
- Handle user cancellations gracefully
- Validate user permissions (admin vs regular users)
- Provide appropriate feedback messages
- Manage state to prevent duplicate actions