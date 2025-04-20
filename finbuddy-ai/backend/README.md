# FinBuddy AI Backend

This is the backend server for FinBuddy AI, built with FastAPI and PostgreSQL.

## Prerequisites

- Python 3.x
- PostgreSQL

## Setup

1. Install PostgreSQL if you haven't already:
```bash
brew install postgresql@14
```

2. Start the PostgreSQL service:
```bash
brew services start postgresql@14
```

3. Create the database and user:
```bash
createdb finbuddy
createuser -s postgres
psql -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

4. Create a `.env` file in the backend directory with the following content:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/finbuddy
SECRET_KEY=your_secret_key_here  # Replace with a secure secret key
```

5. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

To start the backend server:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`. The `--reload` flag enables auto-reload on code changes, which is useful during development.

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Database Structure

The application uses three main tables:
- users: Stores user information and authentication details
- bank_accounts: Stores bank account information
- transactions: Stores transaction history

The tables will be automatically created when you first run the server.

## Development Notes

- The server includes CORS middleware configured for `http://localhost:3000` (frontend)
- SSL is disabled for local development
- Mock bank data is automatically generated for new users 