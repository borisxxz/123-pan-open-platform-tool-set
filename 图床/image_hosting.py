#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
123云盘图床管理工具

支持功能：
- 图片管理（删除、移动、列表、详情）
- 创建目录
- 上传图片（支持秒传和分片上传）
- 从云盘复制图片到图床
- 图片离线迁移

作者: Assistant
日期: 2025/10/01
基于: 123云盘开放平台官方文档 v1
"""

import json
import http.client
import sys
import os
import hashlib
import math
import time
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from codecs import encode
import mimetypes


def load_config(config_path: str = None) -> Dict[str, str]:
    """
    从配置文件加载配置信息

    Args:
        config_path: 配置文件路径，默认为项目根目录的config.txt

    Returns:
        配置字典
    """
    if config_path is None:
        # 获取当前脚本所在目录的父目录（项目根目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        config_path = os.path.join(project_root, "config.txt")

    config = {}

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

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


class ImageHostingManager:
    """123云盘图床管理器"""

    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        """
        初始化图床管理器

        Args:
            access_token: 访问令牌（可选，如果提供则直接使用）
            client_id: 客户端ID（当access_token为空时使用）
            client_secret: 客户端密钥（当access_token为空时使用）
        """
        self.api_base = "open-api.123pan.com"

        # 支持的图片格式
        self.SUPPORTED_FORMATS = ['png', 'gif', 'jpeg', 'jpg', 'tiff', 'tif', 'webp', 'svg', 'bmp']
        # 图片大小限制（100MB）
        self.MAX_IMAGE_SIZE = 100 * 1024 * 1024

        if access_token:
            self.access_token = access_token
        elif client_id and client_secret:
            self.access_token = self._get_access_token(client_id, client_secret)
        else:
            raise ValueError("必须提供access_token或者client_id和client_secret")

    def _get_access_token(self, client_id: str, client_secret: str) -> str:
        """
        获取访问令牌

        Args:
            client_id: 客户端ID
            client_secret: 客户端密钥

        Returns:
            访问令牌
        """
        print("正在获取访问令牌...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)

            payload = json.dumps({
                "clientID": client_id,
                "clientSecret": client_secret
            })

            headers = {
                'Platform': 'open_platform',
                'Content-Type': 'application/json'
            }

            conn.request("POST", "/api/v1/access_token", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

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
        """获取通用请求头"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Platform': 'open_platform',
            'Content-Type': 'application/json'
        }

    def _format_file_size(self, size: int) -> str:
        """格式化文件大小"""
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
        """计算文件MD5值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _calculate_slice_md5(self, file_path: str, start: int, size: int) -> str:
        """计算文件分片的MD5值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = size
            while remaining > 0:
                chunk_size = min(4096, remaining)
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_md5.update(chunk)
                remaining -= len(chunk)
        return hash_md5.hexdigest()

    # ==================== 图片管理 ====================

    def delete_images(self, file_ids: List[str]) -> bool:
        """
        删除图片

        Args:
            file_ids: 文件ID数组，最多100个

        Returns:
            成功返回True
        """
        if len(file_ids) > 100:
            print("❌ 一次最多删除100个文件")
            return False

        print(f"🗑️  正在删除 {len(file_ids)} 个图片...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({"fileIDs": file_ids})

            conn.request("POST", "/api/v1/oss/file/delete", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                print(f"✅ 删除成功")
                return True
            else:
                print(f"❌ 删除失败: {result.get('message', '未知错误')}")
                return False

        except Exception as e:
            print(f"❌ 删除图片时发生错误: {e}")
            return False

    def move_images(self, file_ids: List[str], to_parent_file_id: str) -> bool:
        """
        移动图片

        Args:
            file_ids: 文件ID数组，最多100个
            to_parent_file_id: 目标文件夹ID，移动到根目录时填写空字符串

        Returns:
            成功返回True
        """
        if len(file_ids) > 100:
            print("❌ 一次最多移动100个文件")
            return False

        print(f"📦 正在移动 {len(file_ids)} 个图片...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({
                "fileIDs": file_ids,
                "toParentFileID": to_parent_file_id
            })

            conn.request("POST", "/api/v1/oss/file/move", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                print(f"✅ 移动成功")
                return True
            else:
                print(f"❌ 移动失败: {result.get('message', '未知错误')}")
                return False

        except Exception as e:
            print(f"❌ 移动图片时发生错误: {e}")
            return False

    def get_image_list(self, parent_file_id: str = "", limit: int = 100,
                      last_file_id: str = None, start_time: int = None,
                      end_time: int = None) -> Optional[Dict[str, Any]]:
        """
        获取图片列表

        Args:
            parent_file_id: 父目录ID，空表示根目录
            limit: 每页数量，最大100
            last_file_id: 翻页查询时的起始文件ID
            start_time: 筛选开始时间（时间戳）
            end_time: 筛选结束时间（时间戳）

        Returns:
            图片列表数据
        """
        print(f"📋 正在获取图片列表...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = {
                "parentFileId": parent_file_id,
                "limit": limit,
                "type": 1
            }

            if last_file_id:
                payload["lastFileId"] = last_file_id
            if start_time:
                payload["startTime"] = start_time
            if end_time:
                payload["endTime"] = end_time

            payload_json = json.dumps(payload)

            conn.request("POST", "/api/v1/oss/file/list", payload_json, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                file_list = data_info.get("fileList", [])
                last_id = data_info.get("lastFileId", "-1")

                print(f"✅ 获取到 {len(file_list)} 个文件/文件夹")

                if file_list:
                    print("\n" + "=" * 120)
                    print(f"{'文件名':<30} {'类型':<6} {'大小':<12} {'状态':<8} {'流量':<12} {'更新时间':<20}")
                    print("=" * 120)

                    for file_info in file_list:
                        filename = file_info.get("filename", "")[:28]
                        file_type = "文件夹" if file_info.get("type") == 1 else "文件"
                        file_size = self._format_file_size(file_info.get("size", 0))
                        status = "正常" if file_info.get("status", 0) <= 100 else "驳回"
                        traffic = self._format_file_size(file_info.get("totalTraffic", 0))
                        update_time = file_info.get("updateAt", "")

                        print(f"{filename:<30} {file_type:<6} {file_size:<12} {status:<8} {traffic:<12} {update_time:<20}")
                        print(f"  ID: {file_info.get('fileId', '')}  下载链接: {file_info.get('downloadURL', '')[:50]}")

                return data_info
            else:
                print(f"❌ 获取图片列表失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取图片列表时发生错误: {e}")
            return None

    def get_image_detail(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        获取图片详情

        Args:
            file_id: 文件ID

        Returns:
            图片详情数据
        """
        print(f"🔍 正在获取图片详情...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            conn.request("GET", f"/api/v1/oss/file/detail?fileID={file_id}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                file_info = result.get("data", {})

                print("\n" + "=" * 80)
                print("📄 图片详细信息")
                print("=" * 80)
                print(f"文件ID: {file_info.get('fileId', '')}")
                print(f"文件名: {file_info.get('filename', '')}")
                print(f"类型: {'文件夹' if file_info.get('type') == 1 else '文件'}")
                print(f"大小: {self._format_file_size(file_info.get('size', 0))}")
                print(f"MD5: {file_info.get('etag', '')}")
                print(f"状态: {'正常' if file_info.get('status', 0) <= 100 else '审核驳回'}")
                print(f"流量统计: {self._format_file_size(file_info.get('totalTraffic', 0))}")
                print(f"父目录ID: {file_info.get('parentFileId', '')}")
                print(f"创建时间: {file_info.get('createAt', '')}")
                print(f"更新时间: {file_info.get('updateAt', '')}")
                print(f"下载链接: {file_info.get('downloadURL', '')}")
                print(f"自定义域名链接: {file_info.get('userSelfURL', '')}")
                print("=" * 80)

                return file_info
            else:
                print(f"❌ 获取图片详情失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取图片详情时发生错误: {e}")
            return None

    # ==================== 目录管理 ====================

    def create_directory(self, dir_name: str, parent_id: str = "") -> Optional[str]:
        """
        创建目录

        Args:
            dir_name: 目录名
            parent_id: 父目录ID，上传到根目录时为空

        Returns:
            目录ID，失败返回None
        """
        print(f"📁 正在创建目录: {dir_name}")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({
                "name": dir_name,
                "parentID": parent_id,
                "type": 1
            })

            conn.request("POST", "/upload/v1/oss/file/mkdir", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                dir_list = result.get("data", {}).get("list", [])
                if dir_list:
                    dir_id = dir_list[0].get("dirID")
                    print(f"✅ 目录创建成功，ID: {dir_id}")
                    return dir_id
                else:
                    print("❌ 目录创建失败：响应数据为空")
                    return None
            else:
                print(f"❌ 创建目录失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 创建目录时发生错误: {e}")
            return None

    # ==================== 图片上传 ====================

    def create_file(self, file_path: str, parent_file_id: str = "") -> Dict[str, Any]:
        """
        创建文件（检测秒传）

        Args:
            file_path: 本地文件路径
            parent_file_id: 父目录ID，空表示根目录

        Returns:
            创建文件的响应数据
        """
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # 检查文件格式
        file_ext = filename.split('.')[-1].lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            raise Exception(f"不支持的图片格式: {file_ext}，支持的格式: {', '.join(self.SUPPORTED_FORMATS)}")

        # 检查文件大小
        if file_size > self.MAX_IMAGE_SIZE:
            raise Exception(f"图片大小 {self._format_file_size(file_size)} 超过最大限制 100MB")

        print(f"📊 正在计算文件MD5...")
        file_md5 = self._calculate_md5(file_path)

        print(f"📝 正在创建文件: {filename} (大小: {self._format_file_size(file_size)})")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({
                "parentFileID": parent_file_id,
                "filename": filename,
                "etag": file_md5,
                "size": file_size,
                "type": 1
            })

            conn.request("POST", "/upload/v1/oss/file/create", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})

                if data_info.get("reuse", False):
                    print(f"✅ 文件秒传成功! 文件ID: {data_info.get('fileID')}")
                    return {"success": True, "reuse": True, "fileID": data_info.get("fileID")}
                else:
                    print("需要上传文件内容")
                    return {
                        "success": True,
                        "reuse": False,
                        "preuploadID": data_info.get("preuploadID"),
                        "sliceSize": data_info.get("sliceSize")
                    }
            else:
                raise Exception(f"创建文件失败: {result.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 创建文件时发生错误: {e}")
            raise

    def get_upload_url(self, preupload_id: str, slice_no: int) -> Optional[str]:
        """
        获取上传地址

        Args:
            preupload_id: 预上传ID
            slice_no: 分片序号，从1开始

        Returns:
            上传URL
        """
        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({
                "preuploadID": preupload_id,
                "sliceNo": slice_no
            })

            conn.request("POST", "/upload/v1/oss/file/get_upload_url", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                url = result.get("data", {}).get("presignedURL")
                return url
            else:
                print(f"❌ 获取上传地址失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取上传地址时发生错误: {e}")
            return None

    def upload_slice(self, upload_url: str, file_path: str, start: int, size: int) -> bool:
        """
        上传分片到预签名URL

        Args:
            upload_url: 预签名上传URL
            file_path: 文件路径
            start: 分片起始位置
            size: 分片大小

        Returns:
            成功返回True
        """
        try:
            # 解析URL
            parsed = urlparse(upload_url)
            host = parsed.netloc
            path = parsed.path + '?' + parsed.query if parsed.query else parsed.path

            # 读取分片数据
            with open(file_path, 'rb') as f:
                f.seek(start)
                slice_data = f.read(size)

            # 发送PUT请求
            conn = http.client.HTTPSConnection(host)
            headers = {'Content-Type': 'application/octet-stream'}

            conn.request("PUT", path, slice_data, headers)
            response = conn.getresponse()
            response.read()  # 读取响应内容
            conn.close()

            if response.status == 200:
                return True
            else:
                print(f"❌ 上传分片失败，状态码: {response.status}")
                return False

        except Exception as e:
            print(f"❌ 上传分片时发生错误: {e}")
            return False

    def upload_complete(self, preupload_id: str) -> Dict[str, Any]:
        """
        确认上传完成

        Args:
            preupload_id: 预上传ID

        Returns:
            上传完成结果
        """
        print("⏰ 正在确认上传完成...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({"preuploadID": preupload_id})

            conn.request("POST", "/upload/v1/oss/file/upload_complete", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})

                if data_info.get("async", False):
                    # 需要异步轮询
                    print("需要异步轮询上传结果...")
                    return self.poll_upload_result(preupload_id)
                elif data_info.get("completed", False) and data_info.get("fileID"):
                    print(f"✅ 上传完成! 文件ID: {data_info.get('fileID')}")
                    return {"success": True, "fileID": data_info.get("fileID")}
                else:
                    raise Exception("上传未完成")
            else:
                raise Exception(f"确认上传完成失败: {result.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 确认上传完成时发生错误: {e}")
            raise

    def poll_upload_result(self, preupload_id: str, max_retries: int = 30) -> Dict[str, Any]:
        """
        异步轮询获取上传结果

        Args:
            preupload_id: 预上传ID
            max_retries: 最大重试次数

        Returns:
            上传结果
        """
        print("🔄 开始轮询上传结果...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({"preuploadID": preupload_id})

            for i in range(max_retries):
                conn.request("POST", "/upload/v1/oss/file/upload_async_result", payload, headers)
                response = conn.getresponse()
                data = response.read().decode("utf-8")

                result = json.loads(data)

                if result.get("code") == 0:
                    data_info = result.get("data", {})

                    if data_info.get("completed", False):
                        file_id = data_info.get("fileID")
                        print(f"✅ 上传完成! 文件ID: {file_id}")
                        conn.close()
                        return {"success": True, "fileID": file_id}
                    else:
                        print(f"⏳ 上传处理中... ({i+1}/{max_retries})")
                        time.sleep(1)
                else:
                    conn.close()
                    raise Exception(f"轮询失败: {result.get('message', '未知错误')}")

            conn.close()
            raise Exception("轮询超时，上传可能未完成")

        except Exception as e:
            print(f"❌ 轮询上传结果时发生错误: {e}")
            raise

    def upload_image(self, file_path: str, parent_file_id: str = "") -> Dict[str, Any]:
        """
        上传图片到图床

        Args:
            file_path: 本地文件路径
            parent_file_id: 父目录ID，空表示根目录

        Returns:
            上传结果
        """
        if not os.path.exists(file_path):
            raise Exception(f"文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        print(f"🚀 准备上传图片: {filename}")
        print(f"📏 文件大小: {self._format_file_size(file_size)}")

        # 创建文件（检测秒传）
        create_result = self.create_file(file_path, parent_file_id)

        if create_result.get("reuse", False):
            # 秒传成功
            return {"success": True, "fileID": create_result.get("fileID")}

        # 需要上传
        preupload_id = create_result.get("preuploadID")
        slice_size = create_result.get("sliceSize")

        if not preupload_id or not slice_size:
            raise Exception("创建文件响应数据不完整")

        # 计算分片数量
        total_slices = math.ceil(file_size / slice_size)
        print(f"📦 开始分片上传，总分片数: {total_slices}")

        # 上传每个分片
        for slice_no in range(1, total_slices + 1):
            start_pos = (slice_no - 1) * slice_size
            current_slice_size = min(slice_size, file_size - start_pos)

            print(f"⬆️  正在上传分片 {slice_no}/{total_slices} (大小: {self._format_file_size(current_slice_size)})")

            # 获取上传地址
            upload_url = self.get_upload_url(preupload_id, slice_no)
            if not upload_url:
                raise Exception(f"获取分片 {slice_no} 上传地址失败")

            # 上传分片
            if not self.upload_slice(upload_url, file_path, start_pos, current_slice_size):
                raise Exception(f"分片 {slice_no} 上传失败")

            print(f"✅ 分片 {slice_no} 上传成功")

        print("✅ 所有分片上传完成")

        # 确认上传完成
        return self.upload_complete(preupload_id)

    # ==================== 复制云盘图片 ====================

    def create_copy_task(self, file_ids: List[str], to_parent_file_id: str = "") -> Optional[str]:
        """
        创建复制任务（从云盘复制到图床）

        Args:
            file_ids: 文件ID数组，最多100个
            to_parent_file_id: 目标图床文件夹ID，空表示根目录

        Returns:
            任务ID
        """
        if len(file_ids) > 100:
            print("❌ 一次最多复制100个文件")
            return None

        print(f"📋 正在创建复制任务...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({
                "fileIDs": file_ids,
                "toParentFileID": to_parent_file_id,
                "sourceType": 1,
                "type": 1
            })

            conn.request("POST", "/api/v1/oss/source/copy", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                task_id = result.get("data", {}).get("taskID")
                print(f"✅ 复制任务创建成功，任务ID: {task_id}")
                return task_id
            else:
                print(f"❌ 创建复制任务失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 创建复制任务时发生错误: {e}")
            return None

    def get_copy_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取复制任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态数据
        """
        print(f"🔍 正在查询复制任务状态...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            conn.request("GET", f"/api/v1/oss/source/copy/process?taskID={task_id}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                status = data_info.get("status", 0)
                fail_msg = data_info.get("failMsg", "")

                status_text = {1: "进行中", 2: "结束", 3: "失败", 4: "等待"}.get(status, "未知")
                print(f"任务状态: {status_text}")
                if fail_msg:
                    print(f"失败原因: {fail_msg}")

                return data_info
            else:
                print(f"❌ 获取任务状态失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取任务状态时发生错误: {e}")
            return None

    def get_copy_failed_files(self, task_id: str, limit: int = 100, page: int = 1) -> Optional[Dict[str, Any]]:
        """
        获取复制失败文件列表

        Args:
            task_id: 任务ID
            limit: 每页数量
            page: 页码

        Returns:
            失败文件列表
        """
        print(f"📋 正在获取复制失败文件列表...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            conn.request("GET", f"/api/v1/oss/source/copy/fail?taskID={task_id}&limit={limit}&page={page}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                fail_list = data_info.get("list", [])
                total = data_info.get("total", 0)

                print(f"✅ 共有 {total} 个失败文件")

                if fail_list:
                    print("\n失败文件列表:")
                    for item in fail_list:
                        print(f"  - 文件ID: {item.get('fileId')}, 文件名: {item.get('filename')}")

                return data_info
            else:
                print(f"❌ 获取失败文件列表失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取失败文件列表时发生错误: {e}")
            return None

    # ==================== 图床离线迁移 ====================

    def create_offline_task(self, url: str, file_name: str = None,
                           business_dir_id: str = None, callback_url: str = None) -> Optional[int]:
        """
        创建离线迁移任务

        Args:
            url: 下载资源地址（http/https）
            file_name: 自定义文件名（需携带图片格式）
            business_dir_id: 目标目录ID
            callback_url: 回调地址

        Returns:
            任务ID
        """
        print(f"🌐 正在创建离线迁移任务...")
        print(f"🔗 URL: {url}")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = {"url": url, "type": 1}
            if file_name:
                payload["fileName"] = file_name
            if business_dir_id:
                payload["businessDirID"] = business_dir_id
            if callback_url:
                payload["callBackUrl"] = callback_url

            payload_json = json.dumps(payload)

            conn.request("POST", "/api/v1/oss/offline/download", payload_json, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                task_id = result.get("data", {}).get("taskID")
                print(f"✅ 离线迁移任务创建成功，任务ID: {task_id}")
                return task_id
            else:
                print(f"❌ 创建离线迁移任务失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 创建离线迁移任务时发生错误: {e}")
            return None

    def get_offline_task_status(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        获取离线迁移任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态数据
        """
        print(f"🔍 正在查询离线迁移任务状态...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            conn.request("GET", f"/api/v1/oss/offline/download/process?taskID={task_id}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                status = data_info.get("status", 0)
                process = data_info.get("process", 0)

                status_text = {0: "进行中", 1: "下载失败", 2: "下载成功", 3: "重试中"}.get(status, "未知")
                print(f"任务状态: {status_text}")
                print(f"进度: {process}%")

                return data_info
            else:
                print(f"❌ 获取任务状态失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取任务状态时发生错误: {e}")
            return None


def main():
    """主函数"""
    # 从配置文件加载配置
    try:
        config = load_config()
        CLIENT_ID = config.get("CLIENT_ID")
        CLIENT_SECRET = config.get("CLIENT_SECRET")

        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError("配置文件中缺少CLIENT_ID或CLIENT_SECRET")
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        print("请确保项目根目录存在config.txt文件，并包含CLIENT_ID和CLIENT_SECRET配置")
        return

    try:
        # 创建图床管理器实例
        manager = ImageHostingManager(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

        print("=" * 60)
        print("123云盘图床管理工具")
        print("=" * 60)

        while True:
            print("\n请选择操作:")
            print("1. 查看图片列表")
            print("2. 查看图片详情")
            print("3. 删除图片")
            print("4. 移动图片")
            print("5. 创建目录")
            print("6. 上传图片")
            print("7. 从云盘复制图片到图床")
            print("8. 查询复制任务状态")
            print("9. 创建离线迁移任务")
            print("10. 查询离线迁移任务状态")
            print("0. 退出")

            choice = input("\n请输入选项 (0-10): ").strip()

            if choice == "0":
                print("👋 退出程序")
                break

            elif choice == "1":
                # 查看图片列表
                parent_id = input("请输入父目录ID (直接回车表示根目录): ").strip()
                manager.get_image_list(parent_file_id=parent_id)

            elif choice == "2":
                # 查看图片详情
                file_id = input("请输入文件ID: ").strip()
                if file_id:
                    manager.get_image_detail(file_id)
                else:
                    print("❌ 文件ID不能为空")

            elif choice == "3":
                # 删除图片
                print("请输入要删除的文件ID，每行一个，输入空行结束:")
                file_ids = []
                while True:
                    file_id = input().strip()
                    if not file_id:
                        break
                    file_ids.append(file_id)

                if file_ids:
                    manager.delete_images(file_ids)
                else:
                    print("❌ 未输入任何文件ID")

            elif choice == "4":
                # 移动图片
                print("请输入要移动的文件ID，每行一个，输入空行结束:")
                file_ids = []
                while True:
                    file_id = input().strip()
                    if not file_id:
                        break
                    file_ids.append(file_id)

                if file_ids:
                    target_id = input("请输入目标文件夹ID (直接回车表示根目录): ").strip()
                    manager.move_images(file_ids, target_id)
                else:
                    print("❌ 未输入任何文件ID")

            elif choice == "5":
                # 创建目录
                dir_name = input("请输入目录名: ").strip()
                if dir_name:
                    parent_id = input("请输入父目录ID (直接回车表示根目录): ").strip()
                    manager.create_directory(dir_name, parent_id)
                else:
                    print("❌ 目录名不能为空")

            elif choice == "6":
                # 上传图片
                file_path = input("请输入图片文件路径: ").strip().replace('"', '')
                if file_path and os.path.exists(file_path):
                    parent_id = input("请输入父目录ID (直接回车表示根目录): ").strip()
                    try:
                        manager.upload_image(file_path, parent_id)
                    except Exception as e:
                        print(f"❌ 上传失败: {e}")
                else:
                    print("❌ 文件路径无效或文件不存在")

            elif choice == "7":
                # 从云盘复制图片到图床
                print("请输入要复制的云盘文件ID，每行一个，输入空行结束:")
                file_ids = []
                while True:
                    file_id = input().strip()
                    if not file_id:
                        break
                    file_ids.append(file_id)

                if file_ids:
                    target_id = input("请输入目标图床文件夹ID (直接回车表示根目录): ").strip()
                    task_id = manager.create_copy_task(file_ids, target_id)
                    if task_id:
                        print(f"✅ 任务已创建，可使用选项8查询任务状态")
                else:
                    print("❌ 未输入任何文件ID")

            elif choice == "8":
                # 查询复制任务状态
                task_id = input("请输入任务ID: ").strip()
                if task_id:
                    status_info = manager.get_copy_task_status(task_id)
                    if status_info and status_info.get("status") == 3:
                        # 失败了，查询失败文件列表
                        print("\n正在获取失败文件列表...")
                        manager.get_copy_failed_files(task_id)
                else:
                    print("❌ 任务ID不能为空")

            elif choice == "9":
                # 创建离线迁移任务
                url = input("请输入图片URL: ").strip()
                if url:
                    file_name = input("请输入自定义文件名（可选，需携带扩展名）: ").strip()
                    dir_id = input("请输入目标目录ID（可选）: ").strip()

                    task_id = manager.create_offline_task(
                        url,
                        file_name if file_name else None,
                        dir_id if dir_id else None
                    )
                    if task_id:
                        print(f"✅ 任务已创建，可使用选项10查询任务状态")
                else:
                    print("❌ URL不能为空")

            elif choice == "10":
                # 查询离线迁移任务状态
                task_id = input("请输入任务ID: ").strip()
                if task_id.isdigit():
                    manager.get_offline_task_status(int(task_id))
                else:
                    print("❌ 任务ID必须是数字")

            else:
                print("❌ 无效的选项，请重新选择")

    except Exception as e:
        print(f"\n❌ 程序运行时发生错误: {e}")


if __name__ == "__main__":
    main()
