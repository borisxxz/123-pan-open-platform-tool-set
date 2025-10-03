# Markdown与123网盘互转工具集

这是一套用于Markdown文件与123网盘之间互相转换链接的**完全独立**工具集，包含两个核心工具：

1. **本地Markdown转123云盘在线.py** - 将本地资源上传到123网盘并替换链接
2. **在线Markdown转本地.py** - 将在线资源下载到本地并替换链接

---

## 🚀 工具一：本地Markdown转123云盘在线

将Markdown文件中的本地图片和附件批量上传到123网盘并自动替换为在线链接。

### ✨ 功能特点

- 🔍 **智能提取** - 自动识别Markdown中的各种图片和附件格式
- 🖼️ **图片上传** - 批量上传图片到123网盘图床，获取CDN加速链接
- 📎 **附件上传** - 批量上传附件到123网盘直链目录，获取直链下载地址
- 🔄 **自动替换** - 自动更新Markdown文件中的图片和附件链接
- 💾 **安全备份** - 更新前自动创建备份文件
- 📁 **目录处理** - 支持处理整个目录或递归处理子目录
- 🎯 **灵活控制** - 支持只上传不更新模式

### 📦 支持的文件格式

#### 图片格式（上传到图床）
- JPEG/JPG
- PNG
- GIF
- BMP
- WebP
- SVG
- TIFF/TIF
- 最大文件大小：100MB

#### 附件格式（上传到直链目录）
- 所有非图片文件（PDF、ZIP、DOCX等）
- 最大文件大小：10GB

### 🔧 支持的Markdown语法

#### 图片语法
1. **标准Markdown语法**: `![alt](image.jpg)`
2. **HTML img标签**: `<img src="image.jpg">`

#### 附件语法
1. **标准Markdown链接**: `[文件名](file.pdf)`
2. **HTML链接标签**: `<a href="file.zip">下载</a>`

### ⚙️ 使用方法

#### 基本使用

```bash
# 处理单个Markdown文件（图片+附件）
python "本地Markdown转123云盘在线.py" document.md

# 处理目录中的所有Markdown文件
python "本地Markdown转123云盘在线.py" ./docs/

# 递归处理子目录
python "本地Markdown转123云盘在线.py" ./docs/ --recursive
```

#### 高级选项

```bash
# 只上传文件不更新Markdown
python "本地Markdown转123云盘在线.py" document.md --upload-only

# 不创建备份文件
python "本地Markdown转123云盘在线.py" document.md --no-backup

# 使用自定义图床目录
python "本地Markdown转123云盘在线.py" document.md --image-dir "your-image-dir-id"

# 使用自定义附件目录
python "本地Markdown转123云盘在线.py" document.md --attachment-dir "your-attachment-dir-id"
```

#### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | Markdown文件或目录路径 | 必填 |
| `--recursive`, `-r` | 递归处理子目录 | False |
| `--upload-only`, `-u` | 只上传不更新文件 | False |
| `--no-backup` | 不创建备份文件 | False |
| `--image-dir` | 图床上传根目录ID | 预设值 |
| `--attachment-dir` | 附件上传根目录ID（直链目录） | 预设值 |

### 📝 使用示例

#### 示例1：处理单个文档

```bash
python "本地Markdown转123云盘在线.py" my_article.md
```

输出：
```
从Markdown中提取到 3 个本地图片
从Markdown中提取到 1 个本地附件

开始上传 3 个图片到图床...
[1/3] 上传图片: image1.jpg
image1.jpg 上传成功: https://vip.123pan.cn/xxx/image1.jpg
[2/3] 上传图片: image2.png
image2.png 上传成功: https://vip.123pan.cn/xxx/image2.png
[3/3] 上传图片: image3.gif
image3.gif 上传成功: https://vip.123pan.cn/xxx/image3.gif

上传完成，成功上传 3 个图片

开始上传 1 个附件到直链目录...
[1/1] 上传附件: document.pdf
document.pdf 上传成功: https://vip.123pan.cn/xxx/document.pdf

上传完成，成功上传 1 个附件

创建备份文件: my_article.md.bak
Markdown文件更新成功，替换了 3 个图片链接
Markdown文件更新成功，替换了 1 个附件链接

处理完成!
   找到图片: 3 个
   上传图片: 3 个
   找到附件: 1 个
   上传附件: 1 个
```

