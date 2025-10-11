# Contributing to Youth Hockey Development Tracker

Thank you for your interest in contributing to the Youth Hockey Development Tracker! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a positive and collaborative environment

## Getting Started

### Setting Up Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YouthHockeyTracker.git
   cd YouthHockeyTracker
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up pre-commit hooks** (recommended)
   ```bash
   uv add --dev pre-commit
   uv run pre-commit install
   ```

4. **Configure your environment**
   - Copy `.env.example` to `.env` (if available)
   - Update database and email settings
   - Create a test database for running tests

5. **Run the application**
   ```bash
   # Terminal 1: Flask backend
   uv run python app.py
   
   # Terminal 2: Streamlit frontend
   uv run streamlit run main.py
   ```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation changes
- `refactor/improvement-name` - Code refactoring

### Creating a Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### Making Changes

1. Write your code following our [coding standards](#coding-standards)
2. Add tests for new functionality
3. Update documentation if needed
4. Run tests and linting locally
5. Commit your changes with clear messages

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Formatting**: Use Black for automatic formatting
- **Imports**: Group and sort imports logically
  ```python
  # Standard library
  import os
  from datetime import datetime
  
  # Third-party
  import pandas as pd
  import streamlit as st
  
  # Local
  from database.models import Player
  from utils.type_converter import to_int
  ```

### Code Formatting

**Before committing, always run:**

```bash
# Format code with Black
uv run black .

# Check for lint issues
flake8 . --exclude=.venv,migrations --count --statistics
```

### Type Hints

Add type hints to all new functions:

```python
from typing import Optional, List, Dict
import pandas as pd

def get_players_by_age(age: int, user_id: Optional[int] = None) -> pd.DataFrame:
    """Get players filtered by age and optionally by user.
    
    Args:
        age: Player age to filter by
        user_id: Optional user ID to filter players
        
    Returns:
        DataFrame containing matching players
    """
    # Implementation
    pass
```

### Database Operations

**Always use type converters** before database operations:

```python
from utils.type_converter import to_int, to_float

# Good
player.age = to_int(age_value)
player.skating_speed = to_float(speed_value)
db.session.add(player)
db.session.commit()

# Bad - may cause numpy type errors
player.age = age_value  # Could be numpy.int64
```

### Error Handling

Wrap database operations in try-except blocks:

```python
try:
    db.session.add(player)
    db.session.commit()
    return True
except Exception as e:
    db.session.rollback()
    st.error(f"Error saving player: {str(e)}")
    return False
```

### Component Structure

Streamlit components should follow this pattern:

```python
def display_component_name(param1: Type, param2: Type) -> None:
    """Component description.
    
    Args:
        param1: Description
        param2: Description
    """
    st.subheader("Component Title")
    
    # Component logic here
    
    # Use session state for persistence
    if 'component_state' not in st.session_state:
        st.session_state.component_state = default_value
```

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_function_name_with_condition_returns_expected()`

**Example test structure:**

```python
import pytest
from database.models import Player

class TestPlayerModel:
    """Tests for the Player model."""
    
    def test_create_player_with_valid_data(self, db_session, sample_user):
        """Test creating a player with valid data."""
        player = Player(
            name="Test Player",
            age=12,
            position="Forward",
            user_id=sample_user.id
        )
        db_session.add(player)
        db_session.commit()
        
        assert player.id is not None
        assert player.age_group == "U12"
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_models.py

# Run specific test
uv run pytest tests/test_models.py::TestPlayerModel::test_create_player_with_valid_data
```

### Test Coverage

- Aim for >80% code coverage for new code
- Write tests for:
  - All new functions and methods
  - Edge cases and error conditions
  - Database operations
  - Type conversions

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(player-profile): add export to PDF functionality

fix(auth): resolve token expiration issue for remember me

docs(readme): update installation instructions for uv

test(utils): add tests for type converter edge cases

refactor(team-dashboard): optimize player statistics query
```

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
   ```bash
   uv run pytest
   ```

2. **Run code formatting**
   ```bash
   uv run black .
   ```

3. **Check for lint issues**
   ```bash
   flake8 . --exclude=.venv,migrations
   ```

4. **Update documentation** if needed
   - Update README.md for new features
   - Add docstrings to new functions
   - Update CHANGELOG.md (if exists)

5. **Rebase on main**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

### Creating a Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changed and why
   - Include screenshots for UI changes
   - List any breaking changes

### PR Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #(issue number)

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. At least one maintainer approval required
2. All CI checks must pass
3. No merge conflicts with main
4. Code coverage should not decrease

### After Merge

1. Delete your feature branch
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. Update your local main
   ```bash
   git checkout main
   git pull origin main
   ```

## Common Development Tasks

### Adding a New Model

1. Create model in `database/models.py`
2. Create migration: `uv run alembic revision --autogenerate -m "Add ModelName"`
3. Review and apply migration: `uv run alembic upgrade head`
4. Add tests in `tests/test_models.py`

### Adding a New Component

1. Create file in `components/your_component.py`
2. Import in `main.py`
3. Add navigation menu item
4. Add tests if applicable
5. Update documentation

### Adding a New Utility Function

1. Add to appropriate file in `utils/`
2. Add type hints and docstring
3. Add tests in `tests/test_utils.py`
4. Use type converters for database values

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with reproduction steps
- **Features**: Open a GitHub Issue with detailed requirements
- **Chat**: Contact maintainers directly

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation

Thank you for contributing! 🏒
