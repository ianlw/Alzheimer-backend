from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# ANTES: from .. import crud, schemas, auth, models
# ANTES: from ..database import get_db
# AHORA:
import crud
import schemas
import auth
import models
from database import get_db

router = APIRouter()

@router.post("/register/", response_model=schemas.Usuario)
def register_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_nombre_usuario(db, nombre_usuario=usuario.nombre_usuario)
    if db_usuario:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    return crud.create_usuario(db=db, usuario=usuario)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = crud.get_usuario_by_nombre_usuario(db, nombre_usuario=form_data.username)
    if not usuario or not auth.verify_password(form_data.password, usuario.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": usuario.nombre_usuario}
    )
    return {"access_token": access_token, "token_type": "bearer"}
