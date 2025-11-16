# constants.py
# 文件格式常量
RAW_FORMATS = {
    '.CR3', '.CR2', '.ARW', '.NEF', '.NRW', '.RW2', '.RAW',
    '.DNG', '.ORF', '.RAF', '.SRW', '.PEF', '.IQ', '.3FR'
}

JPG_FORMATS = {
    '.JPG', '.JPEG', '.PNG', '.BMP'
}

SUPPORTED_FORMATS = RAW_FORMATS | JPG_FORMATS

# 文件夹名称常量
RECYCLE_BIN_FOLDER = "🗑️ 回收站"
COMPLETE_FOLDER = "完整"
SINGLE_FOLDER = "单个"

# 窗口配置
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 280
WINDOW_TITLE = "图溜溜——RAW筛选器"

# 消息文本
MSG_SUCCESS = "操作完成"
MSG_ERROR = "操作失败"
MSG_CANCEL = "用户取消操作"

# 日志配置
LOG_FILE = "operation_log.txt"
LOG_ENCODING = "utf-8"

# 进度条配置
PROGRESS_BAR_LENGTH = 20  # 总进度块数
PROGRESS_BLOCK = "▆"     # 进度块字符
PROGRESS_EMPTY = "."     # 空白块字符

# 日志配置
LOG_FILE = "operation_log.txt"
LOG_ENCODING = "utf-8"

# # 进度条配置
# PROGRESS_BAR_LENGTH = 20  # 总进度块数
# PROGRESS_BLOCK = "▆"     # 进度块字符
# PROGRESS_EMPTY = "."     # 空白块字符