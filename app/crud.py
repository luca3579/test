from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_upload(db: Session, filename: str, user_id: int, status: str):
    db_upload = models.Upload(filename=filename, user_id=user_id, status=status)
    db.add(db_upload)
    db.commit()
    db.refresh(db_upload)
    return db_upload


def get_uploads(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Upload).filter(models.Upload.user_id == user_id).offset(skip).limit(limit).all()


def update_upload_status(db: Session, filename: str, user_id: int, status: str):
    db_upload = db.query(models.Upload).filter(models.Upload.filename == filename, models.Upload.user_id == user_id).first()
    if db_upload:
        db_upload.status = status
        db.commit()
        db.refresh(db_upload)
    return db_upload