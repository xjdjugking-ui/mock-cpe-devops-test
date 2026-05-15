import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cpe-devops-secret-2024')
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'mock_cpe.db')
    ARTIFACTS_DIR = os.path.join(BASE_DIR, 'artifacts')
    DEBUG = True

    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'

    DEVICE_MODEL = 'CPE-GW-X300'
    DEVICE_FIRMWARE = 'v2.1.0'
    DEVICE_WAN = 'connected'
