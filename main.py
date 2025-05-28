import pandas as pd
import numpy as np
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import pickle

# Load the trained model (saved dataframe)
with open("actor_model.pkl", "rb") as f:
    df = pickle.load(f)

# Initialize FastAPI app
app = FastAPI(title="Actor Prediction API", description="Explore ML Actor Prediction Model")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Allow frontend requests from this origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the "static" directory to serve CSS, JS, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 for templates
templates = Jinja2Templates(directory="templates")

# Define available genres
genre_columns = [
    'Drama', 'Horror', 'Mystery', 'Comedy', 'Crime', 'Biography', 'Romance', 'Musical',
    'History', 'Action', 'Sport', 'Thriller', 'Family', 'Adventure', 'Sci-Fi', 'Music',
    'Documentary', 'Fantasy', 'War', 'Animation', 'Western', 'News'
]

# Convert necessary columns to numeric
df['height'] = pd.to_numeric(df['height'], errors='coerce')
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
df['Previous Movies'] = pd.to_numeric(df['Previous Movies'], errors='coerce')
df['Previous Movies'] = df['Previous Movies'].fillna(0)

# Home Route - Serves the index.html file
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API Documentation route
@app.get("/api")
def api_docs():
    return {"docs": "/docs", "redoc": "/redoc", "predict_endpoint": "/predict"}

# Actor Prediction Route
@app.get("/predict")
def predict_best_actor(
    genres: str = Query(..., description="Enter comma-separated genres (e.g., Action, Thriller)"),
    min_height: float = Query(1.50, description="Minimum actor height in meters"),
    max_height: float = Query(2.00, description="Maximum actor height in meters"),
    min_age: int = Query(20, description="Minimum actor age"),
    max_age: int = Query(60, description="Maximum actor age"),
):
    print(f"Received request: genres={genres}, min_height={min_height}, max_height={max_height}, min_age={min_age}, max_age={max_age}")

    selected_genres = [g.strip().capitalize() for g in genres.split(",") if g.strip().capitalize() in genre_columns]
    
    if not selected_genres:
        return {"error": "Invalid genres. Please select from: " + ", ".join(genre_columns)}

    df['Genre_Match_Score'] = df[selected_genres].mean(axis=1) * 2

    df['Actor_Score'] = (
        df['Genre_Match_Score'] * 2 +  
        df['Avg_Rating'] * 1.5 +       
        df['Previous Movies'] * 1.2 +  
        df['Awards'] * 1.5             
    )

    filtered_df = df[
        (df['height'] >= min_height) & (df['height'] <= max_height) &
        (df['Age'] >= min_age) & (df['Age'] <= max_age)
    ]

    if filtered_df.empty:
        filtered_df = df.sort_values(by=['Actor_Score'], ascending=False).head(5)

    top_actors = filtered_df[['Actor', 'Actor_Score', 'Genre_Match_Score', 'Avg_Rating', 'Previous Movies', 'Awards', 'height', 'Age']].sort_values(by=['Actor_Score'], ascending=False).head(5).to_dict(orient="records")

    return {"top_actors": top_actors}
