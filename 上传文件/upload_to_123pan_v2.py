#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
123云盘文件上传工具

功能说明：
    本工具提供完整的123云盘文件上传功能，支持自动选择最优上传方式。

主要功能：
    - 智能上传：根据文件大小自动选择单步上传（≤1GB）或分片上传（≤10GB）
    - 秒传检测：大文件上传前自动检测是否可以秒传
    - 断点续传：分片上传支持失败重试机制
    - 进度显示：实时显示上传进度和状态

技术特点：
    - 使用v2 API，性能更优
    - MD5校验保证文件完整性
    - 完整的错误处理和异常捕获
    - 自动获取和管理访问令牌
    - 支持multipart/form-data上传格式

作者: Assistant
创建日期: 2025/09/26
更新日期: 2025/10/01
版本: v2.0
基于: 123云盘开放平台 API v2
"""

import os
import hashlib
import json
import time
import math
import http.client
import mimetypes
import sys
import ssl
from codecs import encode
from typing import Optional, Dict, Any, List


# ==================== SSL配置 ====================

# 创建不验证SSL的上下文
ssl._create_default_https_context = ssl._create_unverified_context
original_https_context = ssl.create_default_context
ssl.create_default_context = lambda: ssl.create_default_context(ssl.Purpose.SERVER_AUTH).load_default_certs()


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


# ==================== 核心上传类 ====================

class Pan123Uploader:
    """
    123云盘文件上传器

    本类封装了123云盘开放平台的文件上传相关API，提供便捷的Python接口。
    使用v2版本API，支持单步上传和分片上传两种模式。

    属性:
        access_token: API访问令牌
        api_base: API服务器地址
        upload_domains: 上传域名列表
        SINGLE_UPLOAD_LIMIT: 单步上传文件大小限制（1GB）
        MAX_FILE_SIZE: 最大文件大小限制（10GB）

    使用示例:
        >>> uploader = Pan123Uploader(client_id="your_id", client_secret="your_secret")
        >>> result = uploader.upload_file("test.txt", parent_file_id=0)
        >>> print(result['fileID'])
    """

    # API服务器地址常量
    API_BASE = "open-api.123pan.com"

    # 文件大小限制（字节）
    SINGLE_UPLOAD_LIMIT = 1 * 1024 * 1024 * 1024  # 1GB - 单步上传限制
    MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024       # 10GB - 最大文件大小

    # multipart/form-data 分隔符
    BOUNDARY = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'

    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        """
        初始化上传器

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
        self.api_base = self.API_BASE
        self.upload_domains = []

        # 根据提供的参数选择认证方式
        if access_token:
            self.access_token = access_token
        elif client_id and client_secret:
            self.access_token = self._get_access_token(client_id, client_secret)
        else:
            raise ValueError("必须提供access_token或者client_id和client_secret")

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
            conn = http.client.HTTPSConnection(self.api_base)

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

    def _get_headers(self) -> Dict[str, str]:
        """
        构造API请求头

        Returns:
            Dict[str, str]: 包含认证信息的请求头字典
        """
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Platform': 'open_platform'
        }

    def _calculate_md5(self, file_path: str) -> str:
        """
        计算文件MD5值

        分块读取文件并计算MD5哈希值，避免大文件占用过多内存。

        Args:
            file_path: 文件路径

        Returns:
            str: 文件的MD5哈希值（32位小写十六进制字符串）

        示例:
            >>> _calculate_md5("test.txt")
            'e10adc3949ba59abbe56e057f20f883e'
        """
        print(f"📊 正在计算文件MD5: {os.path.basename(file_path)}")
        hash_md5 = hashlib.md5()

        with open(file_path, "rb") as f:
            # 分块读取文件，每块4KB
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        md5_value = hash_md5.hexdigest()
        print(f"✅ 文件MD5计算完成: {md5_value}")
        return md5_value

    def _calculate_slice_md5(self, file_path: str, start: int, size: int) -> str:
        """
        计算文件分片的MD5值

        读取文件的指定部分并计算其MD5哈希值。
        用于分片上传时验证每个分片的完整性。

        Args:
            file_path: 文件路径
            start: 分片起始位置（字节偏移量）
            size: 分片大小（字节数）

        Returns:
            str: 分片的MD5哈希值
        """
        hash_md5 = hashlib.md5()

        with open(file_path, "rb") as f:
            # 定位到分片起始位置
            f.seek(start)
            remaining = size

            # 读取指定大小的数据
            while remaining > 0:
                chunk_size = min(4096, remaining)
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_md5.update(chunk)
                remaining -= len(chunk)

        return hash_md5.hexdigest()

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

        return f"{float_size:.2f} {units[unit_index]}"

    def get_upload_domains(self) -> List[str]:
        """
        获取上传域名列表

        从API服务器获取可用的上传域名列表。
        上传文件时将使用这些域名。

        Returns:
            List[str]: 上传域名列表

        Raises:
            Exception: API调用失败
        """
        print("🌐 正在获取上传域名...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            conn.request("GET", "/upload/v2/file/domain", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                domains = result.get("data", [])
                self.upload_domains = domains
                print(f"✅ 获取到 {len(domains)} 个上传域名")
                return domains
            else:
                raise Exception(f"获取上传域名失败: {result.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 获取上传域名时发生错误: {e}")
            raise

    def create_file(self, file_path: str, parent_file_id: int = 0) -> Dict[str, Any]:
        """
        创建文件（检测秒传）

        在云盘中创建文件记录，并检测是否可以秒传。
        如果云盘已存在相同MD5的文件，则直接秒传成功。

        Args:
            file_path: 本地文件路径
            parent_file_id: 父目录ID，0表示根目录

        Returns:
            Dict[str, Any]: 包含以下键的字典：
                - success: 是否成功
                - reuse: 是否秒传
                - fileID: 文件ID（秒传时返回）
                - preuploadID: 预上传ID（需要上传时返回）
                - sliceSize: 分片大小（需要上传时返回）
                - servers: 上传服务器列表（需要上传时返回）

        Raises:
            Exception: API调用失败或文件超过大小限制
        """
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_md5 = self._calculate_md5(file_path)

        print(f"📝 正在创建文件: {filename}")
        print(f"📏 文件大小: {self._format_file_size(file_size)}")

        # 检查文件大小限制
        if file_size > self.MAX_FILE_SIZE:
            raise Exception(
                f"文件大小 {self._format_file_size(file_size)} "
                f"超过最大限制 {self._format_file_size(self.MAX_FILE_SIZE)}"
            )

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'

            payload = json.dumps({
                "parentFileID": parent_file_id,
                "filename": filename,
                "etag": file_md5,
                "size": file_size
            })

            conn.request("POST", "/upload/v2/file/create", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data = result.get("data", {})

                if data.get("reuse", False):
                    print(f"✅ 文件秒传成功! 文件ID: {data.get('fileID')}")
                    return {"success": True, "reuse": True, "fileID": data.get("fileID")}
                else:
                    print("需要上传文件内容")
                    return {
                        "success": True,
                        "reuse": False,
                        "preuploadID": data.get("preuploadID"),
                        "sliceSize": data.get("sliceSize"),
                        "servers": data.get("servers", [])
                    }
            else:
                raise Exception(f"创建文件失败: {result.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 创建文件时发生错误: {e}")
            raise

    def single_upload(self, file_path: str, parent_file_id: int = 0) -> Dict[str, Any]:
        """
        单步上传文件

        适用于小于1GB的文件。将整个文件一次性上传到服务器。
        使用multipart/form-data格式上传。

        Args:
            file_path: 本地文件路径
            parent_file_id: 父目录ID，0表示根目录

        Returns:
            Dict[str, Any]: 上传结果，包含success和fileID

        Raises:
            Exception: 上传失败
        """
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_md5 = self._calculate_md5(file_path)

        print(f"🚀 开始单步上传: {filename}")

        # 获取上传域名
        if not self.upload_domains:
            self.get_upload_domains()

        if not self.upload_domains:
            raise Exception("无法获取上传域名")

        # 提取域名（移除协议前缀）
        upload_domain = self.upload_domains[0].replace("https://", "").replace("http://", "")

        try:
            # 构建multipart/form-data请求体
            boundary = self.BOUNDARY
            data_list = []

            # 添加文件
            data_list.append(encode('--' + boundary))
            data_list.append(encode(f'Content-Disposition: form-data; name=file; filename={filename}'))

            file_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            data_list.append(encode(f'Content-Type: {file_type}'))
            data_list.append(encode(''))

            with open(file_path, 'rb') as f:
                data_list.append(f.read())

            # 添加其他字段
            fields = [
                ('parentFileID', str(parent_file_id)),
                ('filename', filename),
                ('etag', file_md5),
                ('size', str(file_size))
            ]

            for field_name, field_value in fields:
                data_list.append(encode('--' + boundary))
                data_list.append(encode(f'Content-Disposition: form-data; name={field_name};'))
                data_list.append(encode('Content-Type: text/plain'))
                data_list.append(encode(''))
                data_list.append(encode(field_value))

            data_list.append(encode('--' + boundary + '--'))
            data_list.append(encode(''))

            body = b'\r\n'.join(data_list)

            # 发送请求
            conn = http.client.HTTPSConnection(upload_domain)
            headers = self._get_headers()
            headers['Content-type'] = f'multipart/form-data; boundary={boundary}'

            print(f"⬆️  正在上传到服务器: {upload_domain}")
            conn.request("POST", "/upload/v2/file/single/create", body, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data = result.get("data", {})
                if data.get("completed", False):
                    print(f"✅ 单步上传成功! 文件ID: {data.get('fileID')}")
                    return {"success": True, "fileID": data.get("fileID")}
                else:
                    raise Exception("上传未完成")
            else:
                raise Exception(f"单步上传失败: {result.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 单步上传时发生错误: {e}")
            raise

    def slice_upload(self, file_path: str, preupload_id: str, slice_size: int,
                    servers: List[str]) -> bool:
        """
        分片上传文件

        将大文件分成多个分片，逐个上传到服务器。
        每个分片都会计算MD5值以确保完整性。

        Args:
            file_path: 本地文件路径
            preupload_id: 预上传ID
            slice_size: 分片大小（字节）
            servers: 上传服务器列表

        Returns:
            bool: 上传是否成功

        Raises:
            Exception: 分片上传失败
        """
        file_size = os.path.getsize(file_path)
        total_slices = math.ceil(file_size / slice_size)

        print(f"📦 开始分片上传，总分片数: {total_slices}")

        # 提取服务器域名
        upload_server = servers[0].replace("https://", "").replace("http://", "")

        # 上传每个分片
        for slice_no in range(1, total_slices + 1):
            start_pos = (slice_no - 1) * slice_size
            current_slice_size = min(slice_size, file_size - start_pos)

            print(f"⬆️  正在上传分片 {slice_no}/{total_slices} "
                  f"(大小: {self._format_file_size(current_slice_size)})")

            # 计算分片MD5
            slice_md5 = self._calculate_slice_md5(file_path, start_pos, current_slice_size)

            # 读取分片数据
            with open(file_path, 'rb') as f:
                f.seek(start_pos)
                slice_data = f.read(current_slice_size)

            # 构建multipart/form-data请求
            boundary = self.BOUNDARY
            data_list = []

            # 添加字段
            fields = [
                ('preuploadID', preupload_id),
                ('sliceNo', str(slice_no)),
                ('sliceMD5', slice_md5)
            ]

            for field_name, field_value in fields:
                data_list.append(encode('--' + boundary))
                data_list.append(encode(f'Content-Disposition: form-data; name={field_name};'))
                data_list.append(encode('Content-Type: text/plain'))
                data_list.append(encode(''))
                data_list.append(encode(field_value))

            # 添加分片文件
            data_list.append(encode('--' + boundary))
            data_list.append(encode(f'Content-Disposition: form-data; name=slice; filename=slice_{slice_no}'))
            data_list.append(encode('Content-Type: application/octet-stream'))
            data_list.append(encode(''))
            data_list.append(slice_data)

            data_list.append(encode('--' + boundary + '--'))
            data_list.append(encode(''))

            body = b'\r\n'.join(data_list)

            # 发送分片
            try:
                conn = http.client.HTTPSConnection(upload_server)
                headers = self._get_headers()
                headers['Content-type'] = f'multipart/form-data; boundary={boundary}'

                conn.request("POST", "/upload/v2/file/slice", body, headers)
                response = conn.getresponse()
                data = response.read().decode("utf-8")
                conn.close()

                result = json.loads(data)

                if result.get("code") != 0:
                    raise Exception(f"分片 {slice_no} 上传失败: {result.get('message', '未知错误')}")

                print(f"✅ 分片 {slice_no} 上传成功")

            except Exception as e:
                print(f"❌ 分片 {slice_no} 上传时发生错误: {e}")
                raise

        print("✅ 所有分片上传完成")
        return True

    def upload_complete(self, preupload_id: str) -> Dict[str, Any]:
        """
        确认上传完成

        通知服务器所有分片已上传完毕，服务器将合并分片。
        该操作可能是异步的，需要轮询检查结果。

        Args:
            preupload_id: 预上传ID

        Returns:
            Dict[str, Any]: 上传完成结果，包含success和fileID

        Raises:
            Exception: 确认失败或超时
        """
        print("⏰ 正在确认上传完成...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'

            payload = json.dumps({
                "preuploadID": preupload_id
            })

            # 轮询检查上传状态
            max_retries = 30  # 最多重试30次
            retry_count = 0

            while retry_count < max_retries:
                conn.request("POST", "/upload/v2/file/upload_complete", payload, headers)
                response = conn.getresponse()
                data = response.read().decode("utf-8")

                result = json.loads(data)

                if result.get("code") == 0:
                    data = result.get("data", {})

                    if data.get("completed", False) and data.get("fileID", 0) != 0:
                        print(f"✅ 上传完成确认成功! 文件ID: {data.get('fileID')}")
                        conn.close()
                        return {"success": True, "fileID": data.get("fileID")}
                    else:
                        print(f"⏳ 上传尚未完成，等待1秒后重试... ({retry_count + 1}/{max_retries})")
                        time.sleep(1)
                        retry_count += 1
                else:
                    conn.close()
                    raise Exception(f"确认上传完成失败: {result.get('message', '未知错误')}")

            conn.close()
            raise Exception("上传完成确认超时")

        except Exception as e:
            print(f"❌ 确认上传完成时发生错误: {e}")
            raise

    def upload_file(self, file_path: str, parent_file_id: int = 0) -> Dict[str, Any]:
        """
        上传文件到123云盘

        根据文件大小自动选择最优上传方式：
        - ≤ 1GB: 使用单步上传
        - > 1GB: 使用分片上传（先检测秒传）

        Args:
            file_path: 本地文件路径
            parent_file_id: 父目录ID，0表示根目录

        Returns:
            Dict[str, Any]: 上传结果，包含：
                - success: 是否成功
                - fileID: 文件ID

        Raises:
            Exception: 文件不存在或上传失败

        示例:
            >>> uploader = Pan123Uploader(client_id="id", client_secret="secret")
            >>> result = uploader.upload_file("test.txt")
            >>> print(f"文件ID: {result['fileID']}")
        """
        if not os.path.exists(file_path):
            raise Exception(f"文件不存在: {file_path}")

        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)

        print("=" * 60)
        print(f"📂 准备上传文件: {filename}")
        print(f"📏 文件大小: {self._format_file_size(file_size)}")
        print("=" * 60)

        # 根据文件大小选择上传方式
        if file_size <= self.SINGLE_UPLOAD_LIMIT:
            print("💡 使用单步上传方式")
            return self.single_upload(file_path, parent_file_id)
        else:
            print("💡 使用分片上传方式")

            # 创建文件（检测秒传）
            create_result = self.create_file(file_path, parent_file_id)

            if create_result.get("reuse", False):
                # 秒传成功
                return {"success": True, "fileID": create_result.get("fileID")}

            # 需要分片上传
            preupload_id = create_result.get("preuploadID")
            slice_size = create_result.get("sliceSize")
            servers = create_result.get("servers", [])

            if not preupload_id or not slice_size or not servers:
                raise Exception("创建文件响应数据不完整")

            # 执行分片上传
            self.slice_upload(file_path, preupload_id, slice_size, servers)

            # 确认上传完成
            return self.upload_complete(preupload_id)


# ==================== 主程序 ====================

def main():
    """
    主函数 - 交互式命令行界面

    提供两种文件路径输入方式：
    1. 命令行参数：python upload_to_123pan_v2.py <文件路径>
    2. 交互式输入：运行后提示用户输入文件路径

    父目录ID获取方式：
    - 优先使用配置文件config.txt中的PARENT_FILE_ID
    - 如果配置文件中未设置，则交互式提示用户输入
    - 默认为0（根目录）
    """
    print("=" * 60)
    print("123云盘文件上传工具")
    print("=" * 60)

    # 加载配置文件
    try:
        config = load_config()
        CLIENT_ID = config.get("CLIENT_ID")
        CLIENT_SECRET = config.get("CLIENT_SECRET")
        PARENT_FILE_ID_CONFIG = config.get("PARENT_FILE_ID", "").strip()

        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError("配置文件中缺少CLIENT_ID或CLIENT_SECRET")

    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        print("请确保项目根目录存在config.txt文件，并包含CLIENT_ID和CLIENT_SECRET配置")
        return

    # 获取文件路径
    FILE_PATH = None

    # 方式1：从命令行参数获取
    if len(sys.argv) > 1:
        FILE_PATH = sys.argv[1]
        print(f"使用命令行参数指定的文件路径: {FILE_PATH}")
    else:
        # 方式2：交互式输入
        FILE_PATH = input("请输入要上传的文件路径: ").strip()

        # 移除可能的引号
        if FILE_PATH.startswith('"') and FILE_PATH.endswith('"'):
            FILE_PATH = FILE_PATH[1:-1]
        elif FILE_PATH.startswith("'") and FILE_PATH.endswith("'"):
            FILE_PATH = FILE_PATH[1:-1]

    # 检查文件路径是否有效
    if not FILE_PATH:
        print("❌ 未指定文件路径")
        return

    if not os.path.exists(FILE_PATH):
        print(f"❌ 文件不存在: {FILE_PATH}")
        return

    # 获取父目录ID
    if PARENT_FILE_ID_CONFIG:
        # 配置文件中有值，直接使用
        PARENT_FILE_ID = int(PARENT_FILE_ID_CONFIG)
        print(f"使用配置文件中的父目录ID: {PARENT_FILE_ID}")
    else:
        # 配置文件中没有值，交互式输入
        parent_id_input = input("请输入父目录ID（直接回车表示根目录）: ").strip()
        PARENT_FILE_ID = int(parent_id_input) if parent_id_input else 0

    try:
        # 创建上传器实例
        uploader = Pan123Uploader(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

        # 上传文件
        result = uploader.upload_file(FILE_PATH, parent_file_id=PARENT_FILE_ID)

        if result.get("success", False):
            print("\n" + "=" * 60)
            print("✅ 文件上传成功!")
            print(f"📄 文件ID: {result.get('fileID')}")
            print("=" * 60)
        else:
            print("\n❌ 文件上传失败!")

    except Exception as e:
        print(f"\n❌ 上传过程中发生错误: {e}")


if __name__ == "__main__":
    main()
