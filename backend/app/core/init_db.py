from app.core.database import Base, engine
from app.models.user import User
from app.models.file import UploadedFile

def init_db():
    """Drop all tables and recreate them"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 