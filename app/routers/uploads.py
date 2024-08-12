from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.deps import get_db, get_current_user
from app.security import encrypt_file, decrypt_file
from app.utils import AppException, handle_error
import zipfile
import os
import logging

router = APIRouter()

UPLOAD_DIRECTORY = "files"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

async def process_file(file_path: str, db: Session, user_id: int):
    """
    異步處理上傳的文件
    """
    try:
        # 解密
        decrypt_file(file_path)   
        # 驗證
        validate_file(file_path)              
        # 重新加密
        encrypt_file(file_path)
        # 更新狀態
        crud.update_upload_status(db, os.path.basename(file_path), user_id, "已處理")
    except Exception as e:
        logging.error(f"處理文件 {file_path} 時出錯: {str(e)}")
        crud.update_upload_status(db, os.path.basename(file_path), user_id, "處理失敗")

def validate_file(file_path: str):
    """
    驗證上傳的文件
    """
    if not zipfile.is_zipfile(file_path):
        raise ValueError("文件必須是 ZIP ")

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        required_files = ["A.txt", "B.txt"]
        for req_file in required_files:
            if req_file not in file_list:
                raise ValueError(f"缺少: {req_file}")


@router.post("/uploadfile/", response_model=schemas.Upload)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    try:
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # 創建上傳記錄
        upload = crud.create_upload(db=db, filename=file.filename, user_id=current_user.id, status="待處理")

        # 在後台任務中處理文件
        if background_tasks:
            background_tasks.add_task(process_file, file_location, db, current_user.id)

        return upload
    except Exception as e:
        logging.error(f"上傳文件時出錯: {str(e)}")
        raise AppException(status_code=400, detail=f"上傳文件時出錯: {str(e)}")

@router.get("/uploads/", response_model=list[schemas.Upload])
def get_uploads(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    獲取上傳記錄
    """
    uploads = crud.get_uploads(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return uploads