"""
项目脚手架构建器 - Scaffold Builder

【职责】
- 创建项目目录结构
- 生成基础配置文件
- 初始化项目依赖
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
import json


logger = logging.getLogger(__name__)


class ScaffoldBuilder:
    """项目脚手架构建器
    
    【职责】
- 创建标准项目结构
- 生成配置文件
- 初始化开发环境
    """
    
    # 标准目录结构
    STANDARD_DIRECTORIES = [
        'backend',
        'backend/platform',
        'backend/projects',
        'backend/shared',
        'backend/tests',
        'backend/docs',
        'backend/tools',
        'frontend',
        'frontend/src',
        'frontend/public',
        'config',
        'scripts',
        'docs'
    ]
    
    # 设备项目目录结构
    DEVICE_DIRECTORIES = [
        'backend/projects/encoder_test/drivers/device/{device_name}',
        'backend/projects/encoder_test/adapters',
        'backend/tests/device',
        'docs/drivers/device/{device_name}'
    ]
    
    def __init__(self, config):
        """
        Args:
            config: 平台配置
        """
        self.config = config
        self.base_path = Path(config.base_path)
        self.output_dir = self.base_path / config.generator.output_dir
        
        # 构建统计
        self.stats = {
            'directories_created': 0,
            'files_created': 0,
            'total_size': 0
        }
        
        logger.info("脚手架构建器初始化完成")
    
    def build(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """构建项目脚手架
        
        Args:
            project_spec: 项目规范
            
        Returns:
            构建结果
        """
        try:
            logger.info(f"开始构建项目脚手架: {project_spec.get('name', 'unknown')}")
            
            # 重置统计
            self.stats = {
                'directories_created': 0,
                'files_created': 0,
                'total_size': 0
            }
            
            # 根据项目类型选择构建策略
            project_type = project_spec.get('type', 'standard')
            
            if project_type == 'device':
                result = self._build_device_project(project_spec)
            elif project_type == 'platform':
                result = self._build_platform_project(project_spec)
            else:
                result = self._build_standard_project(project_spec)
            
            # 添加构建统计
            result['stats'] = self.stats.copy()
            
            logger.info(f"项目脚手架构建完成: {self.stats['directories_created']} 个目录, {self.stats['files_created']} 个文件")
            return result
            
        except Exception as e:
            logger.error(f"项目脚手架构建失败: {e}")
            raise
    
    def _build_standard_project(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """构建标准项目
        
        Args:
            spec: 项目规范
            
        Returns:
            构建结果
        """
        project_name = spec.get('name', 'new_project')
        project_path = self.output_dir / project_name
        
        # 创建项目目录
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 创建标准目录结构
        for directory in self.STANDARD_DIRECTORIES:
            dir_path = project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.stats['directories_created'] += 1
        
        # 生成配置文件
        config_files = self._get_standard_config_files(project_name, spec)
        for file_path, content in config_files.items():
            self._create_file(project_path / file_path, content)
        
        # 生成README
        readme_content = self._generate_readme(project_name, spec)
        self._create_file(project_path / 'README.md', readme_content)
        
        # 生成.gitignore
        gitignore_content = self._generate_gitignore()
        self._create_file(project_path / '.gitignore', gitignore_content)
        
        return {
            'success': True,
            'project_name': project_name,
            'project_path': str(project_path),
            'type': 'standard',
            'message': f'标准项目 {project_name} 构建完成'
        }
    
    def _build_device_project(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """构建设备项目
        
        Args:
            spec: 设备项目规范
            
        Returns:
            构建结果
        """
        device_name = spec.get('name', 'new_device')
        
        # 创建设备目录结构
        for directory_template in self.DEVICE_DIRECTORIES:
            directory = directory_template.format(device_name=device_name)
            dir_path = self.output_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.stats['directories_created'] += 1
        
        # 生成设备配置文件
        config_content = self._generate_device_config(device_name, spec)
        self._create_file(
            self.output_dir / f'docs/drivers/device/{device_name}/config.json',
            config_content
        )
        
        # 生成设备文档模板
        doc_content = self._generate_device_doc_template(device_name, spec)
        self._create_file(
            self.output_dir / f'docs/drivers/device/{device_name}/README.md',
            doc_content
        )
        
        return {
            'success': True,
            'device_name': device_name,
            'type': 'device',
            'message': f'设备项目 {device_name} 构建完成'
        }
    
    def _build_platform_project(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """构建平台项目
        
        Args:
            spec: 平台项目规范
            
        Returns:
            构建结果
        """
        project_name = spec.get('name', 'new_platform')
        project_path = self.output_dir / project_name
        
        # 创建平台目录结构
        platform_dirs = [
            'backend/platform/runtime',
            'backend/platform/domain',
            'backend/platform/application',
            'backend/platform/storage',
            'backend/platform/api',
            'backend/platform/codegen'
        ]
        
        for directory in platform_dirs:
            dir_path = project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.stats['directories_created'] += 1
        
        # 生成平台配置
        platform_config = self._generate_platform_config(project_name, spec)
        self._create_file(
            project_path / 'backend/platform/config.json',
            platform_config
        )
        
        return {
            'success': True,
            'project_name': project_name,
            'type': 'platform',
            'message': f'平台项目 {project_name} 构建完成'
        }
    
    def _get_standard_config_files(self, project_name: str, spec: Dict[str, Any]) -> Dict[str, str]:
        """获取标准配置文件
        
        Args:
            project_name: 项目名称
            spec: 项目规范
            
        Returns:
            配置文件字典
        """
        return {
            'backend/requirements.txt': self._generate_requirements(spec),
            'backend/pyproject.toml': self._generate_pyproject(project_name, spec),
            'backend/.env.example': self._generate_env_example(),
            'config/settings.json': self._generate_settings(spec),
            'scripts/setup.sh': self._generate_setup_script(),
            'scripts/setup.bat': self._generate_setup_script_bat()
        }
    
    def _generate_requirements(self, spec: Dict[str, Any]) -> str:
        """生成requirements.txt"""
        requirements = [
            '# Core dependencies',
            'django>=4.2,<5.0',
            'sqlalchemy>=2.0,<3.0',
            'pymysql>=1.1,<2.0',
            'redis>=5.0,<6.0',
            '',
            '# Code generation',
            'jinja2>=3.1,<4.0',
            'pyyaml>=6.0,<7.0',
            '',
            '# Development',
            'pytest>=7.4,<8.0',
            'pytest-asyncio>=0.21,<1.0',
            'black>=23.0,<24.0',
            'flake8>=6.0,<7.0',
            'mypy>=1.5,<2.0',
            '',
            '# Industrial communication',
            'pymodbus>=3.5,<4.0',
            'pyserial>=3.5,<4.0',
            'can>=4.0,<5.0'
        ]
        
        return '\n'.join(requirements)
    
    def _generate_pyproject(self, project_name: str, spec: Dict[str, Any]) -> str:
        """生成pyproject.toml"""
        return f'''[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "{spec.get('description', 'Industrial Automation Project')}"
authors = ["Industrial Team"]

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.dev-dependencies]
pytest = "^7.4"
black = "^23.0"
flake8 = "^6.0"
mypy = "^1.5"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''
    
    def _generate_env_example(self) -> str:
        """生成.env.example"""
        return '''# Database
DATABASE_URL=mysql://user:password@localhost:3306/dbname
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=dbname
DATABASE_USER=user
DATABASE_PASSWORD=password

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here

# Platform
PLATFORM_NAME=IndustrialPlatform
PLATFORM_VERSION=1.0.0
'''
    
    def _generate_settings(self, spec: Dict[str, Any]) -> str:
        """生成settings.json"""
        settings = {
            'project': {
                'name': spec.get('name', 'new_project'),
                'version': '1.0.0',
                'description': spec.get('description', '')
            },
            'database': {
                'host': 'localhost',
                'port': 3306,
                'name': 'industrial_db',
                'user': 'root',
                'password': ''
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
        
        return json.dumps(settings, indent=2, ensure_ascii=False)
    
    def _generate_setup_script(self) -> str:
        """生成setup.sh"""
        return '''#!/bin/bash

echo "Setting up Industrial Automation Platform..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Setup database
echo "Setting up database..."
python backend/manage.py migrate

# Create superuser
echo "Creating superuser..."
python backend/manage.py createsuperuser

echo "Setup complete!"
'''
    
    def _generate_setup_script_bat(self) -> str:
        """生成setup.bat"""
        return '''@echo off
echo Setting up Industrial Automation Platform...

REM Create virtual environment
python -m venv venv
call venv\\Scripts\\activate.bat

REM Install dependencies
pip install -r backend\\requirements.txt

REM Setup database
echo Setting up database...
python backend\\manage.py migrate

REM Create superuser
echo Creating superuser...
python backend\\manage.py createsuperuser

echo Setup complete!
pause
'''
    
    def _generate_readme(self, project_name: str, spec: Dict[str, Any]) -> str:
        """生成README.md"""
        return f'''# {project_name}

{spec.get('description', 'Industrial Automation Platform')}

## 项目结构

```
.
├── backend/              # 后端代码
│   ├── platform/        # 平台核心
│   ├── projects/        # 项目实现
│   ├── shared/          # 共享组件
│   └── tests/           # 测试代码
├── frontend/            # 前端代码
├── config/              # 配置文件
├── scripts/             # 脚本工具
└── docs/                # 文档
```

## 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- Redis 6.0+

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd {project_name}
```

2. 安装依赖
```bash
# Linux/Mac
bash scripts/setup.sh

# Windows
scripts\\setup.bat
```

3. 配置环境变量
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env 配置数据库等信息
```

4. 启动服务
```bash
cd backend
python manage.py runserver
```

## 开发指南

### 添加新设备

使用设备生成器工具：
```bash
python tools/device_generator.py new_device
```

### 运行测试
```bash
pytest backend/tests/
```

### 代码格式化
```bash
black backend/
```

## 文档

详细文档请查看 `docs/` 目录。

## 许可证

MIT License
'''
    
    def _generate_gitignore(self) -> str:
        """生成.gitignore"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Generated
