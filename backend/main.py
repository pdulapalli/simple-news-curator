from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from database import init_database
from recommendation_engine import RecommendationEngine

load_dotenv()


# Initialize recommendation engine
recommendation_engine = RecommendationEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_database()
    yield


app = FastAPI(title="News Curator API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ReactionRequest(BaseModel):
    reaction: str


@app.get("/")
async def root():
    return {"message": "News Curator API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/articles/recommended")
async def get_recommended_articles(limit: int = 20):
    """Get personalized article recommendations."""
    try:
        articles = recommendation_engine.get_recommendations(limit=limit)
        return {"articles": articles, "count": len(articles)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch recommendations: {str(e)}"
        )


@app.post("/articles/{article_id}/reaction")
async def submit_reaction(article_id: str, reaction_data: ReactionRequest):
    """Submit user reaction (like/dislike) for an article."""
    try:
        if reaction_data.reaction not in ["like", "dislike"]:
            raise HTTPException(
                status_code=400, detail="Reaction must be 'like' or 'dislike'"
            )

        recommendation_engine.process_user_feedback(article_id, reaction_data.reaction)
        return {"message": "Reaction recorded successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to record reaction: {str(e)}"
        )


@app.get("/preferences")
async def get_user_preferences():
    """Get current user preferences for debugging."""
    try:
        profile = recommendation_engine.get_user_profile()
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get preferences: {str(e)}"
        )


@app.post("/preferences/reset")
async def reset_preferences():
    """Reset all user preferences and reactions."""
    try:
        recommendation_engine.reset_user_data()
        return {"message": "User preferences reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reset preferences: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
