# views.py
import time
import jwt
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from application import settings
from dvadmin.system.models import MessageCenterTargetUser
from django.core.cache import cache


def event_stream(user_id):
    """SSE 事件流生成器"""
    last_sent_time = 0
    
    try:
        while True:
            # 检查客户端是否仍然连接
            try:
                # 从 Redis 中获取最后数据库变更时间
                last_db_change_time = cache.get('last_db_change_time', 0)
                
                # 只有当数据库发生变化时才检查总数
                if last_db_change_time and last_db_change_time > last_sent_time:
                    count = MessageCenterTargetUser.objects.filter(users=user_id, is_read=False).count()
                    yield f"data: {count}\n\n"
                    last_sent_time = time.time()
                
                # 降低轮询频率，减少服务器压力
                time.sleep(2)
            except GeneratorExit:
                # 客户端断开连接
                print(f"SSE 连接关闭: user_id={user_id}")
                break
            except Exception as e:
                print(f"SSE 流错误: {e}")
                time.sleep(2)
    except GeneratorExit:
        print(f"SSE 连接终止: user_id={user_id}")


@csrf_exempt
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def sse_view(request):
    """SSE 服务端推送视图"""
    try:
        token = request.GET.get('token')
        
        # 检查 token 是否存在
        if not token:
            # 返回空的 SSE 流而不是 JSON 错误
            def error_stream():
                yield f"data: {{\"code\": 4000, \"msg\": \"Token 不能为空\"}}\n\n"
            response = StreamingHttpResponse(error_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # 解码 token
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded.get('user_id')
            
            if not user_id:
                # 返回空的 SSE 流
                def error_stream():
                    yield f"data: {{\"code\": 4000, \"msg\": \"Token 无效\"}}\n\n"
                response = StreamingHttpResponse(error_stream(), content_type='text/event-stream')
                response['Cache-Control'] = 'no-cache'
                response['Access-Control-Allow-Origin'] = '*'
                return response
        except jwt.ExpiredSignatureError:
            # 返回空的 SSE 流
            def error_stream():
                yield f"data: {{\"code\": 4001, \"msg\": \"Token 已过期\"}}\n\n"
            response = StreamingHttpResponse(error_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except jwt.InvalidTokenError:
            # 返回空的 SSE 流
            def error_stream():
                yield f"data: {{\"code\": 4000, \"msg\": \"Token 无效\"}}\n\n"
            response = StreamingHttpResponse(error_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        print(f"SSE 连接建立: user_id={user_id}")
        
        # 创建 SSE 响应
        response = StreamingHttpResponse(
            event_stream(user_id),
            content_type='text/event-stream',
        )
        
        # 设置 SSE 必需的响应头
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # 禁用 nginx 缓冲
        response['Connection'] = 'keep-alive'
        
        # 添加 CORS 头
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Expose-Headers'] = 'Content-Type'
        
        return response
        
    except Exception as e:
        print(f"SSE 视图错误: {e}")
        # 返回空的 SSE 流而不是 JSON 错误
        def error_stream():
            yield f"data: {{\"code\": 5000, \"msg\": \"SSE 服务错误\"}}\n\n"
        response = StreamingHttpResponse(error_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['Access-Control-Allow-Origin'] = '*'
        return response
