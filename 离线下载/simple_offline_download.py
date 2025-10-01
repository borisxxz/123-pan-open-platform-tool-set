#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
123云盘离线下载工具

功能说明：
    本工具提供完整的123云盘离线下载功能，支持命令行参数和交互式操作。

主要功能：
    - 离线下载：通过URL创建离线下载任务
    - 批量处理：支持从文件批量读取下载链接
    - 手动输入：支持交互式手动输入下载链接
    - 任务管理：自动创建和跟踪下载任务状态
    - 智能重试：任务间自动延迟，避免频率限制

技术特点：
    - 使用v1 API，稳定可靠
    - 基于http.client实现，无外部依赖
    - 完整的错误处理和异常捕获
    - 自动获取和管理访问令牌
    - 支持命令行参数和交互式输入两种模式

作者: Assistant
创建日期: 2025/09/26
更新日期: 2025/10/01
版本: v2.0
基于: 123云盘开放平台 API v1
"""

import http.client
import json
import time
import os
import argparse
import sys
from typing import Optional, List, Dict, Any

# ==================== 配置文件处理 ====================

def load_config(config_path: Optional[str] = None) -> Dict[str, str]:
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


# ==================== 认证令牌管理 ====================

def get_access_token(client_id: str, client_secret: str) -> str:
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


# ==================== 离线下载任务 ====================

def create_offline_download(access_token: str, url: str, file_name: Optional[str] = None,
                          dir_id: Optional[int] = None, callback_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    创建离线下载任务

    向123云盘API提交离线下载任务，支持自定义文件名、目录和回调。

    Args:
        access_token: API访问令牌
        url: 下载资源地址（必须以http://或https://开头）
        file_name: 自定义文件名（可选，默认使用原文件名）
        dir_id: 目标目录ID（可选，默认为根目录）
        callback_url: 任务完成回调地址（可选）

    Returns:
        Optional[Dict[str, Any]]: API响应数据，失败时返回None

    Raises:
        Exception: 网络请求失败
    """
    print(f"📤 发送请求: {url}")
    if file_name:
        print(f"📁 自定义文件名: {file_name}")
    else:
        print("📁 使用默认文件名")

    # 建立HTTPS连接
    conn = http.client.HTTPSConnection("open-api.123pan.com")

    # 构建请求数据
    payload_data = {"url": url}

    if file_name:
        payload_data["fileName"] = file_name
    if dir_id:
        payload_data["dirID"] = dir_id
    if callback_url:
        payload_data["callBackUrl"] = callback_url

    payload = json.dumps(payload_data)
    print(f"📋 请求数据: {payload}")

    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Platform': 'open_platform',
        'Authorization': f'Bearer {access_token}'
    }

    try:
        # 发送POST请求
        conn.request("POST", "/api/v1/offline/download", payload, headers)

        # 获取响应
        res = conn.getresponse()
        data = res.read()

        # 解析响应数据
        response_text = data.decode("utf-8")
        print(f"📨 响应数据: {response_text}")
        response_data = json.loads(response_text)

        return response_data

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None
    finally:
        conn.close()


# ==================== 用户输入处理 ====================

def get_urls_from_input() -> List[str]:
    """
    从用户输入获取URL列表

    交互式地从标准输入获取下载链接列表，用户输入空行结束。
    自动验证URL格式，只接受http://或https://开头的链接。

    Returns:
        List[str]: 有效的URL列表

    示例:
        >>> urls = get_urls_from_input()
        请按行输入下载链接，输入空行结束：
        https://example.com/file1.zip
        ✅ 已添加: https://example.com/file1.zip
        https://example.com/file2.zip
        ✅ 已添加: https://example.com/file2.zip

        >>> print(urls)
        ['https://example.com/file1.zip', 'https://example.com/file2.zip']
    """
    print("\n请按行输入下载链接，输入空行结束：")
    urls = []
    while True:
        url = input().strip()
        if not url:  # 空行结束
            break
        if url.startswith(('http://', 'https://')):
            urls.append(url)
            print(f"✅ 已添加: {url}")
        else:
            print(f"❌ 无效链接: {url} (必须以http://或https://开头)")

    return urls


