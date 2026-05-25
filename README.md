# Web Traffic Analytics

An end-to-end data pipeline project that ingests, processes, and visualizes website user behavior. The core goal is to track user events, pinpoint drop-off zones in a conversion funnel, and optimize the user journey for higher engagement.

## Features

- **Web SDK (`tracker.js`)**: A lightweight JavaScript library to capture page views, clicks, and session information.
- **Ingestion API (`app.py`)**: A FastAPI backend that receives real-time JSON payloads from the web tracker and stores them.
- **Storage (`analytics.db`)**: Local SQLite database simulating a cloud data lake/warehouse.
- **ETL Processing (`etl.py`)**: A Pandas script that sessionizes user actions, calculates session durations, bounce rates, and extracts user navigation paths.
- **Mock Data Generator (`mock_data.py`)**: Generates thousands of realistic user journeys and drop-off events to test the pipeline.
- **Analytics Dashboard (`dashboard.py`)**: A professional, premium dark-mode Streamlit dashboard with interactive Plotly charts highlighting key metrics, traffic trends, and funnel drop-offs.

## Architecture

`[Web SDK] ➔ [FastAPI Ingestion] ➔ [SQLite Storage] ➔ [Pandas ETL] ➔ [Streamlit Dashboard]`

## Getting Started

### Prerequisites
Make sure you have Python installed. Install the dependencies using:
```bash
pip install -r requirements.txt
```

### Running the Pipeline

1. **Start the API Server** (to receive tracking events):
   ```bash
   python app.py
   ```

2. **Generate Mock Data** (Optional, to populate the dashboard instantly):
   ```bash
   python mock_data.py
   ```
   *(Ensure the `analytics.db` is initialized first, which happens automatically when you run `app.py` for the first time).*

3. **Run the ETL Script** (to process raw events into sessions and metrics):
   ```bash
   python etl.py
   ```

4. **Launch the Dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

### Simulating Live Traffic
Open `sample_website.html` in your web browser. Click around the navigation links and "Add to Cart" buttons. The `tracker.js` script will automatically send these events to the FastAPI server running on `localhost:8000`. Re-run `etl.py` to process these new events, then refresh your dashboard!

## Technologies Used
- Python, JavaScript, HTML/CSS
- FastAPI (Backend Ingestion)
- Pandas (ETL Data Processing)
- Streamlit & Plotly (Data Visualization & UI/UX)
- SQLite (Database)