output/
generated/
'''
    
    def _generate_device_config(self, device_name: str, spec: Dict[str, Any]) -> str:
        """生成设备配置"""
        config = {
            'device_name': device_name,
            'class_name': self._to_class_name(device_name),
            'manufacturer': spec.get('manufacturer', 'Unknown'),
            'model': spec.get('model', 'Unknown'),
            'protocol': spec.get('protocol', 'unknown'),
            'communication': spec.get('communication', 'unknown'),
            'description': spec.get('description', ''),
            'parameters': spec.get('parameters', {}),
            'methods': spec.get('methods', [])
        }
        
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def _generate_device_doc_template(self, device_name: str, spec: Dict[str, Any]) -> str:
        """生成设备文档模板"""
        class_name = self._to_class_name(device_name)
        
        return f'''# {device_name} 设备文档

## 设备信息

- **设备名称**: {device_name}
- **类名**: {class_name}
- **制造商**: {spec.get('manufacturer', 'Unknown')}
- **型号**: {spec.get('model', 'Unknown')}
- **通信协议**: {spec.get('protocol', 'unknown')}
- **通信方式**: {spec.get('communication', 'unknown')}

## 设备描述

{spec.get('description', '设备描述待补充')}

## 技术规格

### 通信参数

- **波特率**: 待补充
- **数据位**: 待补充
- **停止位**: 待补充
- **校验位**: 待补充

