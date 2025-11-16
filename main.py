# main.py
"""
图溜溜——RAW筛选器
模块化版本的主程序入口
"""
import sys
import os
from gui import RawFilterGUI


def main():
    """主函数"""
    try:
        app = RawFilterGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()