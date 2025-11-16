"""
配置管理模块
使用 Pydantic Settings 管理环境变量
"""
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用环境
    app_env: Literal['development', 'production'] = 'development'
    
    # Gate.io API配置
    gate_api_key: str = ''
    gate_api_secret: str = ''
    gate_testnet: bool = True
    
    # DeepSeek AI配置
    deepseek_api_key: str = ''
    
    # 数据库配置
    database_url: str = 'sqlite:///./data/database.db'
    
    # API 配置
    api_host: str = '0.0.0.0'
    api_port: int = 8000
    
    # CORS 配置
    cors_origins: list = ['http://localhost:5173']
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# 创建全局配置实例
settings = Settings()