### 性能参数

- **响应时间**: 待补充
- **精度**: 待补充
- **工作温度**: 待补充

## 寄存器映射

| 地址 | 名称 | 类型 | 描述 |
|------|------|------|------|
| 待补充 | 待补充 | 待补充 | 待补充 |

## 使用示例

```python
from projects.encoder_test.drivers.device.{device_name}.{device_name} import {class_name}
from shared.drivers.factory import CommFactory, ProtocolFactory

# 创建通信层
comm = CommFactory.create('rs485', port='COM3', baudrate=9600)
protocol = ProtocolFactory.create('modbus_rtu', comm=comm, slave_id=1)

# 创建设备实例
device = {class_name}(driver_id='{device_name}', protocol=protocol)

# 连接设备
if device.connect():
    # 读取数据
    data = device.read_data()
    print(data)
    
    # 断开连接
    device.disconnect()
```

## 故障排除

### 常见问题

1. **连接失败**
   - 检查串口是否被占用
   - 确认波特率设置正确
   - 检查设备电源

2. **数据读取错误**
   - 确认寄存器地址正确
   - 检查设备地址配置
   - 验证通信协议参数

## 维护记录

| 日期 | 版本 | 修改内容 | 修改人 |
|------|------|----------|--------|
| 待补充 | 1.0.0 | 初始版本 | 待补充 |
'''
    
    def _generate_platform_config(self, project_name: str, spec: Dict[str, Any]) -> str:
        """生成平台配置"""
        config = {
            'platform': {
                'name': project_name,
                'version': spec.get('version', '1.0.0'),
                'description': spec.get('description', '')
            },
            'modules': {
                'runtime': {
                    'enabled': True,
                    'config': {}
                },
                'domain': {
                    'enabled': True,
                    'config': {}
                },
                'application': {
                    'enabled': True,
                    'config': {}
                },
                'storage': {
                    'enabled': True,
                    'config': {}
                },
                'api': {
                    'enabled': True,
                    'config': {}
                },
                'codegen': {
                    'enabled': True,
                    'config': {}
                }
            }
        }
        
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def _create_file(self, file_path: Path, content: str):
        """创建文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
        """
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新统计
        self.stats['files_created'] += 1
        self.stats['total_size'] += len(content.encode('utf-8'))
        
        logger.debug(f"文件创建完成: {file_path}")
    
    def _to_class_name(self, name: str) -> str:
        """转换为类名
        
        Args:
            name: 原始名称
            
        Returns:
            类名
        """
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def get_stats(self) -> Dict[str, int]:
        """获取构建统计
        
        Returns:
            统计数据
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'directories_created': 0,
            'files_created': 0,
            'total_size': 0
        }