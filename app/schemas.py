# In telnovia-analytics-backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from .models import RoleEnum # Impor RoleEnum
from typing import Optional, Any, List, Dict

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class TeamMembershipOut(BaseModel):
    team_id: int
    role: RoleEnum

    class Config:
        from_attributes = True

class UserOut(UserBase):
    id: int
    memberships: List[TeamMembershipOut] = [] # <-- Tambahkan ini

    class Config:
        from_attributes = True

class NotebookBase(BaseModel):
    filename: str
    description: Optional[str] = None

class NotebookOut(NotebookBase):
    id: int
    is_public: bool
    shareable_token: Optional[str] = None
    team_id: int
    # health_report bisa kompleks, jadi Dict adalah pendekatan umum yang baik
    health_report: Optional[Dict[str, Any]] = None

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
class DbConnectionBase(BaseModel):
    name: str
    host: str
    port: int
    username: str
    dbname: str

class DbConnectionCreate(DbConnectionBase):
    password: str

class DbConnectionOut(DbConnectionBase):
    id: int
    db_type: str
    team_id: int

    class Config:
        from_attributes = True

class TeamMember(BaseModel):
    email: EmailStr
    role: RoleEnum

    class Config:
        from_attributes = True

class TeamOut(BaseModel):
    id: int
    name: str
    members: List[TeamMember]

    class Config:
        from_attributes = True

class InviteRequest(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.viewer # Default role adalah Viewer