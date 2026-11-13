"""
查看数据库中的用户信息
"""
import os
import sys
import django

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from dvadmin.system.models import Users

def list_users():
    """列出所有用户"""
    print("=" * 60)
    print("📋 数据库中的用户列表")
    print("=" * 60)
    
    users = Users.objects.all()
    
    if not users.exists():
        print("❌ 数据库中没有用户")
        return
    
    for i, user in enumerate(users, 1):
        print(f"\n用户 {i}:")
        print(f"  用户名: {user.username}")
        print(f"  姓名: {user.name}")
        print(f"  邮箱: {user.email}")
        print(f"  手机: {user.mobile}")
        print(f"  是否激活: {'✅ 是' if user.is_active else '❌ 否'}")
        print(f"  是否管理员: {'✅ 是' if user.is_superuser else '❌ 否'}")
        print(f"  是否员工: {'✅ 是' if user.is_staff else '❌ 否'}")
        print(f"  创建时间: {user.create_datetime}")
    
    print(f"\n{'=' * 60}")
    print(f"📊 总计: {users.count()} 个用户")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    list_users()