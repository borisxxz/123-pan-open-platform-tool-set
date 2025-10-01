#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
123云盘直链管理工具

支持功能：
- 获取文件直链
- 启用/禁用直链空间
- 直链缓存刷新
- 获取直链流量日志
- 获取直链离线日志
- IP黑名单管理

作者: Assistant
日期: 2025/10/01
基于: 123云盘开放平台官方文档 v1
"""

import json
import http.client
import sys
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


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


class DirectLinkManager:
    """123云盘直链管理器"""

    def __init__(self, access_token: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        """
        初始化直链管理器

        Args:
            access_token: 访问令牌（可选，如果提供则直接使用）
            client_id: 客户端ID（当access_token为空时使用）
            client_secret: 客户端密钥（当access_token为空时使用）
        """
        self.api_base = "open-api.123pan.com"

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

    def get_direct_link(self, file_id: int) -> Optional[str]:
        """
        获取文件直链

        Args:
            file_id: 文件ID

        Returns:
            直链URL，失败返回None
        """
        print(f"🔗 正在获取文件 {file_id} 的直链...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            conn.request("GET", f"/api/v1/direct-link/url?fileID={file_id}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                url = result.get("data", {}).get("url")
                if url:
                    print(f"✅ 直链获取成功")
                    print(f"📋 直链URL: {url}")
                    return url
                else:
                    print("❌ 响应中未找到直链URL")
                    return None
            else:
                print(f"❌ 获取直链失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取直链时发生错误: {e}")
            return None

    def enable_direct_link(self, file_id: int) -> bool:
        """
        启用直链空间

        Args:
            file_id: 文件夹ID

        Returns:
            成功返回True
        """
        print(f"🔓 正在启用文件夹 {file_id} 的直链空间...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({"fileID": file_id})

            conn.request("POST", "/api/v1/direct-link/enable", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                filename = result.get("data", {}).get("filename", "未知")
                print(f"✅ 直链空间启用成功: {filename}")
                return True
            else:
                print(f"❌ 启用直链空间失败: {result.get('message', '未知错误')}")
                return False

        except Exception as e:
            print(f"❌ 启用直链空间时发生错误: {e}")
            return False

    def disable_direct_link(self, file_id: int) -> bool:
        """
        禁用直链空间

        Args:
            file_id: 文件夹ID

        Returns:
            成功返回True
        """
        print(f"🔒 正在禁用文件夹 {file_id} 的直链空间...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({"fileID": file_id})

            conn.request("POST", "/api/v1/direct-link/disable", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                filename = result.get("data", {}).get("filename", "未知")
                print(f"✅ 直链空间禁用成功: {filename}")
                return True
            else:
                print(f"❌ 禁用直链空间失败: {result.get('message', '未知错误')}")
                return False

        except Exception as e:
            print(f"❌ 禁用直链空间时发生错误: {e}")
            return False

    def refresh_cache(self) -> bool:
        """
        刷新直链缓存

        Returns:
            成功返回True
        """
        print("🔄 正在刷新直链缓存...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({})

            conn.request("POST", "/api/v1/direct-link/cache/refresh", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                print("✅ 直链缓存刷新成功")
                return True
            else:
                print(f"❌ 刷新直链缓存失败: {result.get('message', '未知错误')}")
                return False

        except Exception as e:
            print(f"❌ 刷新直链缓存时发生错误: {e}")
            return False

    def get_traffic_log(self, page_num: int = 1, page_size: int = 100,
                       start_time: str = None, end_time: str = None) -> Optional[Dict[str, Any]]:
        """
        获取直链流量日志（需要开发者权益，查询近3天）

        Args:
            page_num: 页数
            page_size: 分页大小
            start_time: 开始时间，格式：2025-01-01 00:00:00
            end_time: 结束时间，格式：2025-01-01 23:59:59

        Returns:
            流量日志数据
        """
        # 如果没有提供时间，默认查询今天
        if not start_time or not end_time:
            today = datetime.now()
            start_time = today.strftime("%Y-%m-%d 00:00:00")
            end_time = today.strftime("%Y-%m-%d 23:59:59")

        print(f"📊 正在获取直链流量日志...")
        print(f"⏰ 时间范围: {start_time} ~ {end_time}")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            # URL编码
            from urllib.parse import quote
            params = f"?pageNum={page_num}&pageSize={page_size}"
            params += f"&startTime={quote(start_time)}&endTime={quote(end_time)}"

            conn.request("GET", f"/api/v1/direct-link/log{params}", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                log_list = data_info.get("list", [])
                total = data_info.get("total", 0)

                print(f"✅ 获取到 {len(log_list)} 条日志记录 (总共 {total} 条)")

                if log_list:
                    print("\n" + "=" * 120)
                    print(f"{'文件名':<30} {'文件大小':<12} {'消耗流量':<12} {'文件来源':<8} {'直链URL'}")
                    print("=" * 120)

                    for log in log_list:
                        filename = log.get("fileName", "")[:28]
                        file_size = self._format_file_size(log.get("fileSize", 0))
                        traffic = self._format_file_size(log.get("totalTraffic", 0))
                        source = "图床" if log.get("fileSource") == 2 else "全部文件"
                        url = log.get("directLinkURL", "")[:60]

                        print(f"{filename:<30} {file_size:<12} {traffic:<12} {source:<8} {url}")

                return data_info
            else:
                print(f"❌ 获取流量日志失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取流量日志时发生错误: {e}")
            return None

    def get_offline_log(self, start_hour: str, end_hour: str,
                       page_num: int = 1, page_size: int = 100) -> Optional[Dict[str, Any]]:
        """
        获取直链离线日志（需要开发者权益，查询近30天）

        Args:
            start_hour: 开始时间，格式：2025010115
            end_hour: 结束时间，格式：2025010116
            page_num: 页数
            page_size: 分页大小

        Returns:
            离线日志数据
        """
        print(f"📊 正在获取直链离线日志...")
        print(f"⏰ 时间范围: {start_hour} ~ {end_hour}")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({
                "startHour": start_hour,
                "endHour": end_hour,
                "pageNum": page_num,
                "pageSize": page_size
            })

            conn.request("GET", "/api/v1/direct-link/offline/logs", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                log_list = data_info.get("list", [])
                total = data_info.get("total", 0)

                print(f"✅ 获取到 {len(log_list)} 条日志记录 (总共 {total} 条)")

                if log_list:
                    print("\n" + "=" * 100)
                    print(f"{'ID':<10} {'文件名':<30} {'文件大小':<12} {'日志时间范围':<30}")
                    print("=" * 100)

                    for log in log_list:
                        log_id = str(log.get("id", ""))
                        filename = log.get("fileName", "")[:28]
                        file_size = self._format_file_size(log.get("fileSize", 0))
                        time_range = log.get("logTimeRange", "")

                        print(f"{log_id:<10} {filename:<30} {file_size:<12} {time_range:<30}")
                        print(f"    下载地址: {log.get('downloadURL', '')}")

                return data_info
            else:
                print(f"❌ 获取离线日志失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取离线日志时发生错误: {e}")
            return None

    def get_ip_blacklist(self) -> Optional[Dict[str, Any]]:
        """
        获取IP黑名单列表

        Returns:
            IP黑名单数据
        """
        print("🔍 正在获取IP黑名单...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            conn.request("GET", "/api/v1/developer/config/forbide-ip/list", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                data_info = result.get("data", {})
                ip_list = data_info.get("ipList", [])
                status = data_info.get("status", 2)

                status_text = "✅ 启用" if status == 1 else "❌ 禁用"
                print(f"黑名单状态: {status_text}")
                print(f"共有 {len(ip_list)} 个IP地址")

                if ip_list:
                    print("\nIP黑名单:")
                    for i, ip in enumerate(ip_list, 1):
                        print(f"  {i}. {ip}")

                return data_info
            else:
                print(f"❌ 获取IP黑名单失败: {result.get('message', '未知错误')}")
                return None

        except Exception as e:
            print(f"❌ 获取IP黑名单时发生错误: {e}")
            return None

    def update_ip_blacklist(self, ip_list: List[str]) -> bool:
        """
        更新IP黑名单列表（需要开发者权益）

        Args:
            ip_list: IP地址列表，最多2000个IPv4地址

        Returns:
            成功返回True
        """
        if len(ip_list) > 2000:
            print("❌ IP地址列表最多2000个")
            return False

        print(f"📝 正在更新IP黑名单 ({len(ip_list)} 个IP)...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({"IpList": ip_list})

            conn.request("POST", "/api/v1/developer/config/forbide-ip/update", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                print(f"✅ IP黑名单更新成功")
                return True
            else:
                print(f"❌ 更新IP黑名单失败: {result.get('message', '未知错误')}")
                return False

        except Exception as e:
            print(f"❌ 更新IP黑名单时发生错误: {e}")
            return False

    def switch_ip_blacklist(self, enable: bool) -> bool:
        """
        开启/关闭IP黑名单（需要开发者权益）

        Args:
            enable: True为启用，False为禁用

        Returns:
            成功返回True
        """
        status = 1 if enable else 2
        action = "启用" if enable else "禁用"

        print(f"🔧 正在{action}IP黑名单...")

        try:
            conn = http.client.HTTPSConnection(self.api_base)
            headers = self._get_headers()

            payload = json.dumps({"Status": status})

            conn.request("POST", "/api/v1/developer/config/forbide-ip/switch", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()

            result = json.loads(data)

            if result.get("code") == 0:
                done = result.get("data", {}).get("Done", False)
                if done:
                    print(f"✅ IP黑名单{action}成功")
                    return True
                else:
                    print(f"❌ IP黑名单{action}未完成")
                    return False
            else:
                print(f"❌ {action}IP黑名单失败: {result.get('message', '未知错误')}")
                return False

        except Exception as e:
            print(f"❌ {action}IP黑名单时发生错误: {e}")
            return False


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
        # 创建直链管理器实例
        manager = DirectLinkManager(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

        print("=" * 60)
        print("123云盘直链管理工具")
        print("=" * 60)

        while True:
            print("\n请选择操作:")
            print("1. 获取文件直链")
            print("2. 启用直链空间")
            print("3. 禁用直链空间")
            print("4. 刷新直链缓存")
            print("5. 获取直链流量日志")
            print("6. 获取直链离线日志")
            print("7. 查看IP黑名单")
            print("8. 更新IP黑名单")
            print("9. 启用/禁用IP黑名单")
            print("0. 退出")

            choice = input("\n请输入选项 (0-9): ").strip()

            if choice == "0":
                print("👋 退出程序")
                break
            elif choice == "1":
                # 获取文件直链
                file_id = input("请输入文件ID: ").strip()
                if file_id.isdigit():
                    manager.get_direct_link(int(file_id))
                else:
                    print("❌ 文件ID必须是数字")

            elif choice == "2":
                # 启用直链空间
                file_id = input("请输入文件夹ID: ").strip()
                if file_id.isdigit():
                    manager.enable_direct_link(int(file_id))
                else:
                    print("❌ 文件夹ID必须是数字")

            elif choice == "3":
                # 禁用直链空间
                file_id = input("请输入文件夹ID: ").strip()
                if file_id.isdigit():
                    manager.disable_direct_link(int(file_id))
                else:
                    print("❌ 文件夹ID必须是数字")

            elif choice == "4":
                # 刷新直链缓存
                manager.refresh_cache()

            elif choice == "5":
                # 获取直链流量日志
                print("查询近3天的流量日志")
                print("提示: 时间格式为 YYYY-MM-DD HH:MM:SS")
                start_time = input("请输入开始时间 (直接回车使用今天00:00:00): ").strip()
                end_time = input("请输入结束时间 (直接回车使用今天23:59:59): ").strip()

                if not start_time and not end_time:
                    manager.get_traffic_log()
                elif start_time and end_time:
                    manager.get_traffic_log(start_time=start_time, end_time=end_time)
                else:
                    print("❌ 请同时提供开始时间和结束时间，或都留空")

            elif choice == "6":
                # 获取直链离线日志
                print("查询近30天的离线日志")
                print("提示: 时间格式为 YYYYMMDDHH，例如 2025010115")
                start_hour = input("请输入开始时间: ").strip()
                end_hour = input("请输入结束时间: ").strip()

                if start_hour and end_hour:
                    manager.get_offline_log(start_hour, end_hour)
                else:
                    print("❌ 请提供开始时间和结束时间")

            elif choice == "7":
                # 查看IP黑名单
                manager.get_ip_blacklist()

            elif choice == "8":
                # 更新IP黑名单
                print("请输入IP地址，每行一个，输入空行结束:")
                ip_list = []
                while True:
                    ip = input().strip()
                    if not ip:
                        break
                    ip_list.append(ip)

                if ip_list:
                    manager.update_ip_blacklist(ip_list)
                else:
                    print("❌ 未输入任何IP地址")

            elif choice == "9":
                # 启用/禁用IP黑名单
                action = input("请输入操作 (1:启用, 2:禁用): ").strip()
                if action == "1":
                    manager.switch_ip_blacklist(True)
                elif action == "2":
                    manager.switch_ip_blacklist(False)
                else:
                    print("❌ 无效的操作")

            else:
                print("❌ 无效的选项，请重新选择")

    except Exception as e:
        print(f"\n❌ 程序运行时发生错误: {e}")


if __name__ == "__main__":
    main()