#### 示例2：批量处理目录

```bash
python "本地Markdown转123云盘在线.py" ./articles/ --recursive
```

输出：
```
找到 5 个Markdown文件

处理完成统计:
   文件处理: 5/5 成功
   图片找到: 12 个
   图片上传: 12 个
   附件找到: 3 个
   附件上传: 3 个
```

### 🔐 配置要求

工具需要与123网盘开放平台配置文件配合使用：

1. **配置文件位置**: 项目根目录的 `config.txt`
2. **必要配置**:
   ```ini
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   ```

### 📋 工作流程

1. **解析Markdown文件** - 提取所有本地图片和附件路径
2. **验证文件** - 检查文件是否存在和支持的格式
3. **上传图片** - 批量上传图片到指定的图床目录，获取CDN链接
4. **上传附件** - 批量上传附件到指定的直链目录，获取直链
5. **更新Markdown** - 替换原始链接为CDN/直链
6. **创建备份** - 保存原始文件的备份

### ⚠️ 注意事项

1. **图片限制**: 单个图片文件最大100MB
2. **附件限制**: 单个附件文件最大10GB
3. **备份文件**: 默认会创建 `.bak` 备份文件
4. **网络链接**: 已经是网络链接的文件会被跳过
5. **路径处理**: 自动处理相对路径和绝对路径
6. **目录自动创建**: 为每个Markdown文件自动创建同名目录存储图片和附件

---

## 🚀 工具二：在线Markdown转本地

将Markdown文件中的外部链接（包括123网盘链接和其他外部资源）下载到本地并自动替换为本地引用。

### ✨ 功能特点

- 🌐 **智能下载** - 自动识别和下载外部资源链接
- 🖼️ **图片处理** - 图片自动保存到 `images` 文件夹
- 📎 **附件处理** - 附件自动保存到 `attachments` 文件夹
- 🔄 **自动替换** - 自动更新Markdown文件中的链接为本地路径
- 📊 **进度显示** - 实时显示下载进度和状态
- 🎯 **去重机制** - 相同URL只下载一次
- 💾 **Data URI支持** - 支持将data URI格式转换为本地文件
- 🏷️ **HTML标签支持** - 支持处理 `<img>` 和 `<source>` 标签

### 📦 支持的文件格式

#### 图片格式（保存到images文件夹）
- JPEG/JPG、PNG、GIF、BMP、SVG
- WebP、ICO、TIFF/TIF

#### 附件格式（保存到attachments文件夹）
- 文档：PDF、DOC/DOCX、XLS/XLSX、PPT/PPTX
- 压缩包：ZIP、TAR、GZ、7Z、RAR
- 代码：PY、JAVA、CPP、JS、TS等
- 其他：配置文件、可执行文件等100+种格式

### 🔧 支持的Markdown语法

#### 图片语法
1. **标准Markdown语法**: `![alt](https://example.com/image.jpg)`
2. **HTML img标签**: `<img src="https://example.com/image.jpg">`
3. **HTML source标签**: `<source src="https://example.com/image.jpg">`
4. **Data URI格式**: `![alt](data:image/png;base64,...)`

#### 附件语法
1. **标准Markdown链接**: `[文件名](https://example.com/file.pdf)`
2. **HTML链接标签**: `<a href="https://example.com/file.zip">下载</a>`

### ⚙️ 使用方法

#### 基本使用

