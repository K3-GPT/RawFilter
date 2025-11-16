import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, SUPPORTED_FORMATS
from file_handler import FileHandler


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
        format_combo['values'] = tuple(sorted(SUPPORTED_FORMATS))
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

            # 执行废片移除
            removed_count = self.file_handler.remove_waste_files(directory, suffix)

            # 执行文件分类
            files_moved = self.file_handler.categorize_files(directory)

            messagebox.showinfo('完成', 
                              f'已移除 {removed_count} 张废片到回收站\n'
                              f'文件分类完成：完整文件 {files_moved["complete"]} 个，单个文件 {files_moved["single"]} 个')

        except Exception as e:
            messagebox.showerror('错误', f'操作失败：{str(e)}')

    def filter_files(self):
        """筛选精修功能"""
        try:
            source_dir = self.get_directory_path('请选择源文件夹（包含RAW和JPG）')
            if not source_dir:
                return

            target_dir = self.get_directory_path('请选择目标文件夹')
            if not target_dir:
                return

            # 获取文件对
            file_pairs = self.file_handler.get_file_pairs(source_dir)

            # 选择格式
            selected_format = self.ask_format_choice()
            if not selected_format:
                return

            # 复制文件
            copied_count = self.file_handler.copy_files_by_format(file_pairs, target_dir, selected_format)

            messagebox.showinfo('完成', f'已复制 {copied_count} 张 {selected_format} 格式的文件')

        except Exception as e:
            messagebox.showerror('错误', f'操作失败：{str(e)}')

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