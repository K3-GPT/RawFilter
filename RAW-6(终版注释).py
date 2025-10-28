#作者：@摄影师星星
#二创作者：@不说爱你到永久
'''
 **说明**
- **整体架构：**
  - 上半部分定义了三个主要功能：
    1. **回收站功能**：将不需要的文件移动到“回收站”文件夹。
    2. **文件分类功能**：将目录下文件根据配对情况分类到“完整”或“单个”文件夹。
    3. **筛选精修功能**：将匹配的文件（RAW 或 JPG，由用户选择）复制到目标文件夹。
  - 中间部分定义了获取目录、选择格式、以及两个按钮的功能回调。
  - 最后配置界面布局和启动事件循环。

- **功能流程：**
  - 当用户点击“去除废片”时，程序调用 `get_content()`：
    1. 从下拉框中获取选择的后缀（如“.CR3”）。
    2. 弹出对话框让用户选择一个目录。
    3. 调用 `main()` 函数，对该目录内的文件进行处理：统计文件名、移动无配对的文件到回收站，再对剩余文件进行分类。
  - 当用户点击“筛选精修”时，程序调用 `get_content2()`：
    1. 弹出对话框选择原始文件夹和目标文件夹。
    2. 调用 `choose()` 函数，利用文件名配对逻辑，并弹出格式选择窗口，让用户选择复制 RAW 还是 JPG，最后将匹配的文件复制到目标文件夹。
'''
import tkinter as tk                      # 导入Tkinter库，用于创建GUI
from tkinter import ttk, messagebox  # 导入ttk模块，用于高级控件，如下拉列表
import tkinter.messagebox                # 导入消息框模块，用于显示提示信息
from tkinter import filedialog           # 导入文件夹选择对话框模块
import os                                # 导入os模块，用于文件系统操作
import shutil                            # 导入shutil模块，用于复制和移动文件

# 创建主窗口对象
root = tk.Tk()
root.title('RAW筛选器')                   # 设置主窗口标题

# 获取屏幕最大尺寸，用于后续窗口居中计算
max_w, max_h = root.maxsize()

# 设置主窗口大小为400x280，并根据屏幕最大尺寸居中显示
# 这里用格式化字符串计算出窗口的 x, y 坐标
root.geometry('400x280+{}+{}'.format(int((max_w - 500) / 2), int((max_h - 200) / 2)))

# 禁止用户调整窗口大小,True:允许   False：禁止
root.resizable(width=False, height=False)


# ------------------------ 回收站功能 ------------------------
def move_to_recycle_bin(directory, filename):
    """
    将指定文件移动到目录下的“回收站”文件夹
    参数:
        directory: 文件所在的目录
        filename: 要移动的文件名
        秋巴布不扭牛
    """
    # 构造回收站文件夹的路径（在当前目录下创建一个名为“回收站”的文件夹）
    RECYCLE_BIN = os.path.join(directory, "回收站")
    # 如果回收站文件夹不存在，则创建
    if not os.path.exists(RECYCLE_BIN):
        os.makedirs(RECYCLE_BIN)

    # 构造文件的完整路径
    file_path = os.path.join(directory, filename)
    # 如果文件存在，则移动到回收站文件夹中
    if os.path.exists(file_path):
        shutil.move(file_path, os.path.join(RECYCLE_BIN, filename))
        return True   # 移动成功返回True
    return False      # 否则返回False


