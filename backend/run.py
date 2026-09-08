"""Entrypoint script to launch ExpiryAware backend server on port 8000."""
import sys
import uvicorn
from app.database import init_db

if __name__ == "__main__":
    print("Initializing ExpiryAware database and seeding baseline if empty...")
    init_db(seed_if_empty=True)
    print("Starting ExpiryAware FastAPI server on http://localhost:8000 ...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
