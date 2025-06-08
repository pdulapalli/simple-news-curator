# simple-news-curator

A personalized news curator that learns from your preferences and delivers tailored article recommendations.

## Prerequisites

ℹ️ NOTE: This setup is only tested on macOS.

Install Homebrew using [these instructions](https://brew.sh/)

### Python

Any version at or above Python 3.11 should work. Install it like so:

```shell
brew install python
```

### uv

Also install the Python package manager `uv` using the [official instructions](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer).

### Node.js

Install Node.js (version 18 or higher):

```shell
brew install node
```

## Setup

### Backend Setup

Navigate to the backend directory:

```shell
cd backend
```

Install Python dependencies:

```shell
uv sync
```

### Frontend Setup

Navigate to the frontend directory:

```shell
cd frontend
```

Install Node.js dependencies:

```shell
npm install
```

### Environment Variables

In the backend directory, create a `.env` file with your TheNewsAPI key:

```shell
THENEWSAPI_KEY=your_api_key_here
```

Get your free API key from [TheNewsAPI.com](https://www.thenewsapi.com/).

## Running

### Start the Backend

In the backend directory:

```shell
uv run main.py
```

The backend will start on `http://localhost:8000`

### Start the Frontend

In a separate terminal, navigate to the frontend directory:

```shell
npm run dev
```

The frontend will start on `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Click on article cards to read full articles
3. Use the 👍 Like and 👎 Dislike buttons to train your preferences
4. The system learns from your reactions and personalizes future recommendations

The app uses a 70/30 strategy: 70% personalized content based on your preferences, 30% general trending news.

## Database

The app uses SQLite for local storage. The database file (`news_curator.db`) will be created automatically in the backend directory when you first run the application.