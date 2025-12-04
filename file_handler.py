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

    def categorize_files(self, directory: str, progress_callback=None) -> dict:
        """将文件分类为完整对和单个文件"""
        # 记录JSON格式的日志
        import json
        import time
        import uuid
        import os
        
        def record_json_log(action, directory, complete_files=0, single_files=0, removed_count=0, status="成功", 
                            error_msg="", total_files=0):
            task_id = f"{time.strftime('%Y%m%d')}-{time.strftime('%H%M%S')}-{str(uuid.uuid4())[:2]}"
            log_data = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "action": action,
                "path": directory,
                "removed_count": removed_count,
                "complete_files": complete_files,
                "single_files": single_files,
                "状态": status,
                "异常信息": error_msg,
                "总文件": total_files,
                "任务ID": task_id
            }
            
            # 创建日志目录(如果不存在)
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 保存JSON日志到单独文件
            log_filename = f"operation_log_{time.strftime('%Y%m%d')}.json"
            log_path = os.path.join(log_dir, log_filename)
            
            try:
                # 如果文件不存在，创建文件并写入JSON日志
                if not os.path.exists(log_path):
                    with open(log_path, "w", encoding="utf-8") as log_file:
                        log_file.write("[")
                        json.dump(log_data, log_file, ensure_ascii=False)
                        log_file.write("]\n")
                else:
                    # 如果文件已存在，读取现有内容
                    with open(log_path, "r", encoding="utf-8") as log_file:
                        try:
                            logs = json.load(log_file)
                            if not isinstance(logs, list):
                                logs = [logs]
                        except json.JSONDecodeError:
                            logs = []
                    
                    # 添加新日志并写入文件
                    logs.append(log_data)
                    with open(log_path, "w", encoding="utf-8") as log_file:
                        json.dump(logs, log_file, ensure_ascii=False, indent=4)
                        
            except Exception as e:
                logger.error(f"写入JSON日志文件失败: {str(e)}")
        
        try:
            complete_folder = os.path.join(directory, COMPLETE_FOLDER)
            single_folder = os.path.join(directory, SINGLE_FOLDER)

            # 创建分类文件夹
            for folder in [complete_folder, single_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    logger.info(f"创建分类文件夹: {folder}")

            # 使用更精确的数据结构来存储文件信息
            file_pairs = {}
            files_moved = {'complete': 0, 'single': 0}

            # 遍历目录获取文件对
            all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            
            logger.info(f"找到 {len(all_files)} 个文件")

            # 按照图溜溜.py的逻辑实现文件分组
            for filename in all_files:
                file_path = os.path.join(directory, filename)
                name, ext = os.path.splitext(filename)
                ext_lower = ext.lower()

                # 添加调试信息
                logger.debug(f"处理文件: {filename}, 原始扩展名: {ext}, 小写扩展名: {ext_lower}")

                # 根据文件扩展名判断文件类型
                if ext_lower in ['.jpg', '.jpeg', '.png', '.bmp']:
                    # 使用setdefault方法将文件添加到相应组
                    file_pairs.setdefault(name, []).append(filename)
                    logger.debug(f"添加图片文件到组 {name}: {filename}")
                elif ext_lower in ['.cr3', '.cr2', '.arw', '.nef', '.nrw', '.rw2', '.raw', '.dng', '.orf', '.raf', '.srw',
                                  '.pef', '.iq', '.3fr']:
                    # 使用setdefault方法将文件添加到相应组
                    file_pairs.setdefault(name, []).append(filename)
                    logger.debug(f"添加RAW文件到组 {name}: {filename}")

            # 更新进度
            if progress_callback:
                progress = 50 + int((len(all_files) / (len(all_files) * 2)) * 50) if all_files else 100
                progress_callback(progress, 100, f"正在分类文件 ({len(all_files)}/{len(all_files)})")

            # 分类处理
            total_pairs = len(file_pairs)
            logger.info(f"开始分类 {total_pairs} 个文件组")
            
            # 按照图溜溜.py的逻辑处理文件分类
            for name, files in file_pairs.items():
                logger.debug(f"处理文件组 {name}: 包含文件 {len(files)} 个: {files}")
                
                # 如果文件组数量>1（说明有JPG和RAW），放入"完整"文件夹
                if len(files) > 1:
                    for file in files:
                        source_path = os.path.join(directory, file)
                        if os.path.exists(source_path):  # 确保文件存在
                            target_path = os.path.join(complete_folder, file)
                            try:
                                shutil.move(source_path, target_path)
                                files_moved['complete'] += 1
                                logger.info(f"移动文件到完整文件夹: {file}")
                            except Exception as e:
                                logger.error(f"移动文件失败 {file}: {str(e)}")
                        else:
                            logger.warning(f"文件不存在: {source_path}")
                    
                    logger.info(f"完成移动完整文件对: {name} (文件: {len(files)} 个)")
                
                # 如果文件组数量==1且文件扩展名为.jpg（不区分大小写），放入"单个"文件夹
                elif len(files) == 1 and files[0].lower().endswith('.jpg'):
                    source_path = os.path.join(directory, files[0])
                    if os.path.exists(source_path):  # 确保文件存在
                        target_path = os.path.join(single_folder, files[0])
                        try:
                            shutil.move(source_path, target_path)
                            files_moved['single'] += 1
                            logger.info(f"移动图片文件到单个文件夹: {files[0]}")
                        except Exception as e:
                            logger.error(f"移动文件失败 {files[0]}: {str(e)}")
                    else:
                        logger.warning(f"文件不存在: {source_path}")
                    
                    logger.info(f"完成移动单个图片文件: {name}")
                
                # 注意：单独的RAW文件不在这里处理，它们会在remove_waste_files中处理

            # 更新进度
            if progress_callback:
                progress = 100
                progress_callback(progress, 100, "文件分类完成")

            # 记录执行结果
            record_json_log("categorize_files", directory, 
                          complete_files=files_moved['complete'], 
                          single_files=files_moved['single'],
                          total_files=len(all_files))
            
            logger.info(
                f"文件分类完成：移动了 {files_moved['complete']} 个文件到'完整'文件夹，{files_moved['single']} 个文件到'单个'文件夹")
            
            # 为了兼容gui.py的调用，需要确保返回值的计算正确
            return files_moved

        except Exception as e:
            
            # 记录失败状态和错误信息
            record_json_log("categorize_files", directory, 
                          complete_files=0, 
                          single_files=0,
                          status="失败", error_msg=str(e), total_files=0)
            
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
                    ext_upper = ext.upper()

                    # 扩展文件匹配范围，不仅限于支持的格式
                    # 匹配所有可能的图片格式
                    if (ext_lower in [fmt.lower() for fmt in SUPPORTED_FORMATS] or
                        ext_upper in ['.JPG', '.JPEG', '.PNG', '.BMP', '.CR3', '.CR2', '.ARW', '.NEF', 
                                     '.NRW', '.RW2', '.RAW', '.DNG', '.ORF', '.RAF', '.SRW', '.PEF', 
                                     '.IQ', '.3FR']):
                        if file_name not in file_pairs:
                            file_pairs[file_name] = []
                        file_pairs[file_name].append(file_path)

            logger.info(f"扫描完成，找到 {len(file_pairs)} 个文件组")
            
            # 详细记录找到的文件组信息
            for file_name, paths in file_pairs.items():
                logger.info(f"文件组: {file_name}, 文件数量: {len(paths)}")
                for path in paths:
                    logger.debug(f"  - {path}")
            
            return file_pairs

        except Exception as e:
            logger.error(f"获取文件对失败: {str(e)}")
            raise

    def copy_files_by_format(self, file_pairs: dict, target_dir: str, format_type: str, progress_callback=None) -> int:
        """根据格式复制文件"""
        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                logger.info(f"创建目标文件夹: {target_dir}")

            copied_count = 0
            
            # 确保格式字符串正确匹配常量
            target_formats = RAW_FORMATS if format_type.upper() == "RAW" else JPG_FORMATS
            
            # 打印目标格式信息用于调试
            logger.info(f"目标格式: {target_formats}")

            # 统计需要复制的文件总数
            total_files_to_copy = 0
            files_to_copy = []  # 需要复制的文件列表
            
            for key, files in file_pairs.items():
                if len(files) > 1:  # 只处理有匹配的文件对
                    for file_path in files:
                        _, ext = os.path.splitext(file_path)
                        ext_upper = ext.upper()
                        
                        # 记录所有匹配的文件
                        logger.debug(f"检查文件: {file_path}, 扩展名: {ext_upper}")
                        
                        if ext_upper in target_formats:
                            total_files_to_copy += 1
                            files_to_copy.append((key, file_path))

            logger.info(f"需要复制的文件总数: {total_files_to_copy}")

            # 复制文件并更新进度
            processed_files = 0
            for key, file_path in files_to_copy:
                # 获取文件名
                filename = os.path.basename(file_path)
                
                # 构造目标路径
                target_path = os.path.join(target_dir, filename)
                
                # 复制文件
                shutil.copy2(file_path, target_path)
                copied_count += 1
                logger.info(f"复制文件: {filename} -> {target_dir}")

                processed_files += 1
                if progress_callback:
                    # 更新进度
                    progress = int((processed_files / total_files_to_copy) * 50) + 50  # 50-100的范围
                    if progress > 100:
                        progress = 100
                    progress_callback(progress, 100,
                                      f"正在复制文件 ({processed_files}/{total_files_to_copy})")

            logger.info(f"文件复制完成: 共复制 {copied_count} 个文件")
            return copied_count

        except Exception as e:
            logger.error(f"文件复制失败: {str(e)}")
            # 记录详细的错误信息
            import traceback
            logger.error(traceback.format_exc())
            raise

    def remove_waste_files(self, directory: str, target_suffix: str, progress_callback=None) -> int:
        """移除废片文件"""
        # 记录JSON格式的日志
        import json
        import time
        import uuid
        import os
        
        def record_json_log(action, directory, complete_files=0, single_files=0, removed_count=0, status="成功", 
                            error_msg="", total_files=0):
            task_id = f"{time.strftime('%Y%m%d')}-{time.strftime('%H%M%S')}-{str(uuid.uuid4())[:2]}"
            log_data = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "action": action,
                "path": directory,
                "removed_count": removed_count,
                "complete_files": complete_files,
                "single_files": single_files,
                "状态": status,
                "异常信息": error_msg,
                "总文件": total_files,
                "任务ID": task_id
            }
            
            # 创建日志目录(如果不存在)
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 保存JSON日志到单独文件
            log_filename = f"operation_log_{time.strftime('%Y%m%d')}.json"
            log_path = os.path.join(log_dir, log_filename)
            
            try:
                # 如果文件不存在，创建文件并写入JSON日志
                if not os.path.exists(log_path):
                    with open(log_path, "w", encoding="utf-8") as log_file:
                        log_file.write("[")
                        json.dump(log_data, log_file, ensure_ascii=False)
                        log_file.write("]\n")
                else:
                    # 如果文件已存在，读取现有内容
                    with open(log_path, "r", encoding="utf-8") as log_file:
                        try:
                            logs = json.load(log_file)
                            if not isinstance(logs, list):
                                logs = [logs]
                        except json.JSONDecodeError:
                            logs = []
                    
                    # 添加新日志并写入文件
                    logs.append(log_data)
                    with open(log_path, "w", encoding="utf-8") as log_file:
                        json.dump(logs, log_file, ensure_ascii=False, indent=4)
                        
            except Exception as e:
                logger.error(f"写入JSON日志文件失败: {str(e)}")
        
        removed_count = 0
        filename_counts = {}
        
        try:
            # 统计文件名出现次数
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if not os.path.isfile(file_path):
                    continue

                base_filename = os.path.splitext(filename)[0]
                filename_counts[base_filename] = filename_counts.get(base_filename, 0) + 1

            # 移动孤立的RAW文件到回收站
            total_files = 0
            # 先统计需要处理的孤立RAW文件数量
            for filename, count in filename_counts.items():
                if count == 1:  # 孤立的文件
                    # 检查是否有对应的RAW文件需要移除
                    for raw_ext in RAW_FORMATS:
                        target_filename = filename + raw_ext
                        file_path = os.path.join(directory, target_filename)
                        if os.path.exists(file_path):
                            total_files += 1
                            break

            processed_files = 0
            for filename, count in filename_counts.items():
                if count == 1:  # 孤立的文件
                    # 检查并移动对应的RAW文件到回收站
                    for raw_ext in RAW_FORMATS:
                        target_filename = filename + raw_ext
                        file_path = os.path.join(directory, target_filename)
                        if os.path.exists(file_path):
                            if self.move_to_recycle_bin(directory, target_filename):
                                removed_count += 1
                            break

                    processed_files += 1
                    if progress_callback:
                        progress = int((processed_files / total_files) * 50) if total_files > 0 else 50
                        progress_callback(progress, 100, f"正在处理废片文件 ({processed_files}/{total_files})")

            # 记录执行结果
            record_json_log("remove_waste_files", directory, removed_count=removed_count, 
                          total_files=total_files)
            
            return removed_count

        except Exception as e:
            # 记录失败状态和错误信息
            record_json_log("remove_waste_files", directory, removed_count=0, 
                          status="失败", error_msg=str(e), total_files=total_files)
            
            logger.error(f"移除废片失败: {str(e)}")
            raise