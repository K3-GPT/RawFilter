import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, SUPPORTED_FORMATS, LOG_FILE, PROGRESS_BAR_LENGTH, \
    PROGRESS_BLOCK, PROGRESS_EMPTY
from file_handler import FileHandler
import datetime
import os



class RawFilterGUI:
    """图形用户界面类"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.root.resizable(width=False, height=False)

        # 居中显示
        max_w, max_h = self.root.maxsize()
        x = int((max_w - WINDOW_WIDTH) / 2)
        y = int((max_h - WINDOW_HEIGHT) / 2)
        self.root.geometry(f'+{x}+{y}')

        self.file_handler = FileHandler()
        self.selected_format = tk.StringVar()
        self.progress_var = tk.StringVar(value="")
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_label = tk.Label(self.root, text='欢迎使用', font=('黑体', 15, 'bold'), fg='red')
        title_label.place(x=55, y=15)

        # 格式选择
        format_label = tk.Label(self.root, text='格式选择: ', font=('黑体', 15))
        format_label.place(x=50, y=50)

        format_combo = ttk.Combobox(self.root, textvariable=self.selected_format, width=26)
        # 定义常见格式的优先级顺序
        priority_formats = [
            '.CR3', '.CR2', '.JPG', '.JPEG', '.ARW', '.NEF',
            '.NRW', '.RW2', '.RAW', '.DNG', '.orf', '.raf', '.SRW',
            '.PEF', '.IQ', '.3FR', '.PNG', '.BMP'
        ]
        
        # 根据优先级排序，优先级高的格式排在前面
        sorted_formats = sorted(SUPPORTED_FORMATS, key=lambda f: (
            priority_formats.index(f) if f in priority_formats else len(priority_formats)
        ))
        
        format_combo['values'] = tuple(sorted_formats)
        format_combo.place(x=150, y=52.5)
        format_combo.current(0)

        # 使用说明
        instructions = [
            '·去除废片：把保留的jpg放到有raw的文件夹内，然后选中这个文件夹',
            '会自动删掉不要的raw。',
            '·筛选精修：把要修的jpg放到有raw的文件夹内，然后选中这个文件夹',
            '再选一个你要放精修的新文件夹',
            '会自动把要修的raw单独拷贝到新文件夹。'
        ]

        for i, instruction in enumerate(instructions):
            label = tk.Label(self.root, text=instruction, font=('黑体', 8))
            if i == 0:
                label.place(x=10, y=100 + i * 20)
            elif i == 1:
                label.place(x=80, y=100 + i * 20)
            elif i == 2:
                label.place(x=10, y=100 + i * 20)
            elif i == 3:
                label.place(x=80, y=100 + i * 20)
            else:
                label.place(x=80, y=100 + i * 20)

        # 提示信息
        note_label = tk.Label(self.root, text='（注：建议 jpg <= raw 的数量。）', font=('黑体', 8))
        note_label.place(x=105, y=250)

        # 进度显示
        progress_label = tk.Label(self.root, textvariable=self.progress_var, font=('黑体', 9), fg='blue')
        progress_label.place(x=10, y=250)

        # 按钮
        button_width = 100
        button_spacing = 40
        button_x_center = (WINDOW_WIDTH - (2 * button_width + button_spacing)) // 2

        remove_waste_btn = tk.Button(self.root, text='去除废片', command=self.remove_waste_files, width=10, height=2)
        remove_waste_btn.place(x=button_x_center, y=200)

        filter_btn = tk.Button(self.root, text='筛选精修', command=self.filter_files, width=10, height=2)
        filter_btn.place(x=button_x_center + button_width + button_spacing, y=200)

    def get_directory_path(self, title='请选择一个目录'):
        """获取目录路径"""
        path = filedialog.askdirectory(title=title)
        return path if path else None

    def update_progress(self, current, total, message=""):
        """更新进度显示"""
        if total <= 0:
            percentage = 0
        else:
            percentage = int((current / total) * 100)

        filled_blocks = int((percentage / 100) * PROGRESS_BAR_LENGTH)
        empty_blocks = PROGRESS_BAR_LENGTH - filled_blocks

        progress_bar = PROGRESS_BLOCK * filled_blocks + PROGRESS_EMPTY * empty_blocks
        progress_text = f"[{progress_bar}]{percentage}%"

        if message:
            progress_text += f" {message}"

        self.progress_var.set(progress_text)
        self.root.update()

    def log_operation(self, operation_type, details, error_msg=None):
        """记录操作日志"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"\n{'=' * 60}\n"
        log_entry += f"时间: {timestamp}\n"
        log_entry += f"操作类型: {operation_type}\n"
        log_entry += f"处理详情: {details}\n"

        if error_msg:
            log_entry += f"错误信息: {error_msg}\n"

        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"日志写入失败: {e}")

    def clear_progress(self):
        """清除进度显示"""
        self.progress_var.set("")

    def remove_waste_files(self):
        """去除废片功能"""
        try:
            suffix = self.selected_format.get()
            if suffix not in SUPPORTED_FORMATS:
                messagebox.showerror('错误', f'不支持的文件格式：{suffix}')
                return

            directory = self.get_directory_path('请选择要处理的文件夹')
            if not directory:
                return

            self.update_progress(0, 100, "开始扫描文件...")

            # 执行废片移除
            removed_count = self.file_handler.remove_waste_files(directory, suffix, self.update_progress)
            self.update_progress(50, 100, f"已移除 {removed_count} 张废片")

            # 执行文件分类
            files_moved = self.file_handler.categorize_files(directory, self.update_progress)
            self.update_progress(100, 100, "文件分类完成")

            complete_count = files_moved["complete"]
            single_count = files_moved["single"]

            # 记录日志
            log_details = f"目录: {directory}, 移除废片: {removed_count}张, 完整文件: {complete_count}个, 单个文件: {single_count}个"
            self.log_operation("去除废片", log_details)

            messagebox.showinfo('完成',
                                f'已移除 {removed_count} 张废片到回收站\n'
                                f'文件分类完成：完整文件 {complete_count} 个，单个文件 {single_count} 个')

        except Exception as e:
            error_msg = str(e)
            self.log_operation("去除废片", f"目录: {directory}", error_msg)
            messagebox.showerror('错误', f'操作失败：{error_msg}')
        finally:
            self.clear_progress()

    def filter_files(self):
        """筛选精修功能"""
        try:
            source_dir = self.get_directory_path('请选择源文件夹（包含RAW和JPG）')
            if not source_dir:
                return

            target_dir = self.get_directory_path('请选择目标文件夹')
            if not target_dir:
                return

            self.update_progress(0, 100, "开始获取文件对...")

            # 获取文件对
            file_pairs = self.file_handler.get_file_pairs(source_dir)
            self.update_progress(30, 100, f"找到 {len(file_pairs)} 对文件")

            # 选择格式
            selected_format = self.ask_format_choice()
            if not selected_format:
                return

            self.update_progress(50, 100, f"开始复制 {selected_format} 格式文件...")

            # 复制文件
            copied_count = self.file_handler.copy_files_by_format(file_pairs, target_dir, selected_format,
                                                                  self.update_progress)
            self.update_progress(100, 100, f"复制完成，共 {copied_count} 个文件")

            # 记录日志
            log_details = f"源目录: {source_dir}, 目标目录: {target_dir}, 格式: {selected_format}, 复制文件: {copied_count}个"
            self.log_operation("筛选精修", log_details)

            messagebox.showinfo('完成', f'已复制 {copied_count} 张 {selected_format} 格式的文件')

        except Exception as e:
            error_msg = str(e)
            self.log_operation("筛选精修", f"源目录: {source_dir}, 目标目录: {target_dir}", error_msg)
            messagebox.showerror('错误', f'操作失败：{error_msg}')
        finally:
            self.clear_progress()

    def ask_format_choice(self):
        """询问用户选择格式"""
        choice = tk.StringVar()

        def on_select(format_type):
            choice.set(format_type)
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("选择格式")
        top.geometry("250x100")

        # 居中显示
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{x}+{y}")

        tk.Label(top, text="请选择要复制的格式：", font=("黑体", 12)).pack(pady=5)

        frame = tk.Frame(top)
        frame.pack(pady=5)

        tk.Button(frame, text="RAW", command=lambda: on_select("RAW"), width=10).pack(side="left", padx=5)
        tk.Button(frame, text="JPG", command=lambda: on_select("JPG"), width=10).pack(side="right", padx=5)

        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)
        return choice.get()

    def run(self):
        """运行应用"""
        self.root.mainloop()