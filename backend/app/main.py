
import os
import logging

from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.database import initialize_database
from app.match_engine import MatchEngine
from app.schemas.requests import AskRequest
from app.services.assistant import ask_matchbro


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("matchbro")


@asynccontextmanager
async def lifespan(app: FastAPI):

    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is missing.")

    initialize_database()

    app.state.match_engine = MatchEngine()

    logger.info("MatchBro initialized.")

    yield


app = FastAPI(
    title="MatchBro AI",
    description="Voice-first AI cricket companion",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():

    return {
        "message": "Welcome to MatchBro AI",
        "status": "running"
    }


@app.get("/api/health")
def health():

    return {
        "status": "healthy",
        "service": "MatchBro AI"
    }


@app.get("/api/match/state")
def match_state():

    engine = app.state.match_engine

    return engine.get_state()


@app.post("/api/match/next-ball")
def next_ball():

    engine = app.state.match_engine

    result = engine.next_ball()

    return result


@app.post("/api/match/reset")
def reset_match():

    engine = app.state.match_engine

    engine.reset()

    return {
        "message": "Demo match reset.",
        "state": engine.get_state()
    }


@app.get("/api/match/timeline")
def match_timeline():

    from app.database import get_all_events

    return {
        "events": get_all_events()
    }


@app.post("/api/assistant/ask")
async def assistant(request: AskRequest):

    engine = app.state.match_engine

    state = engine.get_state()

    try:

        result = await ask_matchbro(
            question=request.question,
            match_state=state
        )

        return result

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception:

        logger.exception("MatchBro assistant failed")

        raise HTTPException(
            status_code=502,
            detail="MatchBro AI service is temporarily unavailable."
        )
