#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "aligo>=6.2.8",
#   "loguru>=0.7.3",
#   "pyzipper>=0.3.6",
# ]
# ///

"""压缩本地文件，上传到阿里云盘。"""

import argparse
import os
import random
import tempfile
import time
from datetime import datetime
from pathlib import Path

from aligo import Aligo
from loguru import logger
import pyzipper


ALI_LOGIN_PORT = 80
ALI_SAVE_PATH = "/"
TEMP_PATH = str(Path(tempfile.gettempdir()))


def get_current_date() -> str:
    """返回当前日期，格式为 YYYYMMDD。"""
    return datetime.now().strftime("%Y%m%d")


def build_remote_date_path(remote_path: str, current_date: str) -> str:
    """在远端目录下追加日期目录。"""
    return '/' + '/'.join([remote_path, current_date]).strip("/")


class ZipArchive:
    """负责将单个文件或整个目录压缩成带有可选密码的 zip。"""

    def __init__(self, src_path: str, output_path: str, name: str | None = None, password: str | None = None):
        self.src_path = Path(src_path).expanduser().resolve()
        if not self.src_path.exists():
            raise FileNotFoundError(f"待备份路径不存在: {self.src_path}")

        self.target_name = name or self.src_path.stem
        self.target = self._build_target(output_path)
        # 密码处理：pyzipper 需要 bytes 类型的密码
        self.password = password.encode('utf-8') if password else None

    def _build_target(self, output_path: str) -> Path:
        output_dir = Path(output_path).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f"{self.target_name}.zip"

    def _zip_folder(self, zipf, folder):
        """同步遍历并写入文件"""
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # 计算相对路径，使压缩包内结构从文件夹内部开始
                    arcname = os.path.relpath(file_path, self.src_path)
                    zipf.write(file_path, arcname)
                except Exception as e:
                    logger.error(f"写入文件失败 {file_path}: {e}")

    def run(self, zip_compression: int = pyzipper.ZIP_DEFLATED, zip_level: int = 6) -> Path:
        """生成 zip 文件，支持 AES-256 加密。"""
        logger.info("开始压缩: {}", self.src_path)

        # 确定加密策略
        encryption = pyzipper.WZ_AES if self.password else None

        # 使用 pyzipper.AESZipFile
        with pyzipper.AESZipFile(
                self.target,
                "w",
                compression=zip_compression,
                compresslevel=zip_level,
                encryption=encryption
        ) as zipf:

            if self.password:
                # 显式设置使用 AES 算法
                zipf.setencryption(pyzipper.WZ_AES, nbits=256)
                zipf.setpassword(self.password)

            if self.src_path.is_file():
                zipf.write(self.src_path, self.src_path.name)
            else:
                self._zip_folder(zipf, self.src_path)

        logger.info("压缩完成: {}", self.target)
        return self.target


class UploadAliDriver:
    """负责把备份文件上传到阿里云盘。"""

    def __init__(self, port: int = ALI_LOGIN_PORT):
        self.ali = Aligo(port=port)

    def _ensure_remote_date_folder(self, remote_folder: str, current_date: str):
        """确保远端日期目录存在，不存在时自动创建。"""
        date_folder_path = build_remote_date_path(remote_folder, current_date)
        existing_folder = self.ali.get_folder_by_path(date_folder_path)
        retry_count = 0

        while existing_folder is None and retry_count < 3:
            retry_count += 1
            wait_seconds = random.randint(1, 3)
            logger.info("远端目录 {} 暂未找到，{} 秒后重试第 {} 次", date_folder_path, wait_seconds, retry_count)
            time.sleep(wait_seconds)
            existing_folder = self.ali.get_folder_by_path(date_folder_path)

        if existing_folder is not None:
            return existing_folder

        parent_folder_path = '/' + remote_folder.strip('/')
        parent_folder = self.ali.get_folder_by_path(parent_folder_path)
        if parent_folder is None:
            raise FileNotFoundError(f"阿里云盘目录不存在: {parent_folder_path}")

        logger.info("创建远端日期目录: {}", date_folder_path)
        self.ali.create_folder(current_date, parent_folder.file_id, check_name_mode="refuse")
        created_folder = self.ali.get_folder_by_path(date_folder_path)
        if created_folder is None:
            raise RuntimeError(f"远端日期目录创建失败: {date_folder_path}")
        return created_folder

    def upload(self, remote_folder: str, target: str | os.PathLike[str], name: str, mode: str = "auto_rename"):
        """上传 zip 到阿里云盘指定目录。"""
        current_date = get_current_date()
        date_folder = self._ensure_remote_date_folder(remote_folder, current_date)

        logger.info("开始上传文件到阿里云盘: {}", name)
        result = self.ali.upload_file(target, parent_file_id=date_folder.file_id, name=name, check_name_mode=mode)
        if not result:
            raise RuntimeError(f"上传失败: {name}")

        logger.info("上传成功: {} -> {}", name, build_remote_date_path(remote_folder, current_date))


def main(args):
    """执行备份主流程。"""
    archive = ZipArchive(args.input, args.output, name=args.name, password=args.password)
    archive_target = archive.run()
    archive_name = f"{archive.target_name}.zip"

    if args.upload:
        UploadAliDriver().upload(args.ali_path, archive_target, archive_name)
        if args.delete and archive_target.exists():
            archive_target.unlink()
            logger.info("已删除本地保存的压缩包: {}", archive_target)


def parse_args():
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="压缩文件或目录，上传到阿里云盘。")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="需要备份的文件或目录路径。",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=TEMP_PATH,
        help=f"可选，本地压缩包输出目录；不传则使用临时路径（{TEMP_PATH}）。",
    )
    parser.add_argument(
        "-n",
        "--name",
        default=None,
        help="压缩包名称（不带 .zip 后缀），默认使用源文件或目录名。",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=None,
        help="压缩密码",
    )
    parser.add_argument(
        "-u",
        "--upload",
        action="store_true",
        help="是否上传阿里云",
    )
    parser.add_argument(
        "--ali-path",
        default=ALI_SAVE_PATH,
        help="阿里云盘目标目录，默认上传到根目录（/ 路径在'备份文件'下）。若指定，则该路径必须已存在",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="上传后是否删除压缩文件",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    main(arguments)
