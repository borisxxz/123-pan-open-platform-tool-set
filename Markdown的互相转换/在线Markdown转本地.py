#!/usr/bin/env python3
"""
Markdown链接转换器
将明确的文件格式链接转换为本地文件引用，图片放到images文件夹，其他附件放到attachments文件夹
"""

import re
import os
import urllib.parse
from pathlib import Path
import requests
import hashlib
import time
from urllib.parse import urlparse

class MarkdownConverter:
    """
    Markdown链接转换器类

    功能：
    - 将Markdown文档中的外部链接转换为本地文件引用
    - 自动下载外部资源文件
    - 支持图片和附件的分类存储
    - 支持 data URI 格式的图片转换
    - 支持 HTML <img> 和 <source> 标签处理
    """

    def __init__(self, input_file='README.md', output_file='README_converted.md'):
        """
        初始化转换器

        参数：
            input_file: 输入的Markdown文件路径，默认为 'README.md'
            output_file: 输出的Markdown文件路径，默认为 'README_converted.md'
        """
        self.input_file = input_file
        self.output_file = output_file

        # 图片文件扩展名集合
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif'}

        # 附件文件扩展名集合（包括各种文档、压缩包、代码文件等）
        self.attachment_extensions = {'.pdf', '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar', '.exe',
                                     '.dmg', '.pkg', '.deb', '.rpm', '.msi', '.apk', '.iso', '.img', '.bin',
                                     '.txt', '.csv', '.json', '.xml', '.yaml', '.yml', '.ini', '.conf', '.log',
                                     '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
                                     '.md', '.markdown', '.html', '.htm', '.css', '.js', '.py', '.java', '.cpp',
                                     '.c', '.h', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.ts', '.jsx',
                                     '.tsx', '.vue', '.sh', '.bat', '.ps1', '.sql', '.toml', '.lock', '.yaml.lock',
                                     '.yml.lock', '.gitignore', '.dockerignore', '.env', '.env.example'}

        # 创建必要的文件夹（images 和 attachments）
        self.create_directories()

        # 初始化下载会话（用于保持连接复用，提高下载效率）
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # 已下载文件映射字典 {url: local_path}，避免重复下载
        self.downloaded_files = {}

    def create_directories(self):
        """
        创建必要的文件夹（images和attachments）

        如果文件夹已存在，则不会重复创建
        """
        os.makedirs('images', exist_ok=True)
        os.makedirs('attachments', exist_ok=True)
        print("已创建images和attachments文件夹")

    def download_file(self, url, save_dir, timeout=30):
        """
        下载文件到指定目录

        参数：
            url: 要下载的文件URL
            save_dir: 保存目录（'images' 或 'attachments'）
            timeout: 下载超时时间（秒），默认30秒

        返回：
            str: 本地文件路径（下载成功）
            None: 下载失败

        功能：
        - 检查文件是否已下载（避免重复下载）
        - 自动处理文件名冲突
        - 支持断点续传（流式下载）
        - 显示下载进度
        """
        try:
            # 检查是否已经下载过
            if url in self.downloaded_files:
                local_path = self.downloaded_files[url]
                if os.path.exists(local_path):
                    return local_path

            print(f"正在下载: {url[:100]}...")

            # 发送请求
            response = self.session.get(url, stream=True, timeout=timeout)
            response.raise_for_status()

            # 获取文件名
            filename = self.get_filename_from_url(url, response)
            local_path = os.path.join(save_dir, filename)

            # 处理文件名冲突
            local_path = self.handle_filename_conflict(local_path)

            # 下载文件
            self.save_response_to_file(response, local_path, url)

            # 记录下载的文件
            self.downloaded_files[url] = local_path

            print(f"下载完成: {local_path}")
            return local_path

        except requests.exceptions.RequestException as e:
            print(f"下载失败 {url}: {e}")
            return None
        except Exception as e:
            print(f"下载文件时出错 {url}: {e}")
            return None

    def get_filename_from_url(self, url, response):
        """
        从URL和HTTP响应头中智能提取文件名

        参数：
            url: 文件的URL
            response: HTTP响应对象

        返回：
            str: 提取或生成的文件名

        提取优先级：
        1. Content-Disposition 响应头中的 filename
        2. URL路径中的文件名
        3. 根据URL的MD5哈希生成唯一文件名
        """
        # 获取 Content-Type 用于后续推断扩展名
        content_type = response.headers.get('content-type', '').lower()

        # 尝试从Content-Disposition获取文件名
        content_disposition = response.headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            filename_match = re.search(r'filename[*]?=([^;]+)', content_disposition)
            if filename_match:
                filename = filename_match.group(1).strip('"\' ')
                # URL 解码文件名
                filename = urllib.parse.unquote(filename)
                # 确保文件名有扩展名
                if '.' not in os.path.basename(filename):
                    ext = self.get_extension_from_content_type(content_type)
                    if ext:
                        filename += ext
                # 清理文件名（替换空格和特殊字符）
                filename = self.sanitize_filename(filename)
                return filename

        # 尝试从URL路径获取文件名
        parsed_url = urlparse(url)
        path = parsed_url.path

        if path and path != '/':
            filename = os.path.basename(path)
            if filename:
                # URL 解码文件名
                filename = urllib.parse.unquote(filename)
                # 检查文件名是否有扩展名
                if '.' not in filename:
                    # 没有扩展名，尝试从 Content-Type 推断
                    ext = self.get_extension_from_content_type(content_type)
                    if ext:
                        filename += ext
                # 清理文件名（替换空格和特殊字符）
                filename = self.sanitize_filename(filename)
                return filename

        # 如果都没有，创建一个基于URL的文件名
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:12]

        # 尝试从Content-Type推断扩展名
        extension = self.get_extension_from_content_type(content_type)

        return f"download_{url_hash}{extension}"

    def sanitize_filename(self, filename):
        """
        清理文件名，移除或替换不安全的字符

        参数：
            filename: 原始文件名

        返回：
            str: 安全的文件名

        处理规则：
        - 将空格替换为连字符
        - 只保留字母、数字、连字符、下划线、点
        - 移除连续的连字符
        - 移除开头和结尾的连字符
        """
        # 分离文件名和扩展名
        name, ext = os.path.splitext(filename)

        # 替换空格为连字符
        name = name.replace(' ', '-')

        # 移除或替换其他可能有问题的字符
        # 保留：字母、数字、连字符、下划线、点
        import string
        allowed_chars = string.ascii_letters + string.digits + '-_.'
        name = ''.join(c if c in allowed_chars else '-' for c in name)

        # 移除连续的连字符
        while '--' in name:
            name = name.replace('--', '-')

        # 移除开头和结尾的连字符
        name = name.strip('-')

        return name + ext

    def get_extension_from_content_type(self, content_type):
        """
        根据HTTP Content-Type响应头推断文件扩展名

        参数：
            content_type: HTTP Content-Type 头的值

        返回：
            str: 文件扩展名（带点），如果无法推断则返回空字符串

        支持的类型：
        - 各种图片格式（jpeg, png, gif, svg, webp等）
        - 文档格式（pdf, text, html等）
        - 压缩格式（zip, tar, gzip等）
        """
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'image/webp': '.webp',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'application/pdf': '.pdf',
            'text/plain': '.txt',
            'text/html': '.html',
            'application/zip': '.zip',
            'application/x-zip-compressed': '.zip',
            'application/x-tar': '.tar',
            'application/x-gzip': '.gz',
            'application/x-bzip2': '.bz2',
            'application/x-xz': '.xz',
            'application/x-7z-compressed': '.7z',
            'application/x-rar-compressed': '.rar',
            'application/octet-stream': '.bin'
        }

        for ct, ext in content_type_map.items():
            if ct in content_type:
                return ext

        return ''

    def handle_filename_conflict(self, original_path):
        """
        处理文件名冲突，自动生成不重复的文件名

        参数：
            original_path: 原始文件路径

        返回：
            str: 不冲突的文件路径

        如果文件已存在，会在文件名后添加 _1, _2, _3... 直到找到不存在的文件名
        例如：file.txt -> file_1.txt -> file_2.txt
        """
        if not os.path.exists(original_path):
            return original_path

        base, ext = os.path.splitext(original_path)
        counter = 1

        while os.path.exists(original_path):
            original_path = f"{base}_{counter}{ext}"
            counter += 1

        return original_path

    def save_response_to_file(self, response, local_path, url):
        """
        将HTTP响应内容保存到本地文件，并显示下载进度

        参数：
            response: HTTP响应对象（流式）
            local_path: 本地保存路径
            url: 下载的URL（用于显示）

        功能：
        - 使用流式下载（chunk by chunk）
        - 实时显示下载进度百分比
        - 支持大文件下载
        """
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    # 显示进度
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r下载进度: {progress:.1f}%", end='', flush=True)

        print()  # 换行

    def create_placeholder_files(self):
        """
        创建占位符文件，用于替换无法下载的资源

        创建的占位符：
        - images/placeholder.png: 1x1像素的透明PNG图片
        - attachments/placeholder.md: 说明文档
        """
        # 创建图片占位符
        placeholder_png = os.path.join('images', 'placeholder.png')
        if not os.path.exists(placeholder_png):
            # 创建一个简单的1x1像素的PNG文件作为占位符
            import base64
            png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==')
            with open(placeholder_png, 'wb') as f:
                f.write(png_data)

        # 创建文档占位符
        placeholder_md = os.path.join('attachments', 'placeholder.md')
        if not os.path.exists(placeholder_md):
            with open(placeholder_md, 'w', encoding='utf-8') as f:
                f.write('# 占位符文档\n\n这是一个占位符文件，原始文件无法下载或不存在。')

    def get_placeholder_file(self, file_type):
        """
        获取占位符文件路径

        参数：
            file_type: 文件类型（'image' 或其他）

        返回：
            str: 占位符文件的路径
        """
        if file_type == 'image':
            return 'images/placeholder.png'
        else:
            return 'attachments/placeholder.md'

    def backup_file(self):
        """
        备份原始Markdown文件

        返回：
            str: 备份文件的路径（备份成功）
            None: 备份失败或原文件不存在

        备份文件命名规则：
        - README.md -> README_backup.md
        - document.md -> document_backup.md
        """
        if os.path.exists(self.input_file):
            backup_name = f"{os.path.splitext(self.input_file)[0]}_backup{os.path.splitext(self.input_file)[1]}"
            try:
                import shutil
                shutil.copy2(self.input_file, backup_name)
                print(f"已备份原始文件到: {backup_name}")
                return backup_name
            except Exception as e:
                print(f"备份文件时出错: {e}")
                return None
        return None

    def is_url(self, text):
        """
        判断文本是否为URL

        参数：
            text: 要检查的文本

        返回：
            bool: 是URL返回True，否则返回False

        支持的协议：
        - http:// 和 https://
        - ftp://
        - mailto:
        - tel:
        - data: (data URI)
        """
        url_patterns = [
            r'^https?://',  # http/https
            r'^ftp://',     # ftp
            r'^mailto:',    # mailto
            r'^tel:',       # tel
            r'^data:image', # data URI中的图片
        ]
        return any(re.match(pattern, text) for pattern in url_patterns)

    def get_file_extension(self, url):
        """
        获取URL中的文件扩展名

        参数：
            url: URL字符串

        返回：
            str: 文件扩展名（小写，带点），如 '.png'。如果没有扩展名返回空字符串
        """
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        if '.' in path:
            return os.path.splitext(path)[1].lower()
        return ''

    def should_convert_link(self, url):
        """
        判断链接是否应该被转换为本地文件引用

        参数：
            url: 链接URL

        返回：
            bool: 需要转换返回True，否则返回False

        转换规则：
        - 锚点链接（#开头）：不转换
        - mailto:、tel: 协议：不转换
        - data: URI：需要转换
        - 外部 http/https/ftp URL：需要转换
        - 本地文件路径：需要转换（移动到对应目录）
        """
        # 排除锚点链接
        if url.startswith('#'):
            return False

        # 排除mailto、tel等协议
        if url.startswith(('mailto:', 'tel:')):
            return False

        # data URI 需要转换为本地文件
        if url.startswith('data:'):
            return True

        # 外部 http/https/ftp URL 需要下载并转换
        if self.is_url(url):
            return True

        # 本地文件路径需要转换（移动到对应目录）
        return True

    def convert_link(self, url, text, is_image=False):
        """
        转换链接为本地文件路径，并下载实际文件

        参数：
            url: 链接URL（可以是外部URL、data URI、或本地路径）
            text: 链接文本（用于判断类型）
            is_image: 是否为图片链接（![...](...) 格式）

        返回：
            str: 转换后的本地文件路径，如果不需要转换或转换失败则返回原URL

        处理类型：
        1. 空链接 -> 占位符文件
        2. data URI -> 解码并保存为本地文件
        3. 外部URL（有文件扩展名或is_image=True）-> 下载到本地
        4. 本地文件路径 -> 移动到对应目录（images或attachments）
        5. 普通超链接（无文件扩展名）-> 保持原样
        """
        # 处理空的[]()链接
        if not url or url.strip() == "":
            # 根据文本判断是否为图片
            if text and (text.startswith('!') or '图片' in text or 'image' in text.lower() or 'img' in text.lower()):
                return "images/placeholder.png"
            else:
                return "attachments/placeholder.md"

        if not self.should_convert_link(url):
            return url

        # 处理data URI格式的图片
        if url.startswith('data:'):
            import base64
            import hashlib

            try:
                # 解析data URI: data:[<mediatype>][;base64],<data>
                header, data = url.split(',', 1)

                # 判断是否 base64 编码
                is_base64 = ';base64' in header

                # 确定文件扩展名
                if 'svg' in header:
                    ext = '.svg'
                elif 'png' in header:
                    ext = '.png'
                elif 'jpeg' in header or 'jpg' in header:
                    ext = '.jpg'
                elif 'gif' in header:
                    ext = '.gif'
                elif 'webp' in header:
                    ext = '.webp'
                else:
                    ext = '.png'

                # 生成文件名（基于内容的hash）
                hash_obj = hashlib.md5(data.encode('utf-8'))
                filename = f"data_{hash_obj.hexdigest()[:12]}{ext}"
                new_path = f"images/{filename}"

                # 如果文件已存在，直接返回
                if os.path.exists(new_path):
                    return new_path

                # 保存文件
                if ext == '.svg':
                    # SVG 可能是 URL 编码或 base64 编码
                    if is_base64:
                        svg_data = base64.b64decode(data)
                        with open(new_path, 'wb') as f:
                            f.write(svg_data)
                    else:
                        # URL 编码的 SVG
                        import urllib.parse
                        svg_content = urllib.parse.unquote(data)
                        with open(new_path, 'w', encoding='utf-8') as f:
                            f.write(svg_content)
                else:
                    # 其他图片格式通常是 base64 编码
                    if is_base64:
                        image_data = base64.b64decode(data)
                    else:
                        # 如果不是 base64，尝试直接使用
                        image_data = data.encode('utf-8')

                    with open(new_path, 'wb') as f:
                        f.write(image_data)

                print(f"保存 data URI 到: {new_path}")
                return new_path
            except Exception as e:
                print(f"处理data URI时出错: {e}")
                return url

        # 处理外部URL
        if self.is_url(url):
            # 获取文件扩展名
            ext = self.get_file_extension(url)

            # 判断是否需要下载
            # 1. 如果是图片链接（is_image=True），则下载
            # 2. 如果URL有明确的文件扩展名（图片或附件），则下载
            # 3. 否则是普通超链接，保持原样
            should_download = is_image or (ext in self.image_extensions) or (ext in self.attachment_extensions)

            if not should_download:
                # 普通超链接，保持原样
                return url

            # 决定保存目录
            if ext in self.image_extensions or is_image:
                save_dir = 'images'
            else:
                save_dir = 'attachments'

            # 下载文件
            local_file_path = self.download_file(url, save_dir)

            if local_file_path:
                # 返回相对路径
                return f"{save_dir}/{os.path.basename(local_file_path)}"
            else:
                # 下载失败，保持原URL
                print(f"下载失败，保持原URL: {url}")
                return url

        # 处理本地路径（非URL）
        ext = self.get_file_extension(url)
        if ext in self.image_extensions:
            return f"images/{url}"
        elif ext in self.attachment_extensions:
            return f"attachments/{url}"

        # 其他类型文件保持原样
        return url

    def process_markdown(self):
        """
        处理Markdown文件的主函数

        功能流程：
        1. 创建占位符文件
        2. 备份原始文件
        3. 读取Markdown内容
        4. 手动解析Markdown链接（支持嵌套结构）
        5. 转换所有链接为本地引用
        6. 处理HTML图片标签
        7. 写入转换后的内容到输出文件

        支持的链接格式：
        - 普通链接：[text](url)
        - 图片链接：![alt](url)
        - 嵌套链接（徽章）：[![img](img_url)](link_url)
        - HTML <img> 标签
        - HTML <source> 标签
        """
        print(f"正在处理文件: {self.input_file}")

        # 创建占位符文件
        self.create_placeholder_files()

        # 备份原始文件
        self.backup_file()

        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"错误: 找不到文件 {self.input_file}")
            return
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return

        # 添加必要的导入
        import urllib.parse
        import os

        # 手动解析Markdown链接，正确处理嵌套结构
        i = 0
        converted_parts = []

        while i < len(content):
            # 检查是否是图片链接 ![...](...) 或普通链接 [...](...)
            is_image_link = False
            if content[i] == '!' and i + 1 < len(content) and content[i + 1] == '[':
                # 图片链接
                is_image_link = True
                i += 1  # 跳过 !

            if content[i] == '[':
                # 找到链接开始
                bracket_count = 1
                j = i + 1
                text_start = j
                text_end = -1

                # 找到匹配的]（考虑内嵌的[]）
                while j < len(content) and bracket_count > 0:
                    if content[j] == '[':
                        bracket_count += 1
                    elif content[j] == ']':
                        bracket_count -= 1
                    j += 1

                if bracket_count == 0:
                    text_end = j - 1
                    link_text = content[text_start:text_end]

                    # 检查是否有匹配的(()
                    if j < len(content) and content[j] == '(':
                        # 找到匹配的)
                        paren_count = 1
                        k = j + 1
                        url_start = k
                        url_end = -1

                        while k < len(content) and paren_count > 0:
                            if content[k] == '(':
                                paren_count += 1
                            elif content[k] == ')':
                                paren_count -= 1
                            k += 1

                        if paren_count == 0:
                            url_end = k - 1
                            url = content[url_start:url_end]

                            # 处理这个链接
                            link_type = "图片" if is_image_link else "链接"
                            print(f"找到{link_type}: [{link_text[:50]}...] -> ({url[:50]}...)")

                            # 递归处理嵌套链接（如徽章链接 [![img](img_url)](link_url)）
                            new_text = link_text
                            if link_text.startswith('![') and '](' in link_text:
                                # 这是一个嵌套的图片链接，需要递归处理
                                # 提取内层图片链接: ![alt](img_url)
                                # 找到内层的 ]( 位置
                                inner_bracket_end = link_text.find('](')
                                if inner_bracket_end > 2:
                                    img_alt = link_text[2:inner_bracket_end]
                                    # 找到内层URL的结束位置（最后一个 )）
                                    img_url_start = inner_bracket_end + 2
                                    img_url = link_text[img_url_start:].rstrip(')')

                                    # 转换内层图片URL（is_image=True）
                                    new_img_url = self.convert_link(img_url, img_alt, is_image=True)

                                    if new_img_url != img_url:
                                        # 重建图片链接
                                        new_text = f'![{img_alt}]({new_img_url})'
                                        print(f"转换嵌套图片: {img_url[:40]}... -> {new_img_url}")

                            # 转换外部链接URL
                            new_url = self.convert_link(url, new_text, is_image=is_image_link)

                            # 重新构建链接
                            if new_url != url or new_text != link_text:
                                print(f"转换完成: [{new_text[:40]}...] -> ({new_url[:40]}...)")

                            # 添加链接（如果是图片链接，需要加上!前缀）
                            if is_image_link:
                                converted_parts.append(f'![{new_text}]({new_url})')
                            else:
                                converted_parts.append(f'[{new_text}]({new_url})')
                            i = k
                            continue

            # 普通字符，直接添加
            converted_parts.append(content[i])
            i += 1

        converted_content = ''.join(converted_parts)

        # 处理 HTML 图片标签
        converted_content = self.process_html_images(converted_content)

        # 写入输出文件
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            print(f"转换完成! 输出文件: {self.output_file}")
        except Exception as e:
            print(f"写入文件时出错: {e}")

    def process_html_images(self, content):
        """
        处理HTML图片标签中的图片链接

        参数：
            content: Markdown内容（可能包含HTML标签）

        返回：
            str: 处理后的内容

        处理的标签：
        - <img src="...">：转换src属性中的URL
        - <source srcset="...">：转换srcset属性中的URL

        转换后的路径会添加 ./ 前缀使其更明确
        """
        print("\n开始处理 HTML 图片标签...")

        # 处理 <img src="..."> 标签
        img_pattern = r'<img\s+([^>]*?)src=["\'](.*?)["\']([^>]*?)>'

        def replace_img_src(match):
            before_src = match.group(1)
            url = match.group(2)
            after_src = match.group(3)

            print(f"找到 <img> 标签: src={url[:50]}...")

            # 转换 URL 为本地路径
            new_url = self.convert_link(url, "img", is_image=True)

            if new_url != url:
                print(f"转换 <img> src: {url[:40]}... -> {new_url}")
                # 添加 ./ 前缀使路径更明确
                if not new_url.startswith(('./','../', '/', 'http://', 'https://')):
                    new_url = './' + new_url

            return f'<img {before_src}src="{new_url}"{after_src}>'

        content = re.sub(img_pattern, replace_img_src, content)

        # 处理 <source srcset="..."> 标签
        source_pattern = r'<source\s+([^>]*?)srcset=["\'](.*?)["\']([^>]*?)>'

        def replace_source_srcset(match):
            before_srcset = match.group(1)
            url = match.group(2)
            after_srcset = match.group(3)

            print(f"找到 <source> 标签: srcset={url[:50]}...")

            # 转换 URL 为本地路径
            new_url = self.convert_link(url, "source", is_image=True)

            if new_url != url:
                print(f"转换 <source> srcset: {url[:40]}... -> {new_url}")
                # 添加 ./ 前缀使路径更明确
                if not new_url.startswith(('./', '../', '/', 'http://', 'https://')):
                    new_url = './' + new_url

            return f'<source {before_srcset}srcset="{new_url}"{after_srcset}>'

        content = re.sub(source_pattern, replace_source_srcset, content)

        print("HTML 图片标签处理完成")
        return content

    def analyze_links(self):
        """
        分析Markdown文件中的链接类型和数量

        功能：
        - 统计各类型链接的数量
        - 分类显示链接示例

        链接分类：
        - 外部URL：http/https/ftp等协议的链接
        - 本地文件(图片)：本地图片文件路径
        - 本地文件(附件)：本地文档/代码文件路径
        - 锚点链接：页面内跳转链接（#开头）
        - 其他本地链接：其他类型的本地文件

        返回：
            dict: 各类型链接的分类字典
        """
        print(f"\n分析文件中的链接: {self.input_file}")

        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return

        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)

        print(f"\n总共找到 {len(links)} 个链接:")
        print("-" * 50)

        categories = {
            '外部URL': [],
            '本地文件(图片)': [],
            '本地文件(附件)': [],
            '锚点链接': [],
            '其他本地链接': []
        }

        for text, url in links:
            if self.is_url(url):
                categories['外部URL'].append((text, url))
            elif url.startswith('#'):
                categories['锚点链接'].append((text, url))
            else:
                ext = self.get_file_extension(url)
                if ext in self.image_extensions:
                    categories['本地文件(图片)'].append((text, url))
                elif ext in self.attachment_extensions:
                    categories['本地文件(附件)'].append((text, url))
                else:
                    categories['其他本地链接'].append((text, url))

        for category, items in categories.items():
            if items:
                print(f"\n{category} ({len(items)} 个):")
                for text, url in items[:5]:  # 只显示前5个作为示例
                    print(f"  [{text}]({url})")
                if len(items) > 5:
                    print(f"  ... 还有 {len(items) - 5} 个")

        return categories

def main():
    """
    主程序入口

    流程：
    1. 请求用户输入Markdown文件路径
    2. 自动生成输出文件名（原文件名_converted.md）
    3. 创建转换器实例
    4. 分析文件中的链接
    5. 执行转换
    """
    print("Markdown链接转换器")
    print("=" * 50)

    # 请求用户输入文件路径
    try:
        input_file = input("\n请输入Markdown文件路径（默认：README.md）: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n使用默认文件路径...")
        input_file = ''

    # 如果用户没有输入，使用默认值
    if not input_file:
        input_file = 'README.md'

    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        return

    # 自动生成输出文件名
    base_name = os.path.splitext(input_file)[0]
    ext = os.path.splitext(input_file)[1]
    output_file = f"{base_name}_converted{ext}"

    # 创建转换器实例
    converter = MarkdownConverter(input_file=input_file, output_file=output_file)

    # 分析链接
    converter.analyze_links()

    # 执行转换
    print("\n" + "=" * 50)
    print(f"开始转换: {input_file} -> {output_file}")
    converter.process_markdown()

if __name__ == "__main__":
    main()