def get_urls_from_file(file_path: str) -> List[str]:
    """
    从文件读取URL列表

    从指定文件中逐行读取下载链接，自动过滤空行和注释行（以#开头）。
    自动验证URL格式，只接受http://或https://开头的链接。

    Args:
        file_path: 文件路径

    Returns:
        List[str]: 有效的URL列表

    Raises:
        FileNotFoundError: 文件不存在
        Exception: 文件读取失败

    文件格式示例:
        # 这是注释行
        https://example.com/file1.zip
        https://example.com/file2.zip

        # 空行会被忽略
        https://example.com/file3.zip
    """
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                url = line.strip()
                if url and not url.startswith('#'):  # 忽略空行和注释行
                    if url.startswith(('http://', 'https://')):
                        urls.append(url)
                        print(f"✅ 第{line_num}行: {url}")
                    else:
                        print(f"❌ 第{line_num}行无效链接: {url}")

        print(f"📁 从文件读取到 {len(urls)} 个有效链接")
        return urls

    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return []
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return []


# ==================== 任务批处理 ====================

def process_downloads(access_token: str, urls: List[str]) -> None:
    """
    批量处理下载任务列表

    遍历URL列表，为每个URL创建离线下载任务。
    任务间自动延迟5秒，避免触发API频率限制。

    Args:
        access_token: API访问令牌
        urls: URL列表

    功能:
        - 逐个创建离线下载任务
        - 统计成功和失败数量
        - 任务间延迟避免频率限制
        - 显示详细的进度信息
    """
    if not urls:
        print("❌ 没有有效的下载链接")
        return

    print(f"\n🚀 开始创建 {len(urls)} 个离线下载任务...")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for i, url in enumerate(urls, 1):
        print(f"\n📥 任务 {i}/{len(urls)}: 使用默认文件名")
        print(f"🔗 链接: {url}")

        # 创建下载任务
        result = create_offline_download(
            access_token=access_token,
            url=url,
            file_name=None  # 使用默认文件名
        )

        if result:
            if result.get('code') == 0:
                task_id = result.get('data', {}).get('taskID')
                print(f"✅ 任务创建成功！任务ID: {task_id}")
                success_count += 1
            else:
                print(f"❌ 任务创建失败: {result.get('message', '未知错误')}")
                print(f"🔍 错误代码: {result.get('code')}")
                failed_count += 1
        else:
            print("❌ 请求失败")
            failed_count += 1

        # 如果不是最后一个任务，等待5秒
        if i < len(urls):
            print("⏳ 等待5秒后继续...")
            time.sleep(5)

        print("-" * 40)

    print(f"\n🎉 所有任务处理完成！")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {failed_count} 个")


# ==================== 主程序 ====================

def main() -> None:
    """
    主函数 - 交互式界面

    提供友好的交互式命令行界面，支持：
    1. 手动输入链接
    2. 从文件读取链接
    0. 退出程序

    工作流程：
        1. 加载配置文件获取API凭据
        2. 获取访问令牌
        3. 显示菜单，等待用户选择
        4. 根据用户选择处理下载任务
        5. 循环直到用户退出
    """
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
        # 获取访问令牌
        ACCESS_TOKEN = get_access_token(CLIENT_ID, CLIENT_SECRET)
    except Exception as e:
        print(f"❌ 无法获取访问令牌: {e}")
        return

    print("\n" + "=" * 60)
    print("123云盘离线下载工具")
    print("=" * 60)

    while True:
        print("\n请选择输入方式:")
        print("1. 手动输入链接")
        print("2. 从文件读取链接")
        print("0. 退出")

        choice = input("\n请输入选项 (0-2): ").strip()

        if choice == "0":
            print("👋 退出程序")
            break
        elif choice == "1":
            # 手动输入
            urls = get_urls_from_input()
            if urls:
                process_downloads(ACCESS_TOKEN, urls)
        elif choice == "2":
            # 从文件读取
            file_path = input("请输入文件路径: ").strip().replace('"', '')
            if file_path:
                urls = get_urls_from_file(file_path)
                if urls:
                    process_downloads(ACCESS_TOKEN, urls)
        else:
            print("❌ 无效选项，请重新选择")


if __name__ == "__main__":
    main()