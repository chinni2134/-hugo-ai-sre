# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database.neo4j import neo4j_connection

app = FastAPI(
    title="HUGO AI",
    version="0.1.0",
    description="AI-native SRE platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    print("Starting HUGO...")

    try:
        neo4j_connection.verify()
        print("PostgreSQL connected.")
        print("Neo4j connected.")
    except Exception as e:
        print(f"Neo4j connection failed: {e}")

    print("HUGO Phase 1 started.")


@app.get("/")
def root():
    return {
        "name": "HUGO AI",
        "version": "0.1.0",
        "phase": 1,
        "status": "running",
    }


app.include_router(router)
