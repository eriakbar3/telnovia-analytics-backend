from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, models
from app.database import get_db
from app.auth.oauth2 import get_current_user

def get_user_role_in_team(team_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)) -> models.RoleEnum:
    membership = crud.get_user_membership_in_team(db, user_id=current_user.id, team_id=team_id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda bukan anggota tim ini."
        )
    return membership.role

class RoleChecker:
    def __init__(self, allowed_roles: list[models.RoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, role: models.RoleEnum = Depends(get_user_role_in_team)):
        if role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Memerlukan salah satu dari peran berikut: {[r.value for r in self.allowed_roles]}"
            )