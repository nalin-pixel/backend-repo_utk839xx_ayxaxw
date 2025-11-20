import os
import time
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Search as SearchSchema, Match as MatchSchema

app = FastAPI(title="Veriqo API", description="Reverse image search service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchResponse(BaseModel):
    id: str
    status: str
    duration_ms: int
    platforms: List[str]
    matches: List[MatchSchema]
    error: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "Veriqo backend running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from Veriqo API"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.post("/api/search/upload", response_model=SearchResponse)
async def reverse_image_search_upload(request: Request, file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file")

    start = time.time()

    # Simulate platform checks and matches
    platforms = ["Twitter", "Instagram", "Facebook", "Reddit", "LinkedIn"]

    # Fake matching logic: random-like deterministic based on filename length
    name_len = len(file.filename or "img")
    potential = [
        MatchSchema(platform="Twitter", url="https://twitter.com/example/status/123", similarity=92,
                    thumbnail="https://picsum.photos/seed/tw/120/80"),
        MatchSchema(platform="Reddit", url="https://reddit.com/r/example/comments/xyz", similarity=87,
                    thumbnail="https://picsum.photos/seed/rd/120/80"),
        MatchSchema(platform="Instagram", url="https://instagram.com/p/abc123", similarity=78,
                    thumbnail="https://picsum.photos/seed/ig/120/80"),
    ]

    matches: List[MatchSchema] = []
    if name_len % 2 == 0:
        matches.append(potential[0])
    if name_len % 3 == 0:
        matches.append(potential[1])
    if name_len % 5 == 0 or not matches:
        matches.append(potential[2])

    duration_ms = int((time.time() - start) * 1000)

    search_doc = SearchSchema(
        query_type="upload",
        filename=file.filename,
        mime_type=file.content_type,
        size=None,
        platforms=platforms,
        matches=matches,
        status="completed",
        duration_ms=duration_ms,
        error=None,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    try:
        inserted_id = create_document("search", search_doc)
    except Exception as e:
        # Database failure should not break the API response, but we include error
        inserted_id = "-1"
        search_doc.error = str(e)

    return SearchResponse(
        id=inserted_id,
        status=search_doc.status,
        duration_ms=search_doc.duration_ms,
        platforms=search_doc.platforms,
        matches=search_doc.matches,
        error=search_doc.error,
    )


class SearchRecord(BaseModel):
    id: str
    data: SearchSchema


@app.get("/api/search/recent")
def recent_searches(limit: int = 5):
    try:
        docs = get_documents("search", limit=limit)
        # Convert ObjectId to string for client consumption
        sanitized = []
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
            sanitized.append(d)
        return {"items": sanitized}
    except Exception:
        # If DB not available, return empty list gracefully
        return {"items": []}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
