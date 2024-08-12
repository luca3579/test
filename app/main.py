from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from starlette import status
from app import models
from app.database import engine
from app.routers import auth, uploads
from app.security import generate_key
import os
import logging
from app.utils import AppException

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 如果沒有密鑰文件，則生成一個
if not os.path.exists("secret.key"):
    generate_key()

# 創建所有數據庫表
models.Base.metadata.create_all(bind=engine)

# 創建 FastAPI 應用實例
app = FastAPI(title="供應商測試數據 API", version="1.0.0")

# 註冊身份驗證和上傳的路由
app.include_router(auth.router)
app.include_router(uploads.router)


# 自定義異常處理器
@app.exception_handler(AppException)
async def app_exception_handler(request, exc):
    """處理自定義的 AppException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """處理請求驗證錯誤"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """處理 HTTP 異常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# 測試用路由
@app.get("/")
def read_root():
    """根路徑，用於測試 API 是否正常運行"""
    logging.info("根端點被訪問")
    return {"message": "歡迎使用供應商測試數據 API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)