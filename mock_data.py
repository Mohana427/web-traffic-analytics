import sqlite3
import random
from datetime import datetime, timedelta
import uuid

DB_NAME = "analytics.db"

# Sample data
pages = ["Home", "Products", "Cart", "Checkout"]
urls = {
    "Home": "http://localhost:8000/",
    "Products": "http://localhost:8000/#products",
    "Cart": "http://localhost:8000/#cart",
    "Checkout": "http://localhost:8000/#checkout"
}

def generate_mock_data(num_sessions=1000, days_back=30):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    now = datetime.now()
    
    events = []
    
    for _ in range(num_sessions):
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        user_id = f"usr_{uuid.uuid4().hex[:8]}"
        
        # Random start time within the last N days
        start_time = now - timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        current_time = start_time
        
        # Define funnel drop-off probabilities
        # Home (100%) -> Products (70%) -> Cart (40%) -> Checkout (15%)
        funnel_stage = 0
        rand_val = random.random()
        
        if rand_val > 0.3: funnel_stage = 1
        if rand_val > 0.6: funnel_stage = 2
        if rand_val > 0.85: funnel_stage = 3
        
        # Generate events for the journey
        for i in range(funnel_stage + 1):
            page = pages[i]
            
            # Page view event
            events.append((
                session_id, user_id, "page_view", urls[page], current_time.isoformat(), '{"title": "Store - ' + page + '"}'
            ))
            
            # Add some time spent on page
            current_time += timedelta(seconds=random.randint(10, 120))
            
            # Optional click events
            if page == "Products" and random.random() > 0.5:
                events.append((
                    session_id, user_id, "click", urls[page], current_time.isoformat(), '{"element_type": "BUTTON", "element_text": "Add to Cart"}'
                ))
                current_time += timedelta(seconds=random.randint(2, 10))
                
    # Sort events by timestamp to simulate real data insertion order
    events.sort(key=lambda x: x[4])
    
    c.executemany('''
        INSERT INTO raw_events (session_id, user_id, event_type, url, timestamp, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', events)
    
    conn.commit()
    conn.close()
    
    print(f"Generated {len(events)} events for {num_sessions} sessions over {days_back} days.")

if __name__ == "__main__":
    generate_mock_data()
