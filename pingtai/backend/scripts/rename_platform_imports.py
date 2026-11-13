"""
批量替换 platform 为 platform_core 的脚本
"""
import os
import re
from pathlib import Path

# 需要替换的目录
backend_dir = Path(r"D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend")

# 需要替换的模式
patterns = [
    (r'from platform\.', 'from platform_core.'),
    (r'import platform\.', 'import platform_core.'),
    (r'platform\.codegen', 'platform_core.codegen'),
    (r'platform\.runtime', 'platform_core.runtime'),
    (r'platform\.domain', 'platform_core.domain'),
    (r'platform\.integration', 'platform_core.integration'),
    (r'platform\.api', 'platform_core.api'),
    (r'platform\.application', 'platform_core.application'),
    (r'platform\.models', 'platform_core.models'),
    (r'"platform_core"', '"platform_core"'),
    (r"'platform_core'", "'platform_core'"),
]

# 需要排除的文件和目录
exclude_dirs = {
    '__pycache__',
    '.git',
    'node_modules',
    'venv',
    '.venv',
    'platform_core',  # 新的目录名
    'static',
    'media',
}

exclude_files = {
    '.pyc',
    '.pyo',
    '.pyd',
    '.so',
    '.dll',
    '.exe',
    '.db',
    '.sqlite3',
}

def should_process_file(file_path):
    """判断是否应该处理该文件"""
    # 检查文件扩展名
    if file_path.suffix.lower() in exclude_files:
        return False
    
    # 检查是否在排除的目录中
    for part in file_path.parts:
        if part in exclude_dirs:
            return False
    
    # 只处理 Python 文件
    return file_path.suffix.lower() in ['.py', '.j2', '.md']

def process_file(file_path):
    """处理单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用所有替换模式
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            return False
    
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("🔍 开始搜索需要更新的文件...")
    
    updated_count = 0
    processed_count = 0
    
    # 遍历所有文件
    for file_path in backend_dir.rglob('*'):
        if file_path.is_file() and should_process_file(file_path):
            processed_count += 1
            if process_file(file_path):
                updated_count += 1
    
    print(f"\n📊 处理完成:")
    print(f"   处理文件数: {processed_count}")
    print(f"   更新文件数: {updated_count}")

if __name__ == '__main__':
    main()