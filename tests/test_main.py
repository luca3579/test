import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from app.main import app
from app.database import Base
import io
import zipfile
import os
import time

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    """建立測試資料庫測試後刪除"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def create_test_zip(files=None):
    """建立測試用的 ZIP 文件"""
    if files is None:
        files = {"A.txt": "Test content for A", "B.txt": "Test content for B"}
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, content in files.items():
            zip_file.writestr(file_name, content)
    return zip_buffer.getvalue()


def test_create_user(test_db):
    """建立建用戶功能"""
    response = client.post(
        "/users/",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


def test_create_duplicate_user(test_db):
    """測試重複用戶"""
    response = client.post(
        "/users/",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 400
    assert "用戶名已被註冊" in response.json()["detail"]


def test_login(test_db):
    """測試登錄功能"""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(test_db):
    """測試錯誤密碼登錄"""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "帳號或密碼不正確" in response.json()["detail"]


def test_upload_file(test_db):
    """測試上傳功能"""
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    zip_content = create_test_zip()
    response = client.post(
        "/uploadfile/",
        files={"file": ("test.zip", zip_content, "application/zip")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.zip"
    assert data["status"] == "待處理"


def test_get_uploads(test_db):
    """測試上傳記錄功能"""
    # 首先上傳一個文件
    test_upload_file(test_db)

    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/uploads/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["filename"] == "test.zip"


def test_upload_invalid_file(test_db):
    """測試上傳無效文件"""
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # 建立一個無效的 ZIP 文件
    invalid_zip_content = create_test_zip({"C.txt": "Invalid content"})

    response = client.post(
        "/uploadfile/",
        files={"file": ("invalid.zip", invalid_zip_content, "application/zip")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200  # 上傳成功，但處理失敗
    data = response.json()
    assert data["status"] == "待處理"  # 初始狀態為待處理

    time.sleep(1)  # 等待1秒，確保後台任務有時間執行

    # 檢查上傳記錄的狀態
    response = client.get(
        "/uploads/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[-1]["filename"] == "invalid.zip"
    assert data[-1]["status"] == "處理失敗"


def test_unauthorized_access(test_db):
    """測試未授權"""
    response = client.get("/uploads/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


# 清理
@pytest.fixture(autouse=True)
def run_around_tests():
    # 在每個測試之前執行
    yield
    # 在每個測試之後執行
    # 清理上傳的文件
    upload_dir = "files"
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            os.remove(os.path.join(upload_dir, file))


if __name__ == "__main__":
    pytest.main([__file__])