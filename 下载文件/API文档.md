# 下载文件 API 文档

## 目录
- [API说明](#api说明)
  - [1. 获取单个文件详情](#1-获取单个文件详情)
  - [2. 获取下载链接](#2-获取下载链接)
- [工具使用说明](#工具使用说明)
  - [功能特点](#功能特点)
  - [使用方法](#使用方法)
  - [配置说明](#配置说明)
  - [使用示例](#使用示例)
  - [错误处理](#错误处理)
  - [注意事项](#注意事项)

---

## API说明

### 1. 获取单个文件详情

**API：** GET 域名 + /api/v1/file/detail

**说明：** 支持查询单文件夹包含文件大小

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileID | number | 必填 | 文件ID |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| fileID | number | 必填 | 文件ID |
| filename | string | 必填 | 文件名 |
| type | number | 必填 | 0-文件  1-文件夹 |
| size | number | 必填 | 文件大小 |
| etag | string | 必填 | md5 |
| status | number | 必填 | 文件审核状态。 大于 100 为审核驳回文件 |
| parentFileID | number | 必填 | 父级ID |
| createAt | string | 必填 | 文件创建时间 |
| trashed | number | 必填 | 该文件是否在回收站<br/>0否、1是 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/file/detail?fileID=14749954' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJI...'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/file/detail?fileID=14749954")
.method("GET", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJI...")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/file/detail?fileID=14749954",
  "method": "GET",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJI..."
  },
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

**NodeJs - Axios**
```javascript
const axios = require('axios');

let config = {
  method: 'get',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/file/detail?fileID=14749954',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJI...'
  }
};

axios.request(config)
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  });
```

**Python - http.client**
```python
import http.client
import json

conn = http.client.HTTPSConnection("open-api.123pan.com")
payload = ''
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJI...'
}
conn.request("GET", "/api/v1/file/detail?fileID=14749954", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**响应示例**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "fileID": 14749954,
    "filename": "Keyshot_win64_2024.exe",
    "type": 0,
    "size": 1163176272,
    "etag": "ab6dd0cfca2da20f84f55d2ed73a8c3d",
    "status": 2,
    "parentFileID": 14749926,
    "createAt": "2025-02-28 09:25:54",
    "trashed": 0
  },
  "x-traceID": "4391f785-4395-41f9-a299-ac1ddc8dc45d_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 2. 获取下载链接

**API：** GET 域名 + /api/v1/file/download_info

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileId | number | 是 | 文件id |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| downloadUrl | string | 是 | 下载地址 |

#### 异常返回
| **code** | **异常原因** | **示例message** |
| :---: | :---: | --- |
| 5113 | 自用下载流量不足 | 您今日自用下载流量已超出1GB上限，升级VIP会员可无限流量下载   |
| 5066 | 文件不存在 | 文件不存在，检查传入fileId是否正确 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/file/download_info?fileId=14749954' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/file/download_info?fileId=14749954")
.method("GET", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/file/download_info?fileId=14749954",
  "method": "GET",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl..."
  },
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

**NodeJs - Axios**
```javascript
const axios = require('axios');

let config = {
  method: 'get',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/file/download_info?fileId=14749954',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...'
  }
};

axios.request(config)
.then((response) => {
  console.log(JSON.stringify(response.data));
})
.catch((error) => {
  console.log(error);
});
```

**Python - http.client**
```python
import http.client
import json

conn = http.client.HTTPSConnection("open-api.123pan.com")
payload = ''
headers = {
  'Content-Type': 'application/json',
  'Platform': 'open_platform',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...'
}
conn.request("GET", "/api/v1/file/download_info?fileId=14749954", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**响应示例**

```json
{
    "code": 0,
    "message": "ok",
    "data": {
        "downloadUrl": "https://download-cdn.cjjd19.com/123-61/ab6dd0cf/18...(过长省略)"
    },
    "x-traceID": "68a2d07c-72d3-4fc6-a0a7-965dfea99dc0_kong-db-5898fdd8c6-wnv6h"
}
```

---

## 工具使用说明

### 功能特点

- ✅ 自动获取访问令牌（参照查询文件.py的方式）
- ✅ 支持命令行参数和交互式输入两种方式
- ✅ 实时显示下载进度
- ✅ 支持大文件分块下载
- ✅ 自动创建保存目录
- ✅ 完善的错误处理和异常捕获

### 使用方法

#### 1. 交互式使用（推荐）

直接运行程序，按提示输入：

```bash
python 下载文件.py
```

程序会提示您：
1. 输入要下载的文件ID
2. 输入保存路径（可选，直接回车使用默认路径）

#### 2. 命令行参数使用

**基本用法**
```bash
# 指定文件ID
python 下载文件.py --file-id 12345

# 指定文件ID和保存路径
python 下载文件.py --file-id 12345 --save-path "D:/downloads/myfile.txt"
```

**使用自定义令牌**
```bash
# 使用访问令牌
python 下载文件.py --file-id 12345 --token "your_access_token"

# 使用客户端ID和密钥
python 下载文件.py --file-id 12345 --client-id "your_client_id" --client-secret "your_client_secret"
```

#### 3. 命令行参数说明

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--file-id` | `-f` | 要下载的文件ID | `--file-id 12345` |
| `--save-path` | `-s` | 保存路径 | `--save-path "D:/downloads/file.txt"` |
| `--token` | `-t` | 访问令牌 | `--token "eyJhbGci..."` |
| `--client-id` | | 客户端ID | `--client-id "your_id"` |
| `--client-secret` | | 客户端密钥 | `--client-secret "your_secret"` |

### 配置说明

程序会自动从项目根目录的 `config.txt` 文件读取配置信息。

配置文件格式示例：
```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
```

如需使用自己的配置，可以：
1. 修改项目根目录的 `config.txt` 文件
2. 使用命令行参数 `--client-id` 和 `--client-secret`
3. 使用命令行参数 `--token` 直接提供访问令牌

### 使用示例

#### 示例1：交互式下载
```bash
$ python 下载文件.py
============================================================
123盘文件下载工具
============================================================
正在获取访问令牌...
访问令牌获取成功
请输入要下载的文件ID: 14749954
请输入保存路径 (直接回车使用默认路径):

开始下载文件ID: 14749954
开始下载文件 ID: 14749954
保存路径: file_14749954
下载进度: 100.0% (1024000/1024000 bytes)
文件下载完成: file_14749954

✅ 下载成功！
```

#### 示例2：命令行下载
```bash
$ python 下载文件.py -f 14749954 -s "downloads/myfile.zip"
============================================================
123盘文件下载工具
============================================================
正在获取访问令牌...
访问令牌获取成功
使用命令行参数指定的文件ID: 14749954
使用命令行参数指定的保存路径: downloads/myfile.zip

开始下载文件ID: 14749954
开始下载文件 ID: 14749954
保存路径: downloads/myfile.zip
下载进度: 100.0% (2048000/2048000 bytes)
文件下载完成: downloads/myfile.zip

✅ 下载成功！
```

### 错误处理

程序包含完善的错误处理机制：

- **令牌获取失败**：会显示具体错误信息
- **文件ID无效**：会提示重新输入（交互模式）
- **文件不存在**：会显示API返回的错误信息
- **网络错误**：会显示连接或下载错误
- **磁盘空间不足**：会显示文件保存错误
- **用户中断**：支持Ctrl+C优雅退出

### 注意事项

1. **文件ID获取**：可以通过查询文件.py程序获取文件ID
2. **保存路径**：如果不指定，程序会尝试从下载URL中提取文件名
3. **目录创建**：程序会自动创建不存在的目录
4. **进度显示**：支持显示下载进度和文件大小
5. **流量限制**：注意123盘的下载流量限制（每日1GB）

### 依赖库

程序使用以下Python标准库和第三方库：

```python
import requests      # HTTP请求库
import os           # 操作系统接口
import sys          # 系统相关参数
import json         # JSON处理
import http.client  # HTTP客户端
import argparse     # 命令行参数解析
from urllib.parse import urlparse  # URL解析
from pathlib import Path          # 路径操作
from typing import Optional       # 类型提示
```

安装依赖：
```bash
pip install requests
```

### 获取帮助

运行以下命令查看帮助信息：

```bash
python 下载文件.py --help
```

---

> 更新日期: 2025-10-01
> 基于: 123云盘开放平台官方文档 v1
> 原文: https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/
