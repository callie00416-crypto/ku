"""
n8n Webhook 接口
用于 Django 触发 n8n 自动化流程
"""

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class N8nWebhookView(APIView):
    """n8n Webhook 视图"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """触发 n8n 工作流"""
        try:
            # 从配置中获取 n8n webhook URL
            n8n_webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/')
            
            # 获取请求数据
            workflow_data = request.data
            
            # 发送请求到 n8n
            response = requests.post(
                n8n_webhook_url,
                json=workflow_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # 返回 n8n 的响应
            return Response({
                'status': 'success',
                'message': 'Workflow triggered successfully',
                'n8n_response': response.json() if response.content else {}
            }, status=response.status_code)
            
        except requests.exceptions.RequestException as e:
            return Response({
                'status': 'error',
                'message': f'Failed to trigger n8n workflow: {str(e)}'
            }, status=500)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }, status=500)


# 如果需要直接调用函数的方式
def trigger_n8n_workflow(workflow_data: dict, webhook_url: str = None) -> dict:
    """
    直接触发 n8n 工作流的函数
    
    Args:
        workflow_data: 要发送给 n8n 的数据
        webhook_url: n8n webhook URL，如果未提供则使用配置中的默认值
        
    Returns:
        n8n 的响应结果
    """
    if webhook_url is None:
        webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/')
    
    try:
        response = requests.post(
            webhook_url,
            json=workflow_data,
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
