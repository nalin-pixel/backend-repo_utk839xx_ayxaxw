"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Veriqo reverse image search schemas
class Match(BaseModel):
    platform: str = Field(..., description="Social platform name")
    url: str = Field(..., description="URL of the found image/post")
    similarity: int = Field(..., ge=0, le=100, description="Similarity score (0-100)")
    thumbnail: Optional[str] = Field(None, description="Optional thumbnail URL")

class Search(BaseModel):
    """
    Reverse image search record
    Collection name: "search"
    """
    query_type: str = Field(..., description="upload or url")
    filename: Optional[str] = Field(None, description="Original filename if uploaded")
    mime_type: Optional[str] = Field(None, description="MIME type of image")
    size: Optional[int] = Field(None, description="File size in bytes")
    platforms: List[str] = Field(default_factory=list, description="Platforms checked")
    matches: List[Match] = Field(default_factory=list, description="Matches found")
    status: str = Field("completed", description="Search status")
    duration_ms: int = Field(0, description="How long the search took in ms")
    error: Optional[str] = Field(None, description="Error message if any")
    ip: Optional[str] = Field(None, description="Requester IP")
    user_agent: Optional[str] = Field(None, description="Requester user agent")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
