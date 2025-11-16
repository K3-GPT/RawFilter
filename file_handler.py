# file_handler.py
import os
import shutil
import logging
from constants import (
    RAW_FORMATS, JPG_FORMATS, SUPPORTED_FORMATS,
    RECYCLE_BIN_FOLDER, COMPLETE_FOLDER, SINGLE_FOLDER
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FileHandler:
    """文件处理类，负责所有文件相关操作"""

    def __init__(self):
        self.processed_count = 0
        self.error_count = 0

    def move_to_recycle_bin(self, directory: str, filename: str) -> bool:
        """将文件移动到回收站文件夹"""
        try:
            recycle_bin_path = os.path.join(directory, RECYCLE_BIN_FOLDER)
            if not os.path.exists(recycle_bin_path):
                os.makedirs(recycle_bin_path)
                logger.info(f"创建回收站文件夹: {recycle_bin_path}")

            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                shutil.move(file_path, os.path.join(recycle_bin_path, filename))
                logger.info(f"移动文件到回收站: {filename}")
                return True
            else:
                logger.warning(f"文件不存在: {file_path}")
                return False
        except Exception as e:
            logger.error(f"移动文件到回收站失败 {filename}: {str(e)}")
            self.error_count += 1
            return False

    def categorize_files(self, directory: str) -> dict:
        """将文件分类为完整对和单个文件"""
        try:
            complete_folder = os.path.join(directory, COMPLETE_FOLDER)
            single_folder = os.path.join(directory, SINGLE_FOLDER)

            # 创建分类文件夹
            for folder in [complete_folder, single_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    logger.info(f"创建分类文件夹: {folder}")

            file_pairs = {}
            files_moved = {'complete': 0, 'single': 0}

            # 遍历目录获取文件对
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if not os.path.isfile(file_path):
                    continue

                name, ext = os.path.splitext(filename)
                ext_lower = ext.lower()

                if ext_lower in SUPPORTED_FORMATS:
                    file_pairs.setdefault(name, []).append(filename)

            # 分类处理
            for name, files in file_pairs.items():
                if len(files) > 1:  # 有匹配的JPG和RAW
                    for file in files:
                        shutil.move(os.path.join(directory, file), os.path.join(complete_folder, file))
                    files_moved['complete'] += len(files)
                    logger.info(f"移动完整文件对: {name} ({len(files)} 个文件)")
                elif len(files) == 1 and files[0].lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    shutil.move(os.path.join(directory, files[0]), os.path.join(single_folder, files[0]))
                    files_moved['single'] += 1
                    logger.info(f"移动单个文件: {files[0]}")

            return files_moved

        except Exception as e:
            logger.error(f"文件分类失败: {str(e)}")
            raise

    def get_file_pairs(self, directory: str) -> dict:
        """获取文件对信息"""
        file_pairs = {}
        try:
            for root_path, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root_path, file)
                    file_name, ext = os.path.splitext(file)
                    ext_lower = ext.lower()

                    if ext_lower in SUPPORTED_FORMATS:
                        if file_name not in file_pairs:
                            file_pairs[file_name] = []
                        file_pairs[file_name].append(file_path)

            logger.info(f"扫描完成，找到 {len(file_pairs)} 个文件组")
            return file_pairs

        except Exception as e:
            logger.error(f"获取文件对失败: {str(e)}")
            raise

    def copy_files_by_format(self, file_pairs: dict, target_dir: str, format_type: str) -> int:
        """根据格式复制文件"""
        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                logger.info(f"创建目标文件夹: {target_dir}")

            copied_count = 0
            target_formats = RAW_FORMATS if format_type == "RAW" else JPG_FORMATS

            for key, files in file_pairs.items():
                if len(files) > 1:  # 只处理有匹配的文件对
                    for file_path in files:
                        _, ext = os.path.splitext(file_path)
                        ext_upper = ext.upper()

                        if ext_upper in target_formats:
                            filename = os.path.basename(file_path)
                            shutil.copy2(file_path, os.path.join(target_dir, filename))
                            copied_count += 1
                            logger.info(f"复制文件: {filename} -> {target_dir}")

            return copied_count

        except Exception as e:
            logger.error(f"文件复制失败: {str(e)}")
            raise

    def remove_waste_files(self, directory: str, target_suffix: str) -> int:
        """移除废片文件"""
        try:
            removed_count = 0
            filename_counts = {}

            # 统计文件名出现次数
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if not os.path.isfile(file_path):
                    continue

                base_filename = os.path.splitext(filename)[0]
                filename_counts[base_filename] = filename_counts.get(base_filename, 0) + 1

            # 移动孤立文件到回收站
            for filename, count in filename_counts.items():
                if count == 1:  # 孤立的文件
                    target_filename = filename + target_suffix
                    file_path = os.path.join(directory, target_filename)
                    if os.path.exists(file_path):
                        if self.move_to_recycle_bin(directory, target_filename):
                            removed_count += 1

            return removed_count

        except Exception as e:
            logger.error(f"移除废片失败: {str(e)}")
            raise