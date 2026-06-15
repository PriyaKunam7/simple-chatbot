# create_tables.py

from app.db_connection import engine, Base
import app.models  # important: ensures models are registered

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ PostgreSQL tables created successfully!")