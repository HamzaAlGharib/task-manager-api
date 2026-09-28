from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+psycopg://postgres:NMHSA$7205@localhost:5432/task_manager"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)