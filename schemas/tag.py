from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    
    model_config = {
        "from_attributes": True  # 更新为 Pydantic v2 语法
    } 