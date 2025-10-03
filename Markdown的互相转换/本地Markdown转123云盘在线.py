#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown文件转123网盘工具（独立Windows版本）

功能：
- 解析Markdown文件中的图片和附件链接
- 将本地图片上传到123网盘图床
- 将本地附件上传到123网盘直链目录
- 替换Markdown中的文件链接为网盘链接
- 支持批量处理多个Markdown文件

作者: Assistant
日期: 2025/10/03
版本: v2.0 - 修复版
"""

import os
import re
import sys
import shutil
import argparse
import json
import http.client
import hashlib
import math
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any
from urllib.parse import urlparse, unquote


def load_config(config_path: str = None) -> Dict[str, str]:
    """从配置文件加载配置信息"""
    if config_path is None:
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
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config
    except Exception as e:
        raise Exception(f"读取配置文件失败: {e}")


class Pan123Manager:
    """123云盘管理器基类"""

    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        self.api_base = "open-api.123pan.com"

        if access_token:
            self.access_token = access_token
        elif client_id and client_secret:
            self.access_token = self._get_access_token(client_id, client_secret)
        else:
            raise ValueError("必须提供access_token或者client_id和client_secret")

    def _get_access_token(self, client_id: str, client_secret: str) -> str:
        """获取访问令牌"""
        print("正在获取访问令牌...")
        conn = None
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
            result = json.loads(data)

            if result.get("code") == 0:
                access_token = result.get("data", {}).get("accessToken")
                if access_token:
                    print("访问令牌获取成功")
                    return access_token
                else:
                    raise Exception("响应中未找到访问令牌")
            else:
                raise Exception(f"获取访问令牌失败: {result.get('message', '未知错误')}")
        except Exception as e:
            print(f"获取访问令牌时发生错误: {e}")
            raise
        finally:
            if conn:
                conn.close()

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

    def _calculate_slice_md5(self, data: bytes) -> str:
        """计算分片MD5值"""
        return hashlib.md5(data).hexdigest()

    def find_directory(self, dir_name: str, parent_id: str = "") -> Optional[str]:
        """查找目录"""
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()
            payload = json.dumps({
                "parentFileID": parent_id,
                "limit": 100,
                "type": 1
            })
            conn.request("POST", "/api/v1/oss/file/list", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            result = json.loads(data)

            if result.get("code") == 0:
                file_list = result.get("data", {}).get("fileList", [])
                for file_info in file_list:
                    if file_info.get("type") == 1 and file_info.get("filename", "").lower() == dir_name.lower():
                        print(f"找到已存在的目录: {dir_name}")
                        return file_info.get("fileId")
                return None
            else:
                print(f"查找目录失败: {result.get('message', '未知错误')}")
                return None
        except Exception as e:
            print(f"查找目录时发生错误: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def create_directory(self, dir_name: str, parent_id: str = "") -> Optional[str]:
        """创建目录"""
        print(f"正在创建目录: {dir_name}")
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()
            payload = json.dumps({
                "name": [dir_name],
                "parentID": parent_id,
                "type": 1
            })
            conn.request("POST", "/upload/v1/oss/file/mkdir", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            result = json.loads(data)

            if result.get("code") == 0:
                dir_list = result.get("data", {}).get("list", [])
                if dir_list:
                    dir_id = dir_list[0].get("dirID")
                    print(f"目录创建成功，ID: {dir_id}")
                    return dir_id
                else:
                    print("目录创建失败：响应数据为空")
                    return None
            else:
                print(f"创建目录失败: {result.get('message', '未知错误')}")
                return None
        except Exception as e:
            print(f"创建目录时发生错误: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_or_create_directory(self, dir_name: str, parent_id: str = "") -> Optional[str]:
        """获取或创建目录"""
        dir_id = self.find_directory(dir_name, parent_id)
        if dir_id:
            return dir_id
        return self.create_directory(dir_name, parent_id)


class ImageHostingManager(Pan123Manager):
    """123云盘图床管理器"""

    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        super().__init__(access_token, client_id, client_secret)
        self.SUPPORTED_FORMATS = ['png', 'gif', 'jpeg', 'jpg', 'tiff', 'tif', 'webp', 'svg', 'bmp']
        self.MAX_IMAGE_SIZE = 100 * 1024 * 1024  # 100MB

    def create_file(self, file_path: str, parent_file_id: str = "") -> Dict[str, Any]:
        """创建文件（检测秒传）"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # 检查文件格式
        file_ext = filename.split('.')[-1].lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            raise Exception(f"不支持的图片格式: {file_ext}")

        # 检查文件大小
        if file_size > self.MAX_IMAGE_SIZE:
            raise Exception(f"图片大小超过最大限制 100MB")

        print(f"正在计算文件MD5...")
        file_md5 = self._calculate_md5(file_path)
        print(f"正在创建文件: {filename}")

        conn = None
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
            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                if data_info.get("reuse", False):
                    print(f"文件秒传成功! 文件ID: {data_info.get('fileID')}")
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
            print(f"创建文件时发生错误: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_upload_url(self, preupload_id: str, slice_no: int) -> Optional[str]:
        """获取上传地址"""
        conn = None
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
            result = json.loads(data)

            if result.get("code") == 0:
                return result.get("data", {}).get("presignedURL")
            else:
                print(f"获取上传地址失败: {result.get('message', '未知错误')}")
                return None
        except Exception as e:
            print(f"获取上传地址时发生错误: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def upload_slice(self, upload_url: str, file_path: str, start: int, size: int) -> bool:
        """上传分片到预签名URL"""
        conn = None
        try:
            parsed = urlparse(upload_url)
            host = parsed.netloc
            path = parsed.path + ('?' + parsed.query if parsed.query else '')

            with open(file_path, 'rb') as f:
                f.seek(start)
                slice_data = f.read(size)

            conn = http.client.HTTPSConnection(host)
            headers = {'Content-Type': 'application/octet-stream'}
            conn.request("PUT", path, slice_data, headers)
            response = conn.getresponse()
            response.read()

            return response.status == 200
        except Exception as e:
            print(f"上传分片时发生错误: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def upload_complete(self, preupload_id: str) -> Dict[str, Any]:
        """确认上传完成"""
        print("正在确认上传完成...")
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()
            payload = json.dumps({"preuploadID": preupload_id})

            conn.request("POST", "/upload/v1/oss/file/upload_complete", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                if data_info.get("async", False):
                    print("需要异步轮询上传结果...")
                    return self.poll_upload_result(preupload_id)
                elif data_info.get("completed", False) and data_info.get("fileID"):
                    print(f"上传完成! 文件ID: {data_info.get('fileID')}")
                    return {"success": True, "fileID": data_info.get("fileID")}
                else:
                    raise Exception("上传未完成")
            else:
                raise Exception(f"确认上传完成失败: {result.get('message', '未知错误')}")
        except Exception as e:
            print(f"确认上传完成时发生错误: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def poll_upload_result(self, preupload_id: str, max_retries: int = 30) -> Dict[str, Any]:
        """异步轮询获取上传结果"""
        print("开始轮询上传结果...")
        conn = None
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
                        print(f"上传完成! 文件ID: {file_id}")
                        return {"success": True, "fileID": file_id}
                    else:
                        print(f"上传处理中... ({i+1}/{max_retries})")
                        time.sleep(1)
                else:
                    raise Exception(f"轮询失败: {result.get('message', '未知错误')}")

            raise Exception("轮询超时，上传可能未完成")
        except Exception as e:
            print(f"轮询上传结果时发生错误: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def upload_image(self, file_path: str, parent_file_id: str = "") -> Dict[str, Any]:
        """上传图片到图床"""
        if not os.path.exists(file_path):
            raise Exception(f"文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        print(f"准备上传图片: {filename} (大小: {self._format_file_size(file_size)})")

        # 创建文件（检测秒传）
        create_result = self.create_file(file_path, parent_file_id)

        if create_result.get("reuse", False):
            return {"success": True, "fileID": create_result.get("fileID")}

        # 需要上传
        preupload_id = create_result.get("preuploadID")
        slice_size = create_result.get("sliceSize")

        if not preupload_id or not slice_size:
            raise Exception("创建文件响应数据不完整")

        # 计算分片数量
        total_slices = math.ceil(file_size / slice_size)
        print(f"开始分片上传，总分片数: {total_slices}")

        # 上传每个分片
        for slice_no in range(1, total_slices + 1):
            start_pos = (slice_no - 1) * slice_size
            current_slice_size = min(slice_size, file_size - start_pos)
            print(f"正在上传分片 {slice_no}/{total_slices}")

            upload_url = self.get_upload_url(preupload_id, slice_no)
            if not upload_url:
                raise Exception(f"获取分片 {slice_no} 上传地址失败")

            if not self.upload_slice(upload_url, file_path, start_pos, current_slice_size):
                raise Exception(f"分片 {slice_no} 上传失败")

            print(f"分片 {slice_no} 上传成功")

        print("所有分片上传完成")
        return self.upload_complete(preupload_id)

    def get_image_detail(self, file_id: str) -> Optional[Dict[str, Any]]:
        """获取图片详情"""
        print(f"正在获取图片详情...")
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()
            conn.request("GET", f"/api/v1/oss/file/detail?fileID={file_id}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            result = json.loads(data)

            if result.get("code") == 0:
                return result.get("data", {})
            else:
                print(f"获取图片详情失败: {result.get('message', '未知错误')}")
                return None
        except Exception as e:
            print(f"获取图片详情时发生错误: {e}")
            return None
        finally:
            if conn:
                conn.close()


class DirectLinkManager(Pan123Manager):
    """123网盘直链管理器 - 使用普通文件上传API + 直链API获取下载链接"""

    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        super().__init__(access_token, client_id, client_secret)
        self.MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024 * 1024  # 10GB (普通上传限制)
        self.SINGLE_UPLOAD_LIMIT = 1 * 1024 * 1024 * 1024   # 1GB

    def upload_attachment(self, file_path: str, parent_file_id: int = 0) -> Dict[str, Any]:
        """上传附件到直链目录"""
        if not os.path.exists(file_path):
            raise Exception(f"文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        print(f"准备上传附件: {filename} (大小: {self._format_file_size(file_size)})")

        if file_size > self.MAX_ATTACHMENT_SIZE:
            raise Exception(f"附件大小超过最大限制 10GB")

        # 使用普通文件上传API
        file_id = self._upload_file_v2(file_path, parent_file_id)

        # 获取直链
        direct_url = self._get_direct_link(file_id)

        return {"success": True, "fileID": file_id, "downloadURL": direct_url}

    def _upload_file_v2(self, file_path: str, parent_file_id: int = 0) -> str:
        """使用v2 API上传文件到云盘"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_md5 = self._calculate_md5(file_path)

        print(f"正在创建文件: {filename}")

        # 根据文件大小选择上传方式
        if file_size <= self.SINGLE_UPLOAD_LIMIT:
            return self._single_upload_v2(file_path, parent_file_id)
        else:
            return self._slice_upload_v2(file_path, parent_file_id)

    def _single_upload_v2(self, file_path: str, parent_file_id: int = 0) -> str:
        """单步上传文件（≤1GB）"""
        # 暂不实现，使用分片上传方式统一处理
        return self._slice_upload_v2(file_path, parent_file_id)

    def _slice_upload_v2(self, file_path: str, parent_file_id: int = 0) -> str:
        """分片上传文件"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_md5 = self._calculate_md5(file_path)

        # 创建文件
        conn = None
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
            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                if data_info.get("reuse", False):
                    print(f"文件秒传成功! 文件ID: {data_info.get('fileID')}")
                    return str(data_info.get("fileID"))
                else:
                    preupload_id = data_info.get("preuploadID")
                    slice_size = data_info.get("sliceSize")
                    servers = data_info.get("servers", [])

                    if not servers:
                        raise Exception("未获取到上传服务器")

                    # 上传分片
                    self._upload_slices_v2(file_path, preupload_id, slice_size, file_size, servers[0])

                    # 确认上传完成
                    return self._upload_complete_v2(preupload_id)
            else:
                raise Exception(f"创建文件失败: {result.get('message', '未知错误')}")
        finally:
            if conn:
                conn.close()

    def _upload_slices_v2(self, file_path: str, preupload_id: str, slice_size: int,
                          file_size: int, server: str) -> None:
        """上传文件分片（V2版本使用multipart/form-data）"""
        total_slices = math.ceil(file_size / slice_size)
        print(f"开始分片上传，总分片数: {total_slices}")

        for slice_no in range(1, total_slices + 1):
            start_pos = (slice_no - 1) * slice_size
            current_slice_size = min(slice_size, file_size - start_pos)
            print(f"正在上传分片 {slice_no}/{total_slices}")

            # 读取分片数据并计算MD5
            with open(file_path, 'rb') as f:
                f.seek(start_pos)
                slice_data = f.read(current_slice_size)

            slice_md5 = self._calculate_slice_md5(slice_data)

            # 上传分片
            if not self._upload_slice_v2(server, preupload_id, slice_no, slice_md5, slice_data):
                raise Exception(f"分片 {slice_no} 上传失败")

            print(f"分片 {slice_no} 上传成功")

    def _upload_slice_v2(self, server: str, preupload_id: str, slice_no: int,
                        slice_md5: str, slice_data: bytes) -> bool:
        """上传分片（使用multipart/form-data格式）"""
        conn = None
        try:
            # 解析服务器地址
            parsed = urlparse(server)
            host = parsed.netloc if parsed.netloc else server.replace('http://', '').replace('https://', '')

            # 构建multipart/form-data
            boundary = '----WebKitFormBoundary' + ''.join([chr(ord('a') + i % 26) for i in range(16)])

            # 构建表单数据
            body_parts = []

            # preuploadID字段
            body_parts.append(f'--{boundary}'.encode())
            body_parts.append(b'Content-Disposition: form-data; name="preuploadID"')
            body_parts.append(b'')
            body_parts.append(preupload_id.encode())

            # sliceNo字段
            body_parts.append(f'--{boundary}'.encode())
            body_parts.append(b'Content-Disposition: form-data; name="sliceNo"')
            body_parts.append(b'')
            body_parts.append(str(slice_no).encode())

            # sliceMD5字段
            body_parts.append(f'--{boundary}'.encode())
            body_parts.append(b'Content-Disposition: form-data; name="sliceMD5"')
            body_parts.append(b'')
            body_parts.append(slice_md5.encode())

            # slice文件字段
            body_parts.append(f'--{boundary}'.encode())
            body_parts.append(b'Content-Disposition: form-data; name="slice"; filename="slice"')
            body_parts.append(b'Content-Type: application/octet-stream')
            body_parts.append(b'')
            body_parts.append(slice_data)

            # 结束边界
            body_parts.append(f'--{boundary}--'.encode())
            body_parts.append(b'')

            # 组合body
            body = b'\r\n'.join(body_parts)

            # 建立连接
            if server.startswith('https://'):
                conn = http.client.HTTPSConnection(host)
            else:
                conn = http.client.HTTPConnection(host)

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Platform': 'open_platform',
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }

            conn.request("POST", "/upload/v2/file/slice", body, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")

            if response.status == 200:
                try:
                    result = json.loads(data)
                    return result.get("code") == 0
                except:
                    return True
            else:
                print(f"上传分片失败，状态码: {response.status}, 响应: {data}")
                return False

        except Exception as e:
            print(f"上传分片时发生错误: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def _upload_complete_v2(self, preupload_id: str) -> str:
        """确认上传完成"""
        print("正在确认上传完成...")

        # 轮询检查上传状态
        max_retries = 30
        for retry in range(max_retries):
            conn = None
            try:
                conn = http.client.HTTPSConnection(self.api_base)
                headers = self._get_headers()
                headers['Content-Type'] = 'application/json'

                payload = json.dumps({"preuploadID": preupload_id})

                conn.request("POST", "/upload/v2/file/upload_complete", payload, headers)
                response = conn.getresponse()
                data = response.read().decode("utf-8")
                result = json.loads(data)

                if result.get("code") == 0:
                    data_info = result.get("data", {})
                    if data_info.get("completed", False) and data_info.get("fileID", 0) != 0:
                        file_id = data_info.get("fileID")
                        print(f"上传完成! 文件ID: {file_id}")
                        return str(file_id)
                    else:
                        print(f"上传处理中... ({retry+1}/{max_retries})")
                        time.sleep(1)
                else:
                    raise Exception(f"确认上传完成失败: {result.get('message', '未知错误')}")
            finally:
                if conn:
                    conn.close()

        raise Exception("上传完成确认超时")

    def _get_direct_link(self, file_id: str) -> str:
        """获取文件的直链下载地址"""
        print(f"正在获取直链...")
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            conn.request("GET", f"/api/v1/direct-link/url?fileID={file_id}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            result = json.loads(data)

            if result.get("code") == 0:
                url = result.get("data", {}).get("url")
                if url:
                    print(f"直链获取成功: {url}")
                    return url
                else:
                    raise Exception("响应中未找到直链URL")
            else:
                raise Exception(f"获取直链失败: {result.get('message', '未知错误')}")
        except Exception as e:
            print(f"获取直链时发生错误: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def find_directory(self, dir_name: str, parent_id: int = 0) -> Optional[int]:
        """查找目录（使用普通文件查询API）"""
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            # 使用v2文件列表API
            params = f"?parentFileId={parent_id}&limit=100"
            conn.request("GET", f"/api/v2/file/list{params}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            result = json.loads(data)

            if result.get("code") == 0:
                file_list = result.get("data", {}).get("fileList", [])
                for file_info in file_list:
                    # type=1表示文件夹
                    if file_info.get("type") == 1 and file_info.get("filename", "").lower() == dir_name.lower():
                        file_id = file_info.get("fileId")
                        print(f"找到已存在的目录: {dir_name} (ID: {file_id})")
                        return int(file_id)
                return None
            else:
                print(f"查找目录失败: {result.get('message', '未知错误')}")
                return None
        except Exception as e:
            print(f"查找目录时发生错误: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def create_directory(self, dir_name: str, parent_id: int = 0) -> Optional[int]:
        """创建目录（使用普通文件创建API）"""
        print(f"正在创建目录: {dir_name}")
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'

            payload = json.dumps({
                "name": dir_name,
                "parentID": parent_id
            })

            conn.request("POST", "/upload/v1/file/mkdir", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            result = json.loads(data)

            if result.get("code") == 0:
                dir_id = result.get("data", {}).get("dirID")
                if dir_id:
                    print(f"目录创建成功，ID: {dir_id}")
                    return int(dir_id)
                else:
                    print("目录创建失败：响应数据为空")
                    return None
            else:
                print(f"创建目录失败: {result.get('message', '未知错误')}")
                return None
        except Exception as e:
            print(f"创建目录时发生错误: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_or_create_directory(self, dir_name: str, parent_id: int = 0) -> Optional[int]:
        """获取或创建目录"""
        dir_id = self.find_directory(dir_name, parent_id)
        if dir_id:
            return dir_id
        return self.create_directory(dir_name, parent_id)


class MarkdownFileConverter:
    """Markdown文件转换器"""

    def __init__(self, image_hosting_dir_id: str, direct_link_dir_id: str,
                 client_id: str = None, client_secret: str = None):
        self.image_hosting_root_dir_id = image_hosting_dir_id
        self.direct_link_root_dir_id = int(direct_link_dir_id) if direct_link_dir_id else 0
        self.IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.tif'}

        try:
            if client_id and client_secret:
                self.image_manager = ImageHostingManager(client_id=client_id, client_secret=client_secret)
                self.direct_link_manager = DirectLinkManager(client_id=client_id, client_secret=client_secret)
            else:
                config = load_config()
                self.image_manager = ImageHostingManager(
                    client_id=config.get("CLIENT_ID"),
                    client_secret=config.get("CLIENT_SECRET")
                )
                self.direct_link_manager = DirectLinkManager(
                    client_id=config.get("CLIENT_ID"),
                    client_secret=config.get("CLIENT_SECRET")
                )
            print("管理器初始化成功")
        except Exception as e:
            print(f"管理器初始化失败: {e}")
            raise

    def get_directory_name_for_file(self, file_path: str) -> str:
        """根据文件名获取目录名"""
        filename = os.path.basename(file_path)
        if filename.endswith('.md'):
            return filename[:-3]
        else:
            return filename

    def get_image_upload_directory(self, md_file_path: str) -> str:
        """获取或创建用于存储图片的图床目录"""
        dir_name = self.get_directory_name_for_file(md_file_path)
        return self.image_manager.get_or_create_directory(dir_name, self.image_hosting_root_dir_id)

    def get_attachment_upload_directory(self, md_file_path: str) -> int:
        """获取或创建用于存储附件的直链目录"""
        dir_name = self.get_directory_name_for_file(md_file_path)
        return self.direct_link_manager.get_or_create_directory(dir_name, self.direct_link_root_dir_id)

    def extract_images_from_markdown(self, md_file_path: str) -> List[Dict[str, str]]:
        """从Markdown文件中提取图片信息"""
        images = []
        md_dir = os.path.dirname(os.path.abspath(md_file_path))

        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取Markdown文件失败: {e}")
            return images

        patterns = [
            r'!\[([^\]]*)\]\(([^)]+)\)',  # Markdown语法
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # HTML标签
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if pattern == patterns[0]:
                    alt_text = match.group(1)
                    image_src = match.group(2)
                else:
                    alt_text = ""
                    image_src = match.group(1)

                if image_src.startswith(('http://', 'https://')):
                    continue

                if not os.path.isabs(image_src):
                    image_path = os.path.join(md_dir, image_src)
                else:
                    image_path = image_src

                if os.path.exists(image_path) and self._is_image_file(image_path):
                    images.append({
                        'alt_text': alt_text,
                        'original_path': image_src,
                        'full_path': os.path.abspath(image_path),
                        'filename': os.path.basename(image_path),
                        'file_size': os.path.getsize(image_path),
                        'match_start': match.start(),
                        'match_end': match.end(),
                        'pattern_type': 'markdown' if pattern == patterns[0] else 'html'
                    })

        print(f"从Markdown中提取到 {len(images)} 个本地图片")
        return images

    def extract_attachments_from_markdown(self, md_file_path: str) -> List[Dict[str, str]]:
        """从Markdown文件中提取附件信息"""
        attachments = []
        md_dir = os.path.dirname(os.path.abspath(md_file_path))

        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取Markdown文件失败: {e}")
            return attachments

        patterns = [
            r'\[([^\]]*)\]\(([^)]+)\)',  # Markdown链接
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',  # HTML链接
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if pattern == patterns[0]:
                    text = match.group(1)
                    file_path = match.group(2)
                else:
                    file_path = match.group(1)
                    text = match.group(2)

                if file_path.startswith(('http://', 'https://')):
                    continue

                if self._is_image_file(file_path):
                    continue

                if not os.path.isabs(file_path):
                    absolute_path = os.path.join(md_dir, file_path)
                else:
                    absolute_path = file_path

                if os.path.exists(absolute_path) and os.path.isfile(absolute_path):
                    attachments.append({
                        'text': text,
                        'original_path': file_path,
                        'full_path': os.path.abspath(absolute_path),
                        'filename': os.path.basename(absolute_path),
                        'file_size': os.path.getsize(absolute_path),
                        'match_start': match.start(),
                        'match_end': match.end(),
                        'pattern_type': 'markdown' if pattern == patterns[0] else 'html'
                    })

        print(f"从Markdown中提取到 {len(attachments)} 个本地附件")
        return attachments

    def _is_image_file(self, file_path: str) -> bool:
        """检查文件是否为图片"""
        ext = Path(file_path).suffix.lower()
        return ext in self.IMAGE_EXTENSIONS

    def upload_images_to_hosting(self, images: List[Dict[str, str]], md_file_path: str) -> Dict[str, str]:
        """将图片上传到图床"""
        image_dir_id = self.get_image_upload_directory(md_file_path)
        if not image_dir_id:
            print("无法创建或获取图床目录")
            return {}

        path_to_cdn = {}
        print(f"开始上传 {len(images)} 个图片到图床...")

        for i, image_info in enumerate(images, 1):
            image_path = image_info['full_path']
            filename = image_info['filename']
            print(f"\n[{i}/{len(images)}] 上传图片: {filename}")

            try:
                if image_info['file_size'] > 100 * 1024 * 1024:
                    print(f"跳过 {filename}: 文件大小超过100MB限制")
                    continue

                result = self.image_manager.upload_image(image_path, image_dir_id)

                if result.get('success') and result.get('fileID'):
                    file_id = result['fileID']
                    detail = self.image_manager.get_image_detail(file_id)

                    if detail and detail.get('downloadURL'):
                        cdn_url = detail['downloadURL']
                        path_to_cdn[image_info['original_path']] = cdn_url
                        print(f"{filename} 上传成功: {cdn_url}")
                    else:
                        print(f"{filename} 上传成功但无法获取CDN链接")
                else:
                    print(f"{filename} 上传失败")

            except Exception as e:
                print(f"{filename} 上传出错: {e}")

        print(f"\n上传完成，成功上传 {len(path_to_cdn)} 个图片")
        return path_to_cdn

    def upload_attachments_to_direct_link(self, attachments: List[Dict[str, str]], md_file_path: str) -> Dict[str, str]:
        """将附件上传到直链目录"""
        attachment_dir_id = self.get_attachment_upload_directory(md_file_path)
        if not attachment_dir_id:
            print("无法创建或获取直链目录")
            return {}

        path_to_link = {}
        print(f"开始上传 {len(attachments)} 个附件到直链目录...")

        for i, attachment_info in enumerate(attachments, 1):
            attachment_path = attachment_info['full_path']
            filename = attachment_info['filename']
            print(f"\n[{i}/{len(attachments)}] 上传附件: {filename}")

            try:
                if attachment_info['file_size'] > 10 * 1024 * 1024 * 1024:  # 10GB
                    print(f"跳过 {filename}: 文件大小超过10GB限制")
                    continue

                result = self.direct_link_manager.upload_attachment(attachment_path, attachment_dir_id)

                if result.get('success') and result.get('downloadURL'):
                    direct_link = result['downloadURL']
                    path_to_link[attachment_info['original_path']] = direct_link
                    print(f"{filename} 上传成功: {direct_link}")
                else:
                    print(f"{filename} 上传失败")

            except Exception as e:
                print(f"{filename} 上传出错: {e}")

        print(f"\n上传完成，成功上传 {len(path_to_link)} 个附件")
        return path_to_link

    def update_markdown_file(self, md_file_path: str, path_to_cdn: Dict[str, str],
                           images: List[Dict[str, str]], backup: bool = True) -> bool:
        """更新Markdown文件中的图片链接"""
        return self._update_markdown_links(md_file_path, path_to_cdn, images, 'image', backup)

    def update_markdown_file_attachments(self, md_file_path: str, path_to_link: Dict[str, str],
                                       attachments: List[Dict[str, str]], backup: bool = True) -> bool:
        """更新Markdown文件中的附件链接"""
        return self._update_markdown_links(md_file_path, path_to_link, attachments, 'attachment', backup)

    def _update_markdown_links(self, md_file_path: str, path_to_link: Dict[str, str],
                             items: List[Dict[str, str]], item_type: str, backup: bool = True) -> bool:
        """通用的Markdown链接更新方法"""
        if not path_to_link:
            print(f"没有需要更新的{item_type}链接")
            return True

        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if backup:
                backup_path = md_file_path + '.bak'
                shutil.copy2(md_file_path, backup_path)
                print(f"创建备份文件: {backup_path}")

            updated_items = []
            for item_info in sorted(items, key=lambda x: x['match_start'], reverse=True):
                original_path = item_info['original_path']
                if original_path in path_to_link:
                    link_url = path_to_link[original_path]

                    if item_type == 'image':
                        if item_info['pattern_type'] == 'markdown':
                            new_link = f"![{item_info['alt_text']}]({link_url})"
                        elif item_info['pattern_type'] == 'html':
                            new_link = f'<img src="{link_url}">'
                        else:
                            new_link = link_url
                    else:  # attachment
                        if item_info['pattern_type'] == 'markdown':
                            new_link = f"[{item_info['text']}]({link_url})"
                        elif item_info['pattern_type'] == 'html':
                            new_link = f'<a href="{link_url}">{item_info["text"]}</a>'
                        else:
                            new_link = link_url

                    content = (content[:item_info['match_start']] +
                             new_link +
                             content[item_info['match_end']:])

                    updated_items.append(item_info['filename'])

            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            item_type_name = "图片" if item_type == 'image' else "附件"
            print(f"Markdown文件更新成功，替换了 {len(updated_items)} 个{item_type_name}链接")
            return True

        except Exception as e:
            print(f"更新Markdown文件失败: {e}")
            return False

    def process_markdown_file(self, md_file_path: str, backup: bool = True,
                            upload_only: bool = False) -> Dict[str, Any]:
        """处理单个Markdown文件"""
        result = {
            'file_path': md_file_path,
            'success': False,
            'images_found': 0,
            'images_uploaded': 0,
            'attachments_found': 0,
            'attachments_uploaded': 0,
            'error': None
        }

        try:
            print(f"\n处理文件: {md_file_path}")

            if not os.path.exists(md_file_path):
                result['error'] = "文件不存在"
                return result

            images = self.extract_images_from_markdown(md_file_path)
            result['images_found'] = len(images)

            attachments = self.extract_attachments_from_markdown(md_file_path)
            result['attachments_found'] = len(attachments)

            if not images and not attachments:
                print("文件中没有找到本地图片或附件")
                result['success'] = True
                return result

            path_to_cdn = {}
            if images:
                path_to_cdn = self.upload_images_to_hosting(images, md_file_path)
                result['images_uploaded'] = len(path_to_cdn)

            path_to_link = {}
            if attachments:
                path_to_link = self.upload_attachments_to_direct_link(attachments, md_file_path)
                result['attachments_uploaded'] = len(path_to_link)

            if not upload_only:
                update_success = True

                if path_to_cdn:
                    image_update_success = self.update_markdown_file(md_file_path, path_to_cdn, images, backup)
                    update_success = update_success and image_update_success
                    backup = False  # 第一次备份后，第二次不需要再备份

                if path_to_link:
                    attachment_update_success = self.update_markdown_file_attachments(md_file_path, path_to_link, attachments, backup)
                    update_success = update_success and attachment_update_success

                if update_success:
                    result['success'] = True
                else:
                    result['error'] = "更新Markdown文件失败"
            else:
                result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            print(f"处理文件时发生错误: {e}")

        return result

    def process_directory(self, dir_path: str, recursive: bool = True,
                         backup: bool = True, upload_only: bool = False) -> List[Dict[str, Any]]:
        """处理目录中的所有Markdown文件"""
        results = []

        try:
            pattern = "**/*.md" if recursive else "*.md"
            md_files = list(Path(dir_path).glob(pattern))

            if not md_files:
                print(f"目录 {dir_path} 中没有找到Markdown文件")
                return results

            print(f"找到 {len(md_files)} 个Markdown文件")

            for md_file in md_files:
                result = self.process_markdown_file(
                    str(md_file), backup=backup, upload_only=upload_only
                )
                results.append(result)

            successful = sum(1 for r in results if r['success'])
            total_images_found = sum(r['images_found'] for r in results)
            total_images_uploaded = sum(r['images_uploaded'] for r in results)
            total_attachments_found = sum(r['attachments_found'] for r in results)
            total_attachments_uploaded = sum(r['attachments_uploaded'] for r in results)

            print(f"\n处理完成统计:")
            print(f"   文件处理: {successful}/{len(results)} 成功")
            print(f"   图片找到: {total_images_found} 个")
            print(f"   图片上传: {total_images_uploaded} 个")
            print(f"   附件找到: {total_attachments_found} 个")
            print(f"   附件上传: {total_attachments_uploaded} 个")

        except Exception as e:
            print(f"处理目录时发生错误: {e}")

        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将Markdown文件中的本地图片和附件上传到123网盘并替换链接',
        epilog="""
使用示例:
  python md_to_image_hosting_win.py document.md
  python md_to_image_hosting_win.py ./docs/ --recursive
        """
    )

    parser.add_argument('input', nargs='?', help='Markdown文件或目录路径')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='递归处理子目录中的Markdown文件')
    parser.add_argument('--upload-only', '-u', action='store_true',
                       help='只上传文件，不更新Markdown文件')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件')
    parser.add_argument('--image-dir', default="yk6baz03t0n000d7w33hcrz8u5d6d0fvDIQwAdJxDcxvAqY2DF==",
                       help='图床上传根目录ID')
    parser.add_argument('--attachment-dir', default="25668840",
                       help='附件上传根目录ID（直链/Markdown目录）')

    # 检查是否有命令行参数
    if len(sys.argv) == 1:
        # 交互式模式
        print("=" * 60)
        print("Markdown文件转123网盘工具（独立Windows版本）")
        print("=" * 60)
        input_path = input("\n请输入Markdown文件或目录路径: ").strip().strip('"')
        if not input_path or not os.path.exists(input_path):
            print("路径不存在或无效")
            return

        args = argparse.Namespace(
            input=input_path,
            recursive=False,
            upload_only=False,
            no_backup=False,
            image_dir="yk6baz03t0n000d7w33hcrz8u5d6d0fvDIQwAdJxDcxvAqY2DF==",
            attachment_dir="25668840"
        )
    else:
        args = parser.parse_args()
        if not args.input:
            parser.print_help()
            return

    if not os.path.exists(args.input):
        print(f"路径不存在: {args.input}")
        return

    try:
        # 如果未指定附件目录，需要提示用户
        if not args.attachment_dir:
            print("\n注意: 需要指定直链目录ID")
            print("请先运行 查询文件.py 找到 '直链/Markdown' 目录的ID")
            args.attachment_dir = input("请输入直链/Markdown目录ID: ").strip()
            if not args.attachment_dir:
                print("未指定附件目录ID，将跳过附件上传")

        converter = MarkdownFileConverter(
            image_hosting_dir_id=args.image_dir,
            direct_link_dir_id=args.attachment_dir
        )

        print("=" * 60)
        print("Markdown文件转123网盘工具")
        print("=" * 60)

        if os.path.isfile(args.input):
            if args.input.lower().endswith('.md'):
                result = converter.process_markdown_file(
                    args.input,
                    backup=not args.no_backup,
                    upload_only=args.upload_only
                )

                if result['success']:
                    print(f"\n处理完成!")
                    print(f"   找到图片: {result['images_found']} 个")
                    print(f"   上传图片: {result['images_uploaded']} 个")
                    print(f"   找到附件: {result['attachments_found']} 个")
                    print(f"   上传附件: {result['attachments_uploaded']} 个")
                else:
                    print(f"\n处理失败: {result.get('error', '未知错误')}")
            else:
                print(f"输入文件不是Markdown文件: {args.input}")

        elif os.path.isdir(args.input):
            results = converter.process_directory(
                args.input,
                recursive=args.recursive,
                backup=not args.no_backup,
                upload_only=args.upload_only
            )

            failed_results = [r for r in results if not r['success']]
            if failed_results:
                print(f"\n以下文件处理失败:")
                for result in failed_results:
                    print(f"   {result['file_path']}: {result.get('error', '未知错误')}")
        else:
            print(f"不支持的输入类型: {args.input}")

    except KeyboardInterrupt:
        print("\n\n用户中断操作，程序退出")
    except Exception as e:
        print(f"程序运行时发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