```bash
# 处理单个Markdown文件（默认）
python "在线Markdown转本地.py"

# 处理指定的Markdown文件
python "在线Markdown转本地.py" -i input.md -o output.md

# 使用默认文件名
python "在线Markdown转本地.py"  # 输入: README.md, 输出: README_converted.md
```

#### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i` / `--input` | 输入的Markdown文件路径 | README.md |
| `-o` / `--output` | 输出的Markdown文件路径 | README_converted.md |

### 📝 使用示例

#### 示例1：转换README文件

```bash
python "在线Markdown转本地.py"
```

输出：
```
已创建images和attachments文件夹
正在读取Markdown文件: README.md
找到 5 个图片链接
找到 2 个附件链接

正在下载: https://example.com/logo.png...
已下载: images/logo.png
正在下载: https://example.com/screenshot.jpg...
已下载: images/screenshot.jpg

正在下载: https://example.com/manual.pdf...
已下载: attachments/manual.pdf

成功替换 5 个图片链接
成功替换 2 个附件链接
转换完成！输出文件: README_converted.md
```

#### 示例2：转换自定义文件

```bash
python "在线Markdown转本地.py" -i article.md -o article_local.md
```

### 📋 工作流程

1. **创建目录** - 自动创建 `images` 和 `attachments` 文件夹
2. **解析Markdown** - 提取所有外部资源链接
3. **分类资源** - 根据扩展名区分图片和附件
4. **下载文件** - 批量下载资源到对应文件夹
5. **去重处理** - 相同URL只下载一次，复用本地路径
6. **更新链接** - 替换Markdown中的外部链接为本地路径
7. **保存文件** - 生成新的Markdown文件

### ⚠️ 注意事项

1. **网络依赖**: 需要稳定的网络连接
2. **文件覆盖**: 同名文件会自动添加数字后缀（如 image_1.jpg）
3. **URL解码**: 自动处理URL编码的文件名
4. **超时设置**: 下载超时时间为30秒
5. **错误处理**: 下载失败的文件会保留原始链接
6. **Data URI**: 支持将base64编码的图片转换为本地文件

---

## 🔗 两个工具的配合使用

### 场景1：发布到不同平台

```bash
# 步骤1：将本地Markdown转为在线版本（适合发布到网络）
python "本地Markdown转123云盘在线.py" article.md

# 步骤2：如需备份或离线使用，再转回本地
python "在线Markdown转本地.py" -i article.md -o article_local.md
```

### 场景2：迁移文档

```bash
# 从其他平台下载Markdown及资源
python "在线Markdown转本地.py" -i downloaded.md -o local.md

# 整理后上传到123网盘
python "本地Markdown转123云盘在线.py" local.md
```

### 场景3：协作编辑

- **编辑时**: 使用在线版本，所有人都能访问最新资源
- **归档时**: 转为本地版本，确保资源永久保存

---

## 🔐 总体配置要求

### 工具一（本地转在线）的配置

需要在项目根目录创建 `config.txt` 文件：

```ini
# 123网盘开放平台配置文件
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
```

### 工具二（在线转本地）的配置

无需配置文件，仅需Python标准库和requests库：

```bash
pip install requests
```

---

## 🛠️ 故障排除

### 工具一常见错误

1. **配置文件不存在**
   ```
   配置文件不存在: config.txt
   ```
   **解决**: 确保 `config.txt` 文件在项目根目录且包含正确的API凭据

2. **图片上传失败**
   ```
   image.jpg 上传出错: 文件大小超过100MB限制
   ```
   **解决**: 压缩图片或使用其他方式处理大文件

3. **附件上传失败**
   ```
   document.pdf 上传出错: 文件大小超过10GB限制
   ```
   **解决**: 分割文件或使用其他上传方式

4. **文件权限错误**
   ```
   更新Markdown文件失败: Permission denied
   ```
   **解决**: 检查文件权限，确保有写入权限

### 工具二常见错误

1. **网络连接错误**
   ```
   下载失败: Connection timeout
   ```
   **解决**: 检查网络连接，确认URL可访问

