import sqlite3
import pandas as pd
import json

DB_NAME = "analytics.db"

def run_etl():
    conn = sqlite3.connect(DB_NAME)
    
    # 1. Read raw events
    df = pd.read_sql_query("SELECT * FROM raw_events", conn)
    
    if df.empty:
        print("No raw events found.")
        return
        
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['session_id', 'timestamp'])
    
    # 2. Sessionization
    # Group by session_id to calculate duration and paths
    
    def process_session(group):
        start_time = group['timestamp'].min()
        end_time = group['timestamp'].max()
        duration_seconds = (end_time - start_time).total_seconds()
        
        # Extract page views for funnel path
        page_views = group[group['event_type'] == 'page_view']
        
        # Extract path from URL hash or root
        def get_page_name(url):
            if "#" in url:
                return url.split("#")[1].title()
            return "Home"
            
        path = " > ".join(page_views['url'].apply(get_page_name).tolist())
        
        # Find entry and exit pages
        entry_page = get_page_name(page_views['url'].iloc[0]) if not page_views.empty else "Unknown"
        exit_page = get_page_name(page_views['url'].iloc[-1]) if not page_views.empty else "Unknown"
        
        return pd.Series({
            'user_id': group['user_id'].iloc[0],
            'start_time': start_time,
            'duration_seconds': duration_seconds,
            'events_count': len(group),
            'page_views': len(page_views),
            'entry_page': entry_page,
            'exit_page': exit_page,
            'path': path,
            'bounced': 1 if len(page_views) <= 1 else 0
        })

    sessions_df = df.groupby('session_id').apply(process_session).reset_index()
    
    # 3. Write processed sessions back to DB
    sessions_df.to_sql('processed_sessions', conn, if_exists='replace', index=False)
    
    # 4. Calculate Daily Metrics
    sessions_df['date'] = sessions_df['start_time'].dt.date
    daily_metrics = sessions_df.groupby('date').agg(
        total_sessions=('session_id', 'count'),
        avg_duration=('duration_seconds', 'mean'),
        bounce_rate=('bounced', 'mean'),
        total_page_views=('page_views', 'sum')
    ).reset_index()
    
    daily_metrics.to_sql('daily_metrics', conn, if_exists='replace', index=False)
    
    print(f"ETL completed. Processed {len(sessions_df)} sessions.")
    conn.close()

if __name__ == "__main__":
    run_etl()
