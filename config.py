import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

load_dotenv()

class Config(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    ADMIN_IDS: list = Field([], env="ADMIN_IDS")
    DATABASE_URL: str = Field("sqlite://db.sqlite3", env="DATABASE_URL")
    TRON_NODE_URL: str = Field("https://api.trongrid.io", env="TRON_NODE_URL")
    TRON_WALLET: str = Field(..., env="TRON_WALLET")
    MAX_DEVICE_CHANGES: int = Field(3, env="MAX_DEVICE_CHANGES")
    COMMISSION_LEVEL1: float = Field(0.15, env="COMMISSION_LEVEL1")
    COMMISSION_LEVEL2: float = Field(0.10, env="COMMISSION_LEVEL2")
    COMMISSION_LEVEL3: float = Field(0.05, env="COMMISSION_LEVEL3")
    LICENSE_POINTS: dict = Field({
        '1m': 1, '3m': 2, '6m': 3,
        '1y': 4, '3y': 5, 'permanent': 8
    }, env="LICENSE_POINTS")
    REWARD_THRESHOLD: int = Field(30, env="REWARD_THRESHOLD")
    
    def __init__(self, **values):
        super().__init__(**values)
        # تبدیل رشته ADMIN_IDS به لیست اعداد
        if isinstance(self.ADMIN_IDS, str):
            self.ADMIN_IDS = [int(id.strip()) for id in self.ADMIN_IDS.split(',') if id.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'