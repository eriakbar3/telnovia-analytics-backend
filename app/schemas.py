# In telnovia-analytics-backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, Any, List, Dict

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

class NotebookBase(BaseModel):
    filename: str

class NotebookOut(NotebookBase):
    id: int

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    query: str
    notebookId: Optional[str] = None # Menjadi opsional

class QueryResponse(BaseModel):
    reply: str
    
    class Config:
        from_attributes = True # Dulu orm_mode = True

# Skema baru untuk slide individual
class SlideBase(BaseModel):
    id: str
    type: str # 'title', 'table', 'markdown', etc.
    title: str
    content: Any

# Skema untuk respons pratinjau presentasi
class PresentationPreviewResponse(BaseModel):
    slides: List[SlideBase]
