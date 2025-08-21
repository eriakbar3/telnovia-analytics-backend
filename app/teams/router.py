from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, models
from app.database import get_db
from app.auth.oauth2 import get_current_user
from app.core.permissions import RoleChecker

router = APIRouter(
    prefix="/api/v1/teams",
    tags=['Teams']
)

# Inisialisasi pengecek peran
admin_only = RoleChecker([models.RoleEnum.admin])
any_member = RoleChecker([models.RoleEnum.admin, models.RoleEnum.editor, models.RoleEnum.viewer])


@router.get("/{team_id}", response_model=schemas.TeamOut, dependencies=[Depends(any_member)])
def get_team_details(team_id: int, db: Session = Depends(get_db)):
    # Verifikasi keanggotaan sekarang ditangani oleh RoleChecker dalam dependencies.
    team = crud.get_team_by_id(db, team_id=team_id)
    if not team:
        # Secara teknis, RoleChecker sudah menangani kasus tim tidak ada,
        # tapi ini adalah fallback yang baik.
        raise HTTPException(status_code=404, detail="Tim tidak ditemukan.")
    
    # Mengubah format members agar sesuai dengan skema TeamMember
    # Ini bisa dipindahkan ke dalam fungsi CRUD jika ingin lebih rapi.
    members_with_details = [{"email": mem.user.email, "role": mem.role} for mem in team.members]
    
    return {"id": team.id, "name": team.name, "members": members_with_details}

@router.post("/{team_id}/invite", dependencies=[Depends(admin_only)])
def invite_user_to_team(
    team_id: int, 
    invite_data: schemas.InviteRequest,
    db: Session = Depends(get_db)
):
    # Verifikasi bahwa `current_user` adalah Admin dari tim sekarang ditangani oleh RoleChecker.
    
    invited_user = crud.get_user_by_email(db, email=invite_data.email)
    if not invited_user:
        # Jika user belum ada, kita bisa kirim email undangan atau buat user non-aktif
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan di sistem.")

    # Cek apakah user sudah menjadi anggota tim
    existing_membership = crud.get_team_membership(db, user_id=invited_user.id, team_id=team_id)
    if existing_membership:
        raise HTTPException(status_code=400, detail=f"Pengguna {invite_data.email} sudah menjadi anggota tim.")

    # Tambahkan user yang sudah ada ke dalam tim
    crud.add_user_to_team(db, team_id=team_id, user_id=invited_user.id, role=invite_data.role)
    
    return {"message": f"Pengguna {invite_data.email} berhasil diundang ke tim sebagai {invite_data.role.value}."}