# build_exe.py
"""
图溜溜——RAW筛选器 打包脚本
使用PyInstaller将Python项目打包为exe可执行文件
"""
import os
import sys
import subprocess
import shutil

def check_requirements():
    """检查必要的文件是否存在"""
    required_files = [
        'main.py',
        'gui.py', 
        'file_handler.py',
        'constants.py',
        'Logo.ico',
        'RawFilter.spec',
        'version_info.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"缺少必要文件: {', '.join(missing_files)}")
        return False
    return True

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("PyInstaller安装成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller安装失败: {e}")
        return False

def clean_build_files():
    """清理之前的构建文件"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    print("清理构建文件...")
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"删除目录: {dir_name}")
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 使用spec文件构建
    try:
        # 先尝试使用spec文件
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'RawFilter.spec']
        print(f"执行命令: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        print("使用spec文件构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"使用spec文件构建失败: {e}")
        print("尝试直接使用命令行参数构建...")
        
        # 备选方案：直接使用命令行参数
        try:
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',                    # 打包成单个exe文件
                '--windowed',                   # 不显示控制台窗口
                '--name=图溜溜——RAW筛选器',      # 可执行文件名称
                '--icon=Logo.ico',              # 设置图标
                '--add-data=constants.py;.',    # 包含数据文件
                '--add-data=gui.py;.',
                '--add-data=file_handler.py;.',
                '--add-data=png;png',           # 包含图片文件夹
                '--hidden-import=tkinter',
                '--hidden-import=tkinter.ttk',
                '--hidden-import=tkinter.filedialog',
                '--hidden-import=tkinter.messagebox',
                'main.py'
            ]
            print(f"执行命令: {' '.join(cmd)}")
            subprocess.check_call(cmd)
            print("使用命令行参数构建成功!")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"构建失败: {e2}")
            return False

def main():
    """主函数"""
    print("=" * 50)
    print("图溜溜——RAW筛选器 打包脚本")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('main.py'):
        print("错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 检查必要文件
    if not check_requirements():
        sys.exit(1)
    
    # 安装PyInstaller
    if not install_pyinstaller():
        sys.exit(1)
    
    # 清理构建文件
    clean_build_files()
    
    # 构建可执行文件
    if build_executable():
        print("\n" + "=" * 50)
        print("构建成功!")
        exe_path = os.path.join('dist', '图溜溜——RAW筛选器.exe')
        if os.path.exists(exe_path):
            print(f"可执行文件位置: {os.path.abspath(exe_path)}")
            print(f"文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
        print("=" * 50)
    else:
        print("构建失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()