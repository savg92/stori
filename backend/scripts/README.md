# Backend Utility Scripts

This directory contains utility scripts for database management, authentication setup, and testing.

## Directory Structure

### 📁 `database/`

Database setup, population, and analysis scripts.

- **`auto_schema_setup.py`** - Automated database schema setup (alternative to manual SQL execution)
- **`check_database.py`** - Check current database content and verify data integrity
- **`analyze_user_data.py`** - Analyze transaction distribution and user data statistics
- **`sync_database_emails.py`** - Sync user emails between database and authentication system

### 📁 `auth/`

Authentication and user management scripts.

- **`create_auth_users.py`** - Create Supabase authentication users for testing (corresponds to database profiles)
- **`confirm_emails.py`** - Confirm user email addresses via Supabase admin API

### 📁 `testing/`

Testing and validation scripts.

- **`test_edge_cases.py`** - Test edge case handling in database setup and validation logic

## Usage

### Database Setup Workflow

1. **Schema Setup**: Run `schema.sql` in Supabase SQL Editor OR use `database/auto_schema_setup.py`
2. **Data Population**: Run `setup_database.py` (in root) to populate with mock data
3. **Auth Users**: Run `auth/create_auth_users.py` to create test authentication users
4. **Verification**: Run `database/check_database.py` to verify setup

### Development Utilities

- **Data Analysis**: Use `database/analyze_user_data.py` to understand data distribution
- **Email Sync**: Use `database/sync_database_emails.py` if emails get out of sync
- **Testing**: Run `testing/test_edge_cases.py` to validate data processing logic

## Environment Requirements

All scripts require:

- `.env` file with Supabase credentials
- `uv` Python environment with dependencies installed

## Running Scripts

```bash
# From backend directory
uv run python scripts/database/check_database.py
uv run python scripts/auth/create_auth_users.py
uv run python scripts/testing/test_edge_cases.py
```

## Notes

- These scripts are for development, testing, and maintenance
- Main application functionality is in `src/` directory
- `setup_database.py` (in root) is the primary database setup script
- `test_jwt_auth.py` (in root) is for active authentication testing