# ------------------------ 文件分类功能 （完整 / 单个） ------------------------
def categorize_files(directory):
    """
    将目录下的文件分类：
      - 同一文件名有多个文件（例如：同时有JPG和RAW）归入“完整”文件夹
      - 单独存在的JPG归入“单个”文件夹
    """
    # 定义“完整”文件夹和“单个”文件夹的路径
    COMPLETE_FOLDER = os.path.join(directory, "完整")
    SINGLE_FOLDER = os.path.join(directory, "单个")

    # 如果“完整”文件夹不存在，则创建
    if not os.path.exists(COMPLETE_FOLDER):
        os.makedirs(COMPLETE_FOLDER)
    # 如果“单个”文件夹不存在，则创建
    if not os.path.exists(SINGLE_FOLDER):
        os.makedirs(SINGLE_FOLDER)

    # 用于存储去除扩展名后的文件名对应的所有文件
    file_pairs = {}

    # 遍历目录下所有文件
    for filename in os.listdir(directory):
        name, ext = os.path.splitext(filename)  # 分离文件名和扩展名
        # 如果扩展名属于图片格式（JPG、JPEG、PNG、BMP），将该文件添加到字典中
        if ext.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            file_pairs.setdefault(name, []).append(filename)
        # 如果扩展名属于RAW格式，则也添加到字典中
        elif ext.lower() in ['.cr3', '.cr2', '.arw', '.nef', '.nrw', '.rw2', '.raw', '.dng', '.orf', '.raf', '.srw',
                             '.pef', '.iq', '.3fr']:
            file_pairs.setdefault(name, []).append(filename)

    # 根据字典内容将文件移动到相应文件夹
    for name, files in file_pairs.items():
        if len(files) > 1:  # 如果同一文件名对应多个文件，说明同时有RAW和JPG，归类为完整文件
            for file in files:
                shutil.move(os.path.join(directory, file), os.path.join(COMPLETE_FOLDER, file))
        # 如果只有一个文件，且是JPG，则归类到单个文件夹
        elif len(files) == 1 and files[0].lower().endswith('.jpg'):
            shutil.move(os.path.join(directory, files[0]), os.path.join(SINGLE_FOLDER, files[0]))


# ------------------------ 主功能：去除废片 ------------------------
def main(directory, suffix):
    """
    功能：
      1. 遍历目录中所有文件，统计不含扩展名的文件名出现的次数。
      2. 如果某个文件名仅出现一次，则认为该文件没有对应配对，将其移动到回收站。
      3. 调用分类功能，将剩余文件按照“完整”与“单个”归类。
    参数：
      directory: 用户选择的文件夹路径
      suffix: 用户从下拉框中选择的文件格式后缀（例如“.CR3”）
    """
    filename_counts = {}  # 用于统计各个文件基名称出现次数
    S = 0  # 记录移动到回收站的文件数量

    # 遍历目录中所有文件
    for filename in os.listdir(directory):
        base_filename = os.path.splitext(filename)[0]  # 获取不含扩展名的文件名
        if base_filename in filename_counts:
            filename_counts[base_filename] += 1
        else:
            filename_counts[base_filename] = 1

    # 对于仅出现一次的文件，认为没有匹配，尝试将对应后缀的文件移入回收站
    for filename, count in filename_counts.items():
        if count == 1:
            new_filename = filename + suffix   # 构造完整的文件名（基名称+后缀）
            if move_to_recycle_bin(directory, new_filename):  # 调用回收站功能
                S += 1  # 成功移动则计数加1

    # 调用文件分类功能，将剩余的文件归类到“完整”或“单个”文件夹中
    categorize_files(directory)
    print(f"已移动 {S} 张文件到回收站，并完成分类")
    return S


