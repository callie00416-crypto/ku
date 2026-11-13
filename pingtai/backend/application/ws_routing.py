# -*- coding: utf-8 -*-
from django.urls import path, re_path
from application.websocketConfig import MegCenter

# 支持两种路由格式：
# 1. 简单的 service_uid
# 2. JWT token（包含点号和特殊字符）
websocket_urlpatterns = [
    path('ws/<str:service_uid>/', MegCenter.as_asgi()),
    re_path(r'ws/(?P<service_uid>[^/]+)/$', MegCenter.as_asgi()),
]