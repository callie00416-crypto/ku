"""
PDF阅读工具

【功能】
- 读取ATA-101B设备手册
- 提取串口控制相关信息
- 分析通信协议
"""
import sys
from pathlib import Path

# 添加路径
current_file = Path(__file__).resolve()
backend_path = current_file.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ pdfplumber未安装，尝试安装...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber"])
    try:
        import pdfplumber
        PDF_AVAILABLE = True
    except ImportError:
        print("✗ pdfplumber安装失败")


def read_pdf_manual(pdf_path: str):
    """读取PDF手册"""
    if not PDF_AVAILABLE:
        print("✗ PDF阅读功能不可用")
        return
    
    print("=" * 70)
    print("ATA-101B设备手册阅读")
    print("=" * 70)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"\nPDF信息:")
            print(f"  页数: {len(pdf.pages)}")
            print(f"  文件: {pdf_path}")
            
            # 搜索关键词
            keywords = [
                "串口",
                "RS485",
                "RS-485",
                "通信",
                "控制",
                "远程",
                "程控",
                "USB",
                "协议",
                "指令",
                "命令",
                "波特率",
                "COM",
                "Serial",
                "通信接口"
            ]
            
            print(f"\n搜索关键词: {', '.join(keywords)}")
            
            # 逐页搜索
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                
                if text:
                    # 检查是否包含关键词
                    found_keywords = []
                    for keyword in keywords:
                        if keyword in text:
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"\n{'=' * 70}")
                        print(f"第 {page_num} 页 - 找到关键词: {', '.join(found_keywords)}")
                        print(f"{'=' * 70}")
                        print(text)
                        print()
            
            # 提取所有文本
            print(f"\n{'=' * 70}")
            print("完整文本提取")
            print(f"{'=' * 70}")
            
            all_text = ""
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    all_text += f"\n--- 第 {page_num} 页 ---\n"
                    all_text += text
            
            # 保存到文件
            output_file = Path(pdf_path).parent / "ATA-101B_manual_text.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(all_text)
            
            print(f"\n✓ 完整文本已保存到: {output_file}")
            
    except Exception as e:
        print(f"✗ 读取PDF失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    pdf_path = r"D:\Users\Administrator\PycharmProjects\django-vue3-admin\docs\drivers\device\Power Amplifier\ATA-101B使用说明书V2.0.pdf"
    
    if not Path(pdf_path).exists():
        print(f"✗ PDF文件不存在: {pdf_path}")
        return
    
    read_pdf_manual(pdf_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n阅读被用户中断")
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()