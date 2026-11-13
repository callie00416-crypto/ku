import os

from application.settings import BASE_DIR

# ================================================= #
# *************** mysql数据库 配置  *************** #
# ================================================= #
DATABASE_ENGINE = "django.db.backends.mysql"
DATABASE_NAME = 'encoder_test'
DATABASE_USER = "encoder_user"
DATABASE_PASSWORD = 'encoder_pass'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '3306'

# 表前缀
TABLE_PREFIX = "dvadmin_"

# ================================================= #
# ******** redis配置  ******** #
# ================================================= #
REDIS_DB = 1
CELERY_BROKER_DB = 3
REDIS_PASSWORD = ''
REDIS_HOST = '127.0.0.1'
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6379'
# ================================================= #
# ****************** 功能 启停  ******************* #
# ================================================= #
DEBUG = True
ENABLE_LOGIN_ANALYSIS_LOG = True
LOGIN_NO_CAPTCHA_AUTH = True
# ================================================= #
# ****************** 其他 配置  ******************* #
# ================================================= #

ALLOWED_HOSTS = ["*"]
COLUMN_EXCLUDE_APPS = []