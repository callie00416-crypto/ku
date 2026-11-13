"""
重置用户密码脚本
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from dvadmin.system.models import Users

def reset_password(username, new_password):
    """重置指定用户的密码"""
    try:
        user = Users.objects.get(username=username)
        user.password = make_password(new_password)
        user.save()
        print(f"✅ 用户 {username} 的密码已重置为: {new_password}")
        return True
    except Users.DoesNotExist:
        print(f"❌ 用户 {username} 不存在")
        return False

def main():
    print("=" * 60)
    print("🔐 用户密码重置工具")
    print("=" * 60)
    
    # 重置所有管理员用户的密码
    admin_users = ['superadmin', 'admin', 'root']
    new_password = 'admin123456'
    
    print(f"\n将以下管理员用户密码重置为: {new_password}")
    print("-" * 40)
    
    for username in admin_users:
        reset_password(username, new_password)
    
    print("\n" + "=" * 60)
    print("🎉 密码重置完成！")
    print("=" * 60)
    print("\n可用登录账户：")
    print(f"  superadmin / {new_password}")
    print(f"  admin / {new_password}")
    print(f"  root / {new_password}")
    print(f"  test / {new_password}")

if __name__ == '__main__':
    main()