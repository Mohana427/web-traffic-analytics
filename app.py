import sqlite3
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Enable CORS for the sample website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "analytics.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS raw_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_id TEXT,
            event_type TEXT,
            url TEXT,
            timestamp DATETIME,
            metadata TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Event(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    event_type: str
    url: str
    timestamp: str
    metadata: Optional[dict] = None

@app.post("/track")
async def track_event(event: Event):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Store event in the database
    c.execute('''
        INSERT INTO raw_events (session_id, user_id, event_type, url, timestamp, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        event.session_id,
        event.user_id,
        event.event_type,
        event.url,
        event.timestamp,
        json.dumps(event.metadata) if event.metadata else None
    ))
    
    conn.commit()
    conn.close()
    
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
