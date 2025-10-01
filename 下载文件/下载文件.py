#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
123云盘文件下载工具

功能说明：
    本工具提供完整的123云盘文件下载功能，支持命令行参数和交互式操作。

主要功能：
    - 文件下载：通过文件ID下载文件到本地
    - 文件详情：获取并显示文件的详细信息
    - MD5校验：下载后自动验证文件完整性
    - 进度显示：实时显示下载进度
    - 智能命名：自动使用API返回的真实文件名

技术特点：
    - 使用v1 API，稳定可靠
    - 流式下载，支持大文件
    - 完整的错误处理和异常捕获
    - 自动获取和管理访问令牌
    - 支持命令行参数和交互式输入两种模式

作者: Assistant
创建日期: 2025/09/26
更新日期: 2025/10/01
版本: v1.5
基于: 123云盘开放平台 API v1
"""

import requests
import os
import sys
import json
import http.client
import argparse
import hashlib
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional, Dict, Any


# ==================== 配置文件处理 ====================

def load_config(config_path: str = None) -> Dict[str, str]:
    """
    从配置文件加载API认证信息

    配置文件说明：
        配置文件采用KEY=VALUE格式，支持注释行（以#开头）
        必需配置项：CLIENT_ID, CLIENT_SECRET

    Args:
        config_path: 配置文件路径，默认为项目根目录的config.txt

    Returns:
        Dict[str, str]: 配置项字典

    Raises:
        FileNotFoundError: 配置文件不存在
        Exception: 配置文件读取失败

    示例:
        >>> config = load_config()
        >>> print(config['CLIENT_ID'])
    """
    if config_path is None:
        # 自动定位配置文件：项目根目录/config.txt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        config_path = os.path.join(project_root, "config.txt")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    config = {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue

                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

        return config

    except Exception as e:
        raise Exception(f"读取配置文件失败: {e}")


# ==================== 核心下载类 ====================

class Pan123Downloader:
    """
    123云盘文件下载器

    本类封装了123云盘开放平台的文件下载相关API，提供便捷的Python接口。
    支持获取文件详情、下载文件和MD5校验等功能。

    属性:
        access_token: API访问令牌
        base_url: API服务器地址
        headers: 通用请求头
        CHUNK_SIZE: 下载块大小（默认8KB）

    使用示例:
        >>> downloader = Pan123Downloader(client_id="your_id", client_secret="your_secret")
        >>> success = downloader.download_file(file_id=12345, save_folder="./downloads")
        >>> if success:
        ...     print("下载成功")
    """

    # API服务器地址常量
    API_BASE_URL = "https://open-api.123pan.com"

    # 下载块大小（8KB）
    CHUNK_SIZE = 8192

    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        """
        初始化下载器

        支持两种初始化方式：
            1. 直接提供access_token
            2. 提供client_id和client_secret，自动获取token

        Args:
            access_token: API访问令牌（可选）
            client_id: 客户端ID（当access_token为空时必需）
            client_secret: 客户端密钥（当access_token为空时必需）

        Raises:
            ValueError: 未提供有效的认证信息
        """
        # 根据提供的参数选择认证方式
        if access_token:
            self.access_token = access_token
        elif client_id and client_secret:
            self.access_token = self._get_access_token(client_id, client_secret)
        else:
            raise ValueError("必须提供access_token或者client_id和client_secret")

        self.base_url = self.API_BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Platform': 'open_platform',
            'Authorization': f'Bearer {self.access_token}'
        }

    def _get_access_token(self, client_id: str, client_secret: str) -> str:
        """
        获取API访问令牌

        向123云盘开放平台认证服务器请求访问令牌。
        令牌用于后续所有API调用的身份验证。

        Args:
            client_id: 客户端ID
            client_secret: 客户端密钥

        Returns:
            str: 访问令牌

        Raises:
            Exception: 令牌获取失败
        """
        print("正在获取访问令牌...")

        try:
            # 建立HTTPS连接
            conn = http.client.HTTPSConnection("open-api.123pan.com")

            # 构造请求体
            payload = json.dumps({
                "clientID": client_id,
                "clientSecret": client_secret
            })

            # 设置请求头
            headers = {
                'Platform': 'open_platform',
                'Content-Type': 'application/json'
            }

            # 发送POST请求
            conn.request("POST", "/api/v1/access_token", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            # 解析响应
            result = json.loads(data)

            if result.get("code") == 0:
                access_token = result.get("data", {}).get("accessToken")
                if access_token:
                    print("✅ 访问令牌获取成功")
                    return access_token
                else:
                    raise Exception("响应中未找到访问令牌")
            else:
                raise Exception(f"获取访问令牌失败: {result.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 获取访问令牌时发生错误: {e}")
            raise

    def _format_file_size(self, size: int) -> str:
        """
        格式化文件大小

        将字节数转换为人类可读的格式（B, KB, MB, GB, TB）。

        Args:
            size: 文件大小（字节）

        Returns:
            str: 格式化后的文件大小字符串

        示例:
            >>> _format_file_size(1024)
            '1.0 KB'
            >>> _format_file_size(1048576)
            '1.0 MB'
        """
        if size == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0

        float_size = float(size)
        while float_size >= 1024 and unit_index < len(units) - 1:
            float_size /= 1024
            unit_index += 1

        return f"{float_size:.1f} {units[unit_index]}"

    def _calculate_md5(self, file_path: str) -> str:
        """
        计算文件MD5值

        分块读取文件并计算MD5哈希值，避免大文件占用过多内存。

        Args:
            file_path: 文件路径

        Returns:
            str: 文件的MD5哈希值（32位小写十六进制字符串）
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # 分块读取文件，每块4KB
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_file_detail(self, file_id: int) -> Optional[Dict[str, Any]]:
        """
        获取文件详情信息

        从API获取指定文件ID的详细信息，包括文件名、大小、MD5等。

        Args:
            file_id: 文件ID

        Returns:
            Optional[Dict[str, Any]]: 文件详情数据，失败时返回None

        Raises:
            requests.exceptions.RequestException: 网络请求失败
        """
        url = f"{self.base_url}/api/v1/file/detail"
        params = {'fileID': file_id}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get('code') == 0:
                return data.get('data')
            else:
                print(f"❌ 获取文件详情失败: {data.get('message', '未知错误')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return None
        except ValueError as e:
            print(f"❌ JSON解析失败: {e}")
            return None

    def get_download_info(self, file_id: int) -> Optional[Dict[str, Any]]:
        """
        获取文件下载信息

        从API获取文件的下载URL等信息。

        Args:
            file_id: 文件ID

        Returns:
            Optional[Dict[str, Any]]: 包含下载URL的响应数据，失败时返回None

        Raises:
            requests.exceptions.RequestException: 网络请求失败
        """
        url = f"{self.base_url}/api/v1/file/download_info"
        params = {'fileId': file_id}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get('code') == 0:
                return data.get('data')
            else:
                print(f"❌ 获取下载信息失败: {data.get('message', '未知错误')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return None
        except ValueError as e:
            print(f"❌ JSON解析失败: {e}")
            return None

    def _display_file_info(self, file_detail: Dict[str, Any]) -> None:
        """
        显示文件详细信息

        格式化输出文件的详细信息，包括ID、名称、大小、MD5等。

        Args:
            file_detail: 文件详情数据
        """
        print("\n" + "=" * 60)
        print("📁 文件详细信息")
        print("=" * 60)
        print(f"文件ID: {file_detail.get('fileID', 'N/A')}")
        print(f"文件名: {file_detail.get('filename', 'N/A')}")
        print(f"文件类型: {'文件夹' if file_detail.get('type') == 1 else '文件'}")
        print(f"文件大小: {self._format_file_size(file_detail.get('size', 0))} "
              f"({file_detail.get('size', 0)} bytes)")
        print(f"MD5值: {file_detail.get('etag', 'N/A')}")
        print(f"审核状态: {'正常' if file_detail.get('status', 0) <= 100 else '审核驳回'}")
        print(f"父目录ID: {file_detail.get('parentFileID', 'N/A')}")
        print(f"创建时间: {file_detail.get('createAt', 'N/A')}")
        print(f"回收站状态: {'在回收站' if file_detail.get('trashed') == 1 else '正常'}")
        print("=" * 60)

    def download_file(self, file_id: int, save_folder: Optional[str] = None,
                     chunk_size: int = None) -> bool:
        """
        下载文件

        从123云盘下载指定文件到本地，支持进度显示和MD5校验。

        工作流程：
            1. 获取文件详情
            2. 验证文件类型和状态
            3. 获取下载链接
            4. 流式下载文件
            5. MD5校验

        Args:
            file_id: 文件ID
            save_folder: 保存文件夹路径，如果不指定则保存到当前目录
            chunk_size: 下载块大小，默认8KB

        Returns:
            bool: 下载成功返回True，失败返回False

        Raises:
            IOError: 文件保存失败
            requests.exceptions.RequestException: 网络请求失败
        """
        if chunk_size is None:
            chunk_size = self.CHUNK_SIZE

        # 步骤1：获取文件详情
        print("📋 正在获取文件详情...")
        file_detail = self.get_file_detail(file_id)
        if not file_detail:
            return False

        # 显示文件信息
        self._display_file_info(file_detail)

        # 步骤2：检查文件类型
        if file_detail.get('type') == 1:
            print("❌ 错误: 不能下载文件夹，请指定具体文件ID")
            return False

        # 检查文件状态
        if file_detail.get('status', 0) > 100:
            print("⚠️  警告: 该文件已被审核驳回，可能无法正常下载")

        if file_detail.get('trashed') == 1:
            print("⚠️  警告: 该文件在回收站中")

        # 步骤3：获取下载信息
        print("\n🔗 正在获取下载链接...")
        download_info = self.get_download_info(file_id)
        if not download_info:
            return False

        download_url = download_info.get('downloadUrl')
        if not download_url:
            print("❌ 未获取到下载链接")
            return False

        print(f"✅ 下载链接: {download_url}")

        # 步骤4：确定保存路径
        filename = file_detail.get('filename', f"file_{file_id}")

        if save_folder:
            # 用户指定了文件夹路径
            if os.path.isdir(save_folder) or not os.path.exists(save_folder):
                save_path = os.path.join(save_folder, filename)
            else:
                print("❌ 错误: 指定的路径不是有效的文件夹路径")
                return False
        else:
            # 保存到当前目录
            save_path = filename

        # 创建保存目录
        save_dir = os.path.dirname(save_path)
        if save_dir:
            Path(save_dir).mkdir(parents=True, exist_ok=True)

        try:
            # 步骤5：下载文件
            print(f"\n🚀 开始下载文件")
            print(f"📄 文件名: {filename}")
            print(f"💾 保存路径: {os.path.abspath(save_path)}")
            print(f"📏 预期大小: {self._format_file_size(file_detail.get('size', 0))}")

            # 发送下载请求（流式）
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            expected_size = file_detail.get('size', 0)
            downloaded_size = 0

            # 检查文件大小是否匹配
            if total_size > 0 and expected_size > 0 and total_size != expected_size:
                print(f"⚠️  警告: 下载大小({total_size})与预期大小({expected_size})不匹配")

            # 写入文件并显示进度
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            downloaded_str = self._format_file_size(downloaded_size)
                            total_str = self._format_file_size(total_size)
                            print(f"\r📥 下载进度: {progress:.1f}% "
                                  f"({downloaded_str}/{total_str})", end='')
                        else:
                            downloaded_str = self._format_file_size(downloaded_size)
                            print(f"\r📥 已下载: {downloaded_str}", end='')

            print(f"\n✅ 文件下载完成: {save_path}")

            # 步骤6：MD5校验
            expected_md5 = file_detail.get('etag', '').lower()
            if expected_md5:
                print("\n🔍 正在进行MD5校验...")
                actual_md5 = self._calculate_md5(save_path)
                print(f"预期MD5: {expected_md5}")
                print(f"实际MD5: {actual_md5}")

                if actual_md5 == expected_md5:
                    print("✅ MD5校验通过，文件完整性验证成功！")
                else:
                    print("❌ MD5校验失败，文件可能已损坏！")
                    return False
            else:
                print("⚠️  无法获取预期MD5值，跳过校验")

            return True

        except requests.exceptions.RequestException as e:
            print(f"\n❌ 下载失败: {e}")
            return False
        except IOError as e:
            print(f"\n❌ 文件保存失败: {e}")
            return False


# ==================== 命令行参数解析 ====================

def parse_arguments():
    """
    解析命令行参数

    支持的参数：
        --file-id/-f: 要下载的文件ID
        --save-path/-p: 保存文件夹路径
        --token/-t: 访问令牌
        --client-id: 客户端ID
        --client-secret: 客户端密钥

    Returns:
        argparse.Namespace: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description='123云盘文件下载工具',
        epilog='示例: python 下载文件.py --file-id 12345 --save-path ./downloads'
    )
    parser.add_argument('--file-id', '-f', type=int, help='要下载的文件ID')
    parser.add_argument('--save-path', '-p', help='保存文件夹路径')
    parser.add_argument('--token', '-t', help='访问令牌')
    parser.add_argument('--client-id', help='客户端ID')
    parser.add_argument('--client-secret', help='客户端密钥')

    return parser.parse_args()


# ==================== 用户输入处理 ====================

def get_file_id_from_input() -> int:
    """
    从用户输入获取文件ID

    持续提示用户输入，直到输入有效的数字ID。

    Returns:
        int: 文件ID
    """
    while True:
        file_id_str = input("请输入要下载的文件ID: ").strip()
        try:
            return int(file_id_str)
        except ValueError:
            print("❌ 文件ID必须是数字，请重新输入")


def get_save_folder_from_input() -> Optional[str]:
    """
    从用户输入获取保存文件夹路径

    持续提示用户输入，直到输入有效的文件夹路径或选择当前目录。
    自动检测并拒绝文件路径（包含扩展名的路径）。

    Returns:
        Optional[str]: 文件夹路径，或None表示当前目录
    """
    while True:
        folder_path = input("请输入保存文件夹路径 (直接回车保存到当前目录): ").strip()

        if not folder_path:
            # 用户直接回车，使用当前目录
            return None

        # 检查输入是否为文件夹路径（不应该包含文件扩展名）
        if os.path.isfile(folder_path):
            print("❌ 错误: 请输入文件夹路径，不是文件路径")
            continue

        # 检查路径是否看起来像文件名（包含扩展名）
        basename = os.path.basename(folder_path)
        if '.' in basename and not folder_path.endswith(('/', '\\')):
            print("❌ 错误: 请输入文件夹路径，不要包含文件名")
            continue

        return folder_path


# ==================== 主程序 ====================

def main():
    """
    主函数 - 命令行和交互式混合界面

    支持两种使用方式：
    1. 命令行参数：python 下载文件.py --file-id 12345 --save-path ./downloads
    2. 交互式输入：运行后按提示输入文件ID和保存路径

    命令行参数优先于交互式输入。
    """
    # 解析命令行参数
    args = parse_arguments()

    # 加载配置文件
    try:
        config = load_config()
        CLIENT_ID = config.get("CLIENT_ID")
        CLIENT_SECRET = config.get("CLIENT_SECRET")

        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError("配置文件中缺少CLIENT_ID或CLIENT_SECRET")

    except Exception as e:
        # 如果配置文件加载失败，但命令行提供了凭据，则继续执行
        if not (args.token or (args.client_id and args.client_secret)):
            print(f"❌ 加载配置失败: {e}")
            print("请确保项目根目录存在config.txt文件，并包含CLIENT_ID和CLIENT_SECRET配置")
            print("或者使用命令行参数 --token 或 --client-id 和 --client-secret 提供凭据")
            return
        CLIENT_ID = None
        CLIENT_SECRET = None

    try:
        print("=" * 60)
        print("123云盘文件下载工具")
        print("=" * 60)

        # 创建下载器实例
        if args.token:
            # 使用命令行提供的访问令牌
            downloader = Pan123Downloader(access_token=args.token)
        elif args.client_id and args.client_secret:
            # 使用命令行提供的客户端ID和密钥
            downloader = Pan123Downloader(
                client_id=args.client_id,
                client_secret=args.client_secret
            )
        else:
            # 使用配置文件中的客户端ID和密钥
            downloader = Pan123Downloader(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET
            )

        # 获取文件ID
        if args.file_id:
            # 使用命令行参数提供的文件ID
            file_id = args.file_id
            print(f"使用命令行参数指定的文件ID: {file_id}")
        else:
            # 从用户输入获取文件ID
            file_id = get_file_id_from_input()

        # 获取保存文件夹路径
        if args.save_path:
            # 使用命令行参数提供的保存文件夹路径
            save_folder = args.save_path
            print(f"使用命令行参数指定的保存文件夹: {save_folder}")
        elif args.file_id:
            # 如果提供了文件ID但没有保存路径，直接保存到当前目录
            save_folder = None
            print("未指定保存路径，将保存到当前目录")
        else:
            # 完全交互式模式，从用户输入获取保存文件夹路径
            save_folder = get_save_folder_from_input()

        # 执行下载
        print(f"\n🎯 准备下载文件ID: {file_id}")
        success = downloader.download_file(file_id, save_folder)

        if success:
            print("\n" + "=" * 60)
            print("🎉 下载任务完成！")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("💥 下载任务失败！")
            print("=" * 60)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 程序运行时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
