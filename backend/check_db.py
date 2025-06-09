"""Check database tables."""
from sqlalchemy import text
from app.core.database_config import engine

def check_tables():
    """Check if required tables exist."""
    with engine.connect() as conn:
        # Get list of tables
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        
        # Check for required tables
        required_tables = ['users', 'uploaded_files', 'parsed_contents', 'quizzes', 'migrations']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
        else:
            print("All required tables exist!")
        
        # Print all tables
        print("\nAll tables in database:")
        for table in tables:
            print(f"- {table}")

if __name__ == "__main__":
    check_tables() 