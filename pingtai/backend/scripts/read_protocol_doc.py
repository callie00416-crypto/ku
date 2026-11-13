"""
读取电源设备协议文档
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from docx import Document

# 读取Word文档
doc_path = r"D:\Users\Administrator\PycharmProjects\django-vue3-admin\docs\drivers\device\PowerSupply\博瑞程控系列 Modbus编程协议2026-03-26.docx"
print(f"文档路径: {doc_path}")
print(f"文件存在: {Path(doc_path).exists()}")

doc = Document(str(doc_path))

print("=" * 80)
print("博瑞程控系列 Modbus编程协议")
print("=" * 80)

# 读取所有段落
for i, paragraph in enumerate(doc.paragraphs):
    if paragraph.text.strip():
        print(f"{paragraph.text}")

# 读取所有表格
for table_idx, table in enumerate(doc.tables):
    print(f"\n{'=' * 80}")
    print(f"表格 {table_idx + 1}")
    print(f"{'=' * 80}")
    
    for row_idx, row in enumerate(table.rows):
        row_text = []
        for cell in row.cells:
            row_text.append(cell.text.strip())
        print(" | ".join(row_text))