# ------------------------ 筛选精修功能 ------------------------
# 这里的功能是：根据同一文件名配对的规则，复制匹配的文件到目标文件夹
def choose(path, opath):
    """
    功能：
      1. 遍历原始文件夹，按照去除扩展名后的文件名对文件进行分组。
      2. 如果某个文件名对应多个文件（说明存在匹配的JPG和RAW），则复制这些文件（根据用户选择的格式）到目标文件夹。
    参数：
      path: 原始文件夹路径
      opath: 目标文件夹路径
    """
    filename_counts = {}  # 用于存储文件名（去除扩展名）及对应文件的完整路径
    S = 0  # 记录复制的文件数量

    # 遍历所有子目录和文件
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name, ext = os.path.splitext(file)
            if file_name in filename_counts:
                filename_counts[file_name].append(file_path)
            else:
                filename_counts[file_name] = [file_path]

    # 如果目标文件夹不存在，则创建
    if not os.path.exists(opath):
        os.mkdir(opath)

    # 弹出窗口，让用户选择复制 RAW 还是 JPG 格式
    selected_format = ask_format_choice()
    if not selected_format:
        return  # 用户点击取消则退出

    # 定义 RAW 和 JPG 的格式集合，用于匹配文件后缀
    raw_formats = {'.CR3', '.CR2', '.ARW', '.NEF', '.NRW', '.RW2', '.RAW',
                   '.DNG', '.ORF', '.RAF', '.SRW', '.PEF', '.IQ', '.3FR'}
    jpg_formats = {'.JPG', '.JPEG'}

    # 对于每个文件组，若组内有多个文件（说明有配对的情况），则根据用户选择复制对应格式的文件
    for key, files in filename_counts.items():
        if len(files) > 1:  # 说明存在匹配的 RAW 和 JPG 文件
            for file_path in files:
                _, ext = os.path.splitext(file_path)
                ext = ext.upper()  # 转换为大写，统一格式比较

                if selected_format == "RAW" and ext in raw_formats:
                    shutil.copy2(file_path, opath)  # 复制RAW文件
                    S += 1
                elif selected_format == "JPG" and ext in jpg_formats:
                    shutil.copy2(file_path, opath)  # 复制JPG文件
                    S += 1

    # 显示复制完成的提示信息
    messagebox.showinfo("完成", f"已复制 {S} 张 {selected_format} 格式的文件")
    return S


# ------------------------ 弹窗：选择复制格式 ------------------------
def ask_format_choice():
    """
    弹出一个窗口，让用户选择复制 RAW 还是 JPG 格式的文件
    返回用户选择的字符串："RAW" 或 "JPG"
    """
    choice = tk.StringVar()  # 用于存储用户选择的格式

    def on_select(format_type):
        choice.set(format_type)  # 设置选择的格式
        top.destroy()            # 关闭弹窗

    top = tk.Toplevel(root)       # 创建顶级窗口，其父窗口为主窗口 root
    top.title("选择格式")
    top.geometry("250x100")

    # 让弹窗相对于主窗口居中显示
    top.update_idletasks()  # 更新窗口信息，确保尺寸数据准确
    x = root.winfo_x() + (root.winfo_width() - top.winfo_width()) // 2
    y = root.winfo_y() + (root.winfo_height() - top.winfo_height()) // 2
    top.geometry(f"+{x}+{y}")   # 设置窗口位置

    # 显示提示文本
    tk.Label(top, text="请选择要复制的格式：", font=("黑体", 12)).pack(pady=5)

    # 创建一个容器，用于放置两个按钮
    frame = tk.Frame(top)
    frame.pack(pady=5)

    # 创建按钮，点击后调用on_select函数，传入相应的格式参数
    tk.Button(frame, text="RAW", command=lambda: on_select("RAW"), width=10).pack(side="left", padx=5)
    tk.Button(frame, text="JPG", command=lambda: on_select("JPG"), width=10).pack(side="right", padx=5)

    top.transient(root)   # 设置顶级窗口为临时窗口，和主窗口关联
    top.grab_set()        # 使弹窗成为模态窗口，用户必须先处理弹窗
    root.wait_window(top) # 等待弹窗关闭
    return choice.get()   # 返回用户选择的格式


# ------------------------ 获取目录路径 ------------------------
def get_path():
    """
    弹出文件夹选择对话框，返回用户选择的文件夹路径（字符串）
    """
    path = filedialog.askdirectory(title='请选择一个目录')
    return str(path)


# ------------------------ 处理“去除废片”功能 ------------------------
def get_content():
    """
    当用户点击“去除废片”按钮时调用：
      1. 从下拉框中获取用户选择的格式后缀（如“.CR3”）
      2. 弹出对话框让用户选择要处理的目录
      3. 调用 main() 函数，进行废片的移动（删除）操作
      4. 弹出提示信息显示处理结果
    """
    suffix = number_int_var.get()  # 获取下拉列表中选择的格式后缀
    path = get_path()              # 弹出对话框，获取目录路径
    # 定义支持的格式集合
    supported_formats = {'.CR3', '.CR2', '.JPG', '.ARW', '.NEF', '.NRW',
                         '.RW2', '.RAW', '.DNG', '.orf', '.raf', '.SRW',
                         '.PEF', '.IQ', '.3FR'}

    if suffix in supported_formats:
        title = main(path, suffix)  # 调用 main() 函数处理废片（移动到回收站，并分类）
        tk.messagebox.showinfo(title='温馨提示', message=f'已将{title}张{suffix}文件移入回收站')
    else:
        tk.messagebox.showinfo(title='温馨提示', message=f'不支持的文件格式：{suffix}')


