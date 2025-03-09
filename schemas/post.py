from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    content: str = Field(..., min_length=1, description="文章内容")

class PostCreate(PostBase):
    tags: Optional[List[int]] = Field(None, description="标签ID列表")

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文章标题")
    content: Optional[str] = Field(None, min_length=1, description="文章内容")
    tags: Optional[List[int]] = Field(None, description="标签ID列表")

class TagResponse(BaseModel):
    id: int
    name: str
    
    model_config = {
        "from_attributes": True
    }

class PostResponse(PostBase):
    id: int
    created_at: datetime
    author_id: int
    tags: List[TagResponse] = []
    
    model_config = {
        "from_attributes": True
    } 