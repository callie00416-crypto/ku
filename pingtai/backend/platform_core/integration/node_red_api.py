"""
Node-RED API 接口
用于 Django 调用 Node-RED 硬件网关
"""

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class NodeRedApiView(APIView):
    """Node-RED API 视图"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """向 Node-RED 发送命令"""
        try:
            # 从配置中获取 Node-RED API URL
            node_red_url = getattr(settings, 'NODE_RED_API_URL', 'http://localhost:1880/')
            
            # 获取请求数据
            command_data = request.data
            
            # 确定具体的端点
            endpoint = command_data.get('endpoint', '')
            if not endpoint:
                return Response({
                    'status': 'error',
                    'message': 'Endpoint is required'
                }, status=400)
            
            # 构建完整 URL
            full_url = f"{node_red_url}{endpoint}"
            
            # 移除 endpoint 字段，避免发送到 Node-RED
            payload = {k: v for k, v in command_data.items() if k != 'endpoint'}
            
            # 发送请求到 Node-RED
            response = requests.post(
                full_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # 返回 Node-RED 的响应
            return Response({
                'status': 'success',
                'message': 'Command sent to Node-RED successfully',
                'node_red_response': response.json() if response.content else {}
            }, status=response.status_code)
            
        except requests.exceptions.RequestException as e:
            return Response({
                'status': 'error',
                'message': f'Failed to communicate with Node-RED: {str(e)}'
            }, status=500)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }, status=500)
    
    def get(self, request):
        """从 Node-RED 获取状态信息"""
        try:
            # 从配置中获取 Node-RED API URL
            node_red_url = getattr(settings, 'NODE_RED_API_URL', 'http://localhost:1880/')
            
            # 获取查询参数
            endpoint = request.query_params.get('endpoint', '')
            if not endpoint:
                return Response({
                    'status': 'error',
                    'message': 'Endpoint query parameter is required'
                }, status=400)
            
            # 构建完整 URL
            full_url = f"{node_red_url}{endpoint}"
            
            # 发送 GET 请求到 Node-RED
            response = requests.get(
                full_url,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # 返回 Node-RED 的响应
            return Response({
                'status': 'success',
                'data': response.json() if response.content else {}
            }, status=response.status_code)
            
        except requests.exceptions.RequestException as e:
            return Response({
                'status': 'error',
                'message': f'Failed to communicate with Node-RED: {str(e)}'
            }, status=500)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }, status=500)


# 如果需要直接调用函数的方式
def send_to_node_red(endpoint: str, payload: dict, base_url: str = None) -> dict:
    """
    直接向 Node-RED 发送命令的函数
    
    Args:
        endpoint: Node-RED 端点路径
        payload: 要发送的数据
        base_url: Node-RED 基础 URL，如果未提供则使用配置中的默认值
        
    Returns:
        Node-RED 的响应结果
    """
    if base_url is None:
        base_url = getattr(settings, 'NODE_RED_API_URL', 'http://localhost:1880/')
    
    full_url = f"{base_url}{endpoint}"
    
    try:
        response = requests.post(
            full_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        return {
            'status': 'success',
            'data': response.json() if response.content else {},
            'status_code': response.status_code
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def get_from_node_red(endpoint: str, base_url: str = None) -> dict:
    """
    直接从 Node-RED 获取数据的函数
    
    Args:
        endpoint: Node-RED 端点路径
        base_url: Node-RED 基础 URL，如果未提供则使用配置中的默认值
        
    Returns:
        Node-RED 的响应结果
    """
    if base_url is None:
        base_url = getattr(settings, 'NODE_RED_API_URL', 'http://localhost:1880/')
    
    full_url = f"{base_url}{endpoint}"
    
    try:
        response = requests.get(
            full_url,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        return {
            'status': 'success',
            'data': response.json() if response.content else {},
            'status_code': response.status_code
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': str(e)
        }