# ------------------------ 处理“筛选精修”功能 ------------------------
def get_content2():
    """
    当用户点击“筛选精修”按钮时调用：
      1. 弹出对话框让用户选择原始文件夹和目标文件夹
      2. 调用 choose() 函数，复制匹配的文件（根据用户选择的格式）到目标文件夹
    """
    path = get_path()   # 获取原始文件夹路径
    opath = get_path()  # 获取目标文件夹路径
    title = choose(path, opath)  # 调用 choose() 进行匹配复制
    # 下面这行代码已被注释，若需要可解除注释显示提示信息
    # tk.messagebox.showinfo(title='温馨提示', message=f'已复制{title}张')


# ------------------------ 设置窗口属性 ------------------------
root.attributes("-alpha", 1.0)   # 设置窗口不透明（1.0表示全不透明）

# 创建说明标签
text_label_1 = tk.Label(root, text='格式选择: ', font=('黑体', 15))
text_label_1.place(x=50, y=50)

# 创建下拉列表，用于选择处理的文件格式后缀
number_int_var = tk.StringVar()
numberChosen = ttk.Combobox(root, textvariable=number_int_var, width=26)
numberChosen['values'] = ('.CR3', '.CR2', '.JPG', '.ARW', '.NEF', '.NRW',
                          '.RW2', '.RAW', '.DNG', '.orf', '.raf', '.SRW', '.PEF', '.IQ', '.3FR')
numberChosen.place(x=150, y=52.5)
numberChosen.current(0)  # 默认选择第一个选项

# 创建多行说明文本标签，解释功能和注意事项
text_label_2 = tk.Label(root, text='·去除废片：把保留的jpg放到有raw的文件夹内，然后选中这个文件夹', font=('黑体', 8))
text_label_2.place(x=10, y=100)
text_label_2 = tk.Label(root, text='会自动删掉不要的raw。', font=('黑体', 8))
text_label_2.place(x=80, y=120)
text_label_2 = tk.Label(root, text='·筛选精修：把要修的jpg放到有raw的文件夹内，然后选中这个文件夹', font=('黑体', 8))
text_label_2.place(x=10, y=140)
text_label_2 = tk.Label(root, text='再选一个你要放精修的新文件夹', font=('黑体', 8))
text_label_2.place(x=80, y=160)
text_label_2 = tk.Label(root, text='会自动把要修的raw单独拷贝到新文件夹。', font=('黑体', 8))
text_label_2.place(x=80, y=180)
text_label_2 = tk.Label(root, text='欢迎使用', font=('黑体', 15, 'bold'), fg='red')
text_label_2.place(x=55, y=15)
text_label_2 = tk.Label(root, text='（注：建议 jpg <= raw 的数量。）', font=('黑体', 8))
text_label_2.place(x=105, y=250)

# ------------------------ 按钮布局 ------------------------
# 计算按钮水平居中的 x 坐标（确保两个按钮间距一致）
button_width = 100   # 按钮宽度，单位为像素（width=10 对应大约100像素）
button_spacing = 40  # 按钮之间的间隔
button_x_center = (400 - (2 * button_width + button_spacing)) // 2  # 400 是窗口宽度

# 创建“去除废片”按钮，并设置点击时调用 get_content() 函数
Button_1 = tk.Button(root, text='去除废片', command=get_content, width=10, height=2)
Button_1.place(x=button_x_center, y=200)  # 放置在计算好的位置

# 创建“筛选精修”按钮，并设置点击时调用 get_content2() 函数
Button_2 = tk.Button(root, text='筛选精修', command=get_content2, width=10, height=2)
Button_2.place(x=button_x_center + button_width + button_spacing, y=200)

# ------------------------ 进入事件循环 ------------------------
root.mainloop()  # 启动Tkinter事件循环，等待用户操作