2. **文件下载失败**
   ```
   下载失败: 404 Not Found
   ```
   **解决**: URL可能已失效，检查链接是否正确

3. **依赖库缺失**
   ```
   ModuleNotFoundError: No module named 'requests'
   ```
   **解决**: 安装requests库
   ```bash
   pip install requests
   ```

4. **权限错误**
   ```
   Permission denied: images/
   ```
   **解决**: 确保有创建目录和写入文件的权限

### 调试模式

**工具一调试**：使用 `--upload-only` 模式只上传文件

```bash
python "本地Markdown转123云盘在线.py" document.md --upload-only
```

这样可以验证上传是否正常工作，然后再进行文件更新。

**工具二调试**：直接运行会显示详细的下载进度和错误信息

```bash
python "在线Markdown转本地.py" -i test.md -o test_output.md
```

---

## 📄 文件结构

```
Markdown的互相转换/
├── 本地Markdown转123云盘在线.py    # 本地转在线工具（1332行代码）
├── 在线Markdown转本地.py           # 在线转本地工具（932行代码）
├── README.md                       # 本说明文档
└── ../config.txt                   # 配置文件（仅工具一需要）
```

---

## 📝 工具特点总结

### 工具一：本地转在线
- ✅ **完全独立** - 不依赖任何外部模块，所有功能内置
- ✅ **自包含** - 集成图床管理、直链管理、配置读取等
- ✅ **易于部署** - 只需复制单个Python文件即可使用
- ✅ **双重上传** - 同时支持图片（图床）和附件（直链）
- ✅ **批量处理** - 支持目录和递归处理

### 工具二：在线转本地
- ✅ **轻量级** - 仅依赖requests库
- ✅ **智能分类** - 自动区分图片和附件
- ✅ **去重机制** - 相同资源只下载一次
- ✅ **多格式支持** - 支持100+种文件格式
- ✅ **容错能力强** - 下载失败保留原始链接

---

## 🔄 版本历史

### 工具一版本历史
- **v2.0** (2025-10-03)
  - 新增附件上传到直链目录功能
  - 修复V2 API上传问题
  - 优化multipart/form-data上传方式
  - 完善错误处理和日志输出
- **v1.0** (2025-10-03)
  - 基础功能实现
  - 支持多种Markdown语法
  - 批量处理和目录递归
  - 自动备份机制

### 工具二版本历史
- **v1.0** (2025-10-03)
  - 初始版本发布
  - 支持图片和附件下载
  - Data URI格式支持
  - HTML标签处理
  - 智能去重机制

---

## 📞 技术支持

如果遇到问题或需要帮助，请：

**工具一（本地转在线）**：
1. 检查配置文件是否正确
2. 确认网络连接正常
3. 查看123网盘开放平台API状态
4. 确认图床和直链空间已启用
5. 参考项目根目录的 README.md 文档

**工具二（在线转本地）**：
1. 确认网络连接正常
2. 检查requests库是否已安装
3. 确认URL链接是否有效
4. 检查文件和目录权限
5. 查看控制台输出的详细错误信息

---

## 💡 使用建议

### 通用建议
1. **首次使用**: 先用小文件测试，确保工具正常工作
2. **大批量处理**: 建议分批处理，避免一次性处理过多文件
3. **备份重要文件**: 虽然工具会自动备份（工具一），但重要文件建议手动额外备份
4. **定期清理**: 定期清理不需要的`.bak`备份文件

### 工具一专属建议
1. **目录规划**: 在123网盘提前创建好图床和直链目录
2. **定期检查**: 定期检查云盘空间使用情况
3. **流量监控**: 关注直链流量使用情况

### 工具二专属建议
1. **网络环境**: 在稳定的网络环境下使用
2. **资源有效性**: 优先处理可靠来源的资源链接
3. **本地存储**: 确保本地有足够的存储空间

---

**Enjoy Markdown converting with 123 Pan! 🖼️✨📝**