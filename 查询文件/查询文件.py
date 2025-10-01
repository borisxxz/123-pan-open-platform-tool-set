#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
123云盘文件查询工具

功能说明：
    本工具提供完整的123云盘文件查询功能，支持多种查询方式和灵活的筛选条件。

主要功能：
    - 文件列表查询：支持指定目录查询和翻页浏览
    - 文件搜索：支持模糊搜索和精准搜索两种模式
    - 批量查询：一次性获取所有页面的文件列表
    - 智能过滤：自动过滤回收站文件，保持结果清晰

技术特点：
    - 使用v2 API，性能更优
    - 完整的错误处理和异常捕获
    - 自动获取和管理访问令牌
    - 格式化输出，结果一目了然

作者: Assistant
创建日期: 2025/09/26
更新日期: 2025/10/01
版本: v2.0
基于: 123云盘开放平台 API v2
"""

import json
import http.client
import sys
import os
from typing import Optional, Dict, Any, List
from urllib.parse import quote


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

    示例：
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


# ==================== 核心查询类 ====================

class Pan123Query:
    """
    123云盘文件查询器

    本类封装了123云盘开放平台的文件查询相关API，提供便捷的Python接口。
    使用v2版本API，支持更高效的文件列表获取和搜索功能。

    属性:
        access_token: API访问令牌
        api_base: API服务器地址

    使用示例:
        >>> query = Pan123Query(client_id="your_id", client_secret="your_secret")
        >>> result = query.get_file_list(parent_file_id=0)
        >>> files = result['files']
    """

    # API服务器地址常量
    API_BASE = "open-api.123pan.com"

    # 文件分类映射表
    CATEGORY_MAP = {
        0: "未知",
        1: "音频",
        2: "视频",
        3: "图片",
        10: "文档"
    }

    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        """
        初始化查询器

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

    def _get_category_name(self, category: int) -> str:
        """
        获取文件分类名称

        将数字分类代码转换为可读的分类名称。

        Args:
            category: 分类代码

        Returns:
            str: 分类名称
        """
        return self.CATEGORY_MAP.get(category, f"类型{category}")

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

    def get_file_list(self, parent_file_id: int = 0, limit: int = 100,
                     last_file_id: Optional[int] = None, include_trashed: bool = False) -> Dict[str, Any]:
        """
        获取文件列表

        查询指定目录下的文件和文件夹列表。支持分页查询和回收站文件过滤。

        Args:
            parent_file_id: 父目录ID，0表示根目录
            limit: 每页数量，最大100
            last_file_id: 翻页查询时的起始文件ID，用于获取下一页
            include_trashed: 是否包含回收站文件，默认False

        Returns:
            Dict[str, Any]: 包含以下键的字典：
                - success: 是否成功
                - files: 文件列表
                - last_file_id: 下一页起始ID（-1表示无更多数据）
                - has_more: 是否有更多数据
                - limit: 每页数量

        Raises:
            Exception: API调用失败

        示例:
            >>> result = query.get_file_list(parent_file_id=0, limit=50)
            >>> for file in result['files']:
            ...     print(file['filename'])
        """
        print(f"正在获取文件列表 (目录ID: {parent_file_id})")

        try:
            # 建立连接
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            # 构建查询参数
            params = f"?parentFileId={parent_file_id}&limit={limit}"
            if last_file_id is not None:
                params += f"&lastFileId={last_file_id}"

            # 发送请求
            conn.request("GET", f"/api/v2/file/list{params}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            # 解析响应
            result = json.loads(data)

            if result.get("code") == 0:
                data = result.get("data", {})
                file_list = data.get("fileList", [])
                last_file_id = data.get("lastFileId", -1)

                # 过滤回收站文件（除非明确要求包含）
                if not include_trashed:
                    file_list = [f for f in file_list if f.get("trashed", 0) == 0]

                print(f"✅ 获取到 {len(file_list)} 个文件/文件夹")

                # 格式化输出文件列表
                if file_list:
                    self._print_file_list(file_list)

                return {
                    "success": True,
                    "files": file_list,
                    "last_file_id": last_file_id,
                    "has_more": last_file_id != -1,
                    "limit": limit
                }
            else:
                raise Exception(f"获取文件列表失败: {result.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 获取文件列表时发生错误: {e}")
            raise

    def search_files(self, keyword: str, search_mode: int = 0, limit: int = 100,
                    last_file_id: Optional[int] = None, include_trashed: bool = False) -> Dict[str, Any]:
        """
        搜索文件

        在整个云盘中搜索包含指定关键词的文件和文件夹。

        Args:
            keyword: 搜索关键词
            search_mode: 搜索模式
                - 0: 全文模糊搜索（默认）
                - 1: 精准搜索（完全匹配）
            limit: 每页数量，最大100
            last_file_id: 翻页查询时的起始文件ID
            include_trashed: 是否包含回收站文件

        Returns:
            Dict[str, Any]: 包含搜索结果的字典

        Raises:
            Exception: API调用失败
        """
        print(f"正在搜索文件: '{keyword}' (模式: {'精准' if search_mode == 1 else '模糊'})")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            # 构建查询参数 - URL编码搜索关键词
            encoded_keyword = quote(keyword)
            params = f"?parentFileId=0&limit={limit}&searchData={encoded_keyword}&searchMode={search_mode}"
            if last_file_id is not None:
                params += f"&lastFileId={last_file_id}"

            # 发送请求
            conn.request("GET", f"/api/v2/file/list{params}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            # 解析响应
            result = json.loads(data)

            if result.get("code") == 0:
                data = result.get("data", {})
                file_list = data.get("fileList", [])
                last_file_id = data.get("lastFileId", -1)

                # 过滤回收站文件
                if not include_trashed:
                    file_list = [f for f in file_list if f.get("trashed", 0) == 0]

                print(f"✅ 搜索到 {len(file_list)} 个匹配的文件/文件夹")

                # 格式化输出搜索结果
                if file_list:
                    self._print_search_results(file_list)

                return {
                    "success": True,
                    "files": file_list,
                    "last_file_id": last_file_id,
                    "has_more": last_file_id != -1,
                    "keyword": keyword
                }
            else:
                raise Exception(f"搜索文件失败: {result.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 搜索文件时发生错误: {e}")
            raise

    def get_file_list_all_pages(self, parent_file_id: int = 0, limit: int = 100,
                               include_trashed: bool = False) -> List[Dict[str, Any]]:
        """
        获取所有页面的文件列表

        自动进行分页查询，一次性获取指定目录下的所有文件。
        适用于需要完整文件列表的场景。

        Args:
            parent_file_id: 父目录ID，0表示根目录
            limit: 每页数量，最大100
            include_trashed: 是否包含回收站文件

        Returns:
            List[Dict[str, Any]]: 所有文件的列表

        注意:
            对于大型目录，此方法可能需要较长时间执行
        """
        all_files = []
        last_file_id = None

        print("正在获取所有页面的文件列表...")

        while True:
            result = self.get_file_list(parent_file_id, limit, last_file_id, include_trashed)

            if not result.get("success"):
                break

            files = result.get("files", [])
            all_files.extend(files)

            # 检查是否还有更多数据
            if not result.get("has_more", False):
                break

            last_file_id = result.get("last_file_id")
            if last_file_id == -1:
                break

        return all_files

    def _print_file_list(self, file_list: List[Dict[str, Any]]) -> None:
        """
        格式化打印文件列表

        Args:
            file_list: 文件信息列表
        """
        print("\n文件列表:")
        print("-" * 100)
        print(f"{'ID':<12} {'类型':<6} {'名称':<25} {'大小':<12} {'分类':<8} {'状态':<6} {'修改时间'}")
        print("-" * 100)

        for file_info in file_list:
            file_id = file_info.get("fileId", "")
            file_type = "文件夹" if file_info.get("type") == 1 else "文件"
            file_name = file_info.get("filename", "")[:23]
            file_size = self._format_file_size(file_info.get("size", 0))
            category = self._get_category_name(file_info.get("category", 0))
            status = "正常" if file_info.get("status", 0) <= 100 else "驳回"
            update_time = file_info.get("updateAt", "")[:16]

            print(f"{file_id:<12} {file_type:<6} {file_name:<25} {file_size:<12} {category:<8} {status:<6} {update_time}")

    def _print_search_results(self, file_list: List[Dict[str, Any]]) -> None:
        """
        格式化打印搜索结果

        Args:
            file_list: 文件信息列表
        """
        print("\n搜索结果:")
        print("-" * 100)
        print(f"{'ID':<12} {'类型':<6} {'名称':<25} {'大小':<12} {'分类':<8} {'父目录ID':<10} {'修改时间'}")
        print("-" * 100)

        for file_info in file_list:
            file_id = file_info.get("fileId", "")
            file_type = "文件夹" if file_info.get("type") == 1 else "文件"
            file_name = file_info.get("filename", "")[:23]
            file_size = self._format_file_size(file_info.get("size", 0))
            category = self._get_category_name(file_info.get("category", 0))
            parent_id = file_info.get("parentFileId", "")
            update_time = file_info.get("updateAt", "")[:16]

            print(f"{file_id:<12} {file_type:<6} {file_name:<25} {file_size:<12} {category:<8} {parent_id:<10} {update_time}")


# ==================== 主程序 ====================

def main():
    """
    主函数 - 交互式命令行界面

    提供菜单式操作界面，支持：
    - 文件列表查询
    - 文件搜索
    - 批量获取所有页面
    """
    print("=" * 60)
    print("123云盘文件查询工具")
    print("=" * 60)

    # 加载配置文件
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
        # 创建查询器实例
        query = Pan123Query(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

        # 主循环
        while True:
            print("\n" + "=" * 60)
            print("请选择操作:")
            print("  1. 获取文件列表")
            print("  2. 搜索文件")
            print("  3. 获取所有页面文件列表")
            print("  0. 退出")
            print("=" * 60)

            choice = input("\n请输入选项 (0-3): ").strip()

            if choice == "0":
                print("\n👋 退出程序")
                break

            elif choice == "1":
                # 获取文件列表
                print("\n--- 获取文件列表 ---")
                parent_id = input("请输入父目录ID (直接回车表示根目录): ").strip()
                parent_id = int(parent_id) if parent_id else 0

                last_file_id = input("请输入起始文件ID (翻页用，直接回车表示从头开始): ").strip()
                last_file_id = int(last_file_id) if last_file_id else None

                query.get_file_list(parent_file_id=parent_id, last_file_id=last_file_id)

            elif choice == "2":
                # 搜索文件
                print("\n--- 搜索文件 ---")
                keyword = input("请输入搜索关键词: ").strip()

                if keyword:
                    search_mode = input("请选择搜索模式 (0:模糊搜索, 1:精准搜索, 直接回车默认模糊): ").strip()
                    search_mode = int(search_mode) if search_mode in ['0', '1'] else 0
                    query.search_files(keyword, search_mode=search_mode)
                else:
                    print("❌ 搜索关键词不能为空")

            elif choice == "3":
                # 获取所有页面文件列表
                print("\n--- 获取所有页面文件列表 ---")
                parent_id = input("请输入父目录ID (直接回车表示根目录): ").strip()
                parent_id = int(parent_id) if parent_id else 0

                all_files = query.get_file_list_all_pages(parent_file_id=parent_id)
                print(f"\n✅ 总共获取到 {len(all_files)} 个文件/文件夹")

            else:
                print("❌ 无效的选项，请重新选择")

    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出程序")

    except Exception as e:
        print(f"\n❌ 程序运行时发生错误: {e}")


if __name__ == "__main__":
    main()
