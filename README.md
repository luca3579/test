# 供應商測試數據 API

本專案是基於 FastAPI 的 API 服務，用於處理供應商測試數據。

## 前置要求

- Python 3.9+
- Docker 和 Docker Compose

## 本地設置

1. Clone儲存庫：
   ```
   git clone <儲存庫網址>
   cd <專案目錄>
   ```

2. 創立虛擬環境並啟動：
   ```
   python -m venv venv
   source venv/bin/activate  # Windows 使用 `venv\Scripts\activate`
   ```

3. 安裝依賴：
   ```
   pip install -r requirements.txt
   ```

4. 設置環境變量：
   在專案根目錄創建 `.env` 文件並添加以下內容：
   ```
   SECRET_KEY=你的密鑰
   DATABASE_URL=sqlite:///./test.db
   ```

5. 運行應用程序：
   ```
   uvicorn app.main:app --reload
   ```

   API 在 `http://localhost:8000` 

## 使用 Docker 運行

1. 建立 Docker 容器：
   ```
   docker-compose up --build
   ```

   API 將在 `http://localhost:8000` 可用

## 運行測試

使用 pytest 運行測試：
```
pytest
```

## API 文檔

執行後，以下地址訪問 API ：
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

## 專案結構

- `app/`：
  - `main.py`：FastAPI 應用程式
  - `models.py`：SQLAlchemy 模型
  - `schemas.py`：Pydantic 模型
  - `crud.py`：資料庫操作
  - `deps.py`：依賴
  - `auth.py`：身份驗證相關
  - `uploads.py`：上傳相關
- `tests/`：測試
- `Dockerfile` 和 `docker-compose.yml`：Docker 配置

## 使用說明

1. 註冊新用戶：
   發送 POST 請求到 `/users/` ，包含帳號和密碼。

2. 獲取訪問token：
   發送 POST 請求到 `/token` ，提供帳號和密碼。

3. 上傳文件：
   使用獲得的訪問token，發送 POST 請求到 `/uploadfile/` ，上傳 ZIP 。

4. 查詢上傳記錄：
   使用訪問token，發送 GET 請求到 `/uploads/` 。

## 注意事項

- 確保上傳的 ZIP 文件包含必需的 A.txt 和 B.txt 文件。
- 文件大小限制為 50MB。
- 所有請求（除了註冊和登錄）都需要在請求頭中包含有效的 JWT 令牌。

如有任何問題或需要進一步的協助，請聯繫專案維護者。
