""" 
AI-Spot-Master 后端入口
FastAPI 应用程序主文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import trade, trader, ai
import uvicorn

# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI-Spot-Master API",
    description="AI驱动的现货交易系统",
    version="0.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(trade.router)
app.include_router(trader.router)
app.include_router(ai.router)

@app.get("/")
async def root():
    """根路径"""
    return {"message": "AI-Spot-Master API is running"}

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "ai-spot-master",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
