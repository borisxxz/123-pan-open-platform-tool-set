# 上传文件 API 文档

## 目录
- [上传流程说明](#上传流程说明)
  - [分片上传流程](#分片上传流程)
  - [单步上传流程](#单步上传流程)
  - [分片上传 vs 单步上传](#分片上传-vs-单步上传)
  - [注意事项](#注意事项)
- [分片上传相关API](#分片上传相关api)
  - [1. 创建文件](#1-创建文件)
  - [2. 上传分片](#2-上传分片)
  - [3. 上传完毕](#3-上传完毕)
- [单步上传相关API](#单步上传相关api)
  - [1. 获取上传域名](#1-获取上传域名)
  - [2. 单步上传](#2-单步上传)

---

## 上传流程说明

### 分片上传流程
1. **创建文件**
    1. 调用创建文件接口，接口返回的`reuse`为true时，表示秒传成功，上传结束。
    2. 非秒传情况将会返回预上传ID`preuploadID`与分片大小`sliceSize`，请将文件根据分片大小切分。
    3. 非秒传情况下返回`servers`为后续上传文件的对应域名（**重要**），多个任选其一。
2. **上传分片**
    1. 该步骤准备工作，按照`sliceSize`将文件切分，并计算每个分片的MD5。
    2. 调用上传分片接口，传入对应参数，注意此步骤 **Content-Type: multipart/form-data**。
3. **上传完毕**
    1. 调用上传完毕接口，若接口返回的`completed`为 ture 且`fileID`不为0时，上传完成。
    2. 若接口返回的`completed`为 false 时，则需间隔1秒继续轮询此接口，获取上传最终结果。

#### 上传文件时序图
```
用户端                  API服务器              存储服务器
  |                        |                      |
  |--1. 创建文件请求------->|                      |
  |   (文件MD5+大小)        |                      |
  |                        |                      |
  |<--返回preuploadID------|                      |
  |   sliceSize, servers   |                      |
  |                        |                      |
  |--2. 上传分片1----------|--------------------->|
  |   (preuploadID+分片)   |                      |
  |                        |                      |
  |--3. 上传分片2----------|--------------------->|
  |                        |                      |
  |--4. 上传分片N----------|--------------------->|
  |                        |                      |
  |--5. 上传完毕请求------->|                      |
  |   (preuploadID)        |                      |
  |                        |--检查分片完整性------>|
  |                        |<--验证通过-----------|
  |<--返回fileID-----------|                      |
  |   completed=true       |                      |
```

### 单步上传流程
1. **获取上传域名**
    1. 调用该接口，在接口返回中你将获得多个上传域名，后续上传任务需要使用。
2. **发起上传**
    1. 计算文件MD5；
    2. 使用获取到的上传域名发起上传；
    3. 注意此步骤 **Content-Type: multipart/form-data**。

### 分片上传 vs 单步上传

| 对比项 | 分片上传 | 单步上传 |
|--------|---------|---------|
| 适用场景 | 大文件（>1GB） | 小文件（≤1GB） |
| 文件大小限制 | 最大10GB | 最大1GB |
| 上传步骤 | 3步（创建→分片→完毕） | 2步（获取域名→上传） |
| 断点续传 | 支持 | 不支持 |
| 秒传 | 支持 | 支持 |
| 推荐程度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### 注意事项

1. **文件命名规则**
   - 文件名要小于256个字符
   - 不能包含以下字符：`"\/:*?|><`
   - 文件名不能全部是空格

2. **重要提示**
   - 分片上传时，`servers`域名非常重要，后续分片上传必须使用该域名
   - 上传分片和单步上传都必须设置 `Content-Type: multipart/form-data`
   - 上传完毕接口可能返回 `completed=false`，需要轮询直到 `completed=true`

3. **秒传机制**
   - 系统会根据文件MD5判断是否已存在相同文件
   - 如果已存在，直接返回 `reuse=true` 和 `fileID`，无需实际上传

---

## 分片上传相关API

### 1. 创建文件

**API：** POST 域名 + /upload/v2/file/create

**说明：**
+ 文件名要小于256个字符且不能包含以下任何字符："\/:*?|><
+ 文件名不能全部是空格
+ 开发者上传单文件大小限制10GB

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| parentFileID | number | **必填** | 父目录id，上传到根目录时填写 0 |
| filename | string | **必填** | 文件名要小于255个字符且不能包含以下任何字符："\/:*?|><。（注：不能重名）<br/>containDir 为 true 时，传入路径+文件名，例如：/你好/123/测试文件.mp4 |
| etag | string | **必填** | 文件md5 |
| size | number | **必填** | 文件大小，单位为 byte 字节 |
| duplicate | number | 非必填 | 当有相同文件名时，文件处理策略（1保留两者，新文件名将自动添加后缀，2覆盖原文件） |
| containDir | bool | 非必填 | 上传文件是否包含路径，默认false |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| fileID | number | 非必填 | 文件ID。当123云盘已有该文件,则会发生秒传。此时会将文件ID字段返回。唯一 |
| preuploadID | string | 必填 | 预上传ID(如果 reuse 为 true 时,该字段不存在) |
| reuse | boolean | 必填 | 是否秒传，返回true时表示文件已上传成功 |
| sliceSize | number | 必填 | 分片大小，必须按此大小生成文件分片再上传 |
| servers | array | 必填 | 上传地址 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/upload/v2/file/create' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...' \
--data '{
    "parentFileID": 0,
    "filename": "测试文件.mp4",
    "etag": "4b5c549c4abd0a079caf92d6cad24127",
    "size": 50650928
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"parentFileID\": 0,\n    \"filename\": \"测试文件.mp4\",\n    \"etag\": \"4b5c549c4abd0a079caf92d6cad24127\",\n    \"size\": 50650928\n}");
Request request = new Request.Builder()
  .url("https://open-api.123pan.com/upload/v2/file/create")
  .method("POST", body)
  .addHeader("Content-Type", "application/json")
  .addHeader("Platform", "open_platform")
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...")
  .build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v2/file/create",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl..."
  },
  "data": JSON.stringify({
    "parentFileID": 0,
    "filename": "测试文件.mp4",
    "etag": "4b5c549c4abd0a079caf92d6cad24127",
    "size": 50650928
  }),
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

**NodeJs - Axios**
```javascript
const axios = require('axios');
let data = JSON.stringify({
  "parentFileID": 0,
  "filename": "测试文件.mp4",
  "etag": "4b5c549c4abd0a079caf92d6cad24127",
  "size": 50650928
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/upload/v2/file/create',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...'
  },
  data : data
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
payload = json.dumps({
    "parentFileID": 0,
    "filename": "测试文件.mp4",
    "etag": "4b5c549c4abd0a079caf92d6cad24127",
    "size": 50650928
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...'
}
conn.request("POST", "/upload/v2/file/create", payload, headers)
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
    "fileID": 0,
    "reuse": false,
    "preuploadID": "WvjyUgonimrlBq2PVJ3bSyjPVJYP4IGeSxGdSly...",
    "sliceSize": 16777216,
    "servers": [
      "http://openapi-upload.123242.com"
    ]
  },
  "x-traceID": "2f41bbb4-93ab-459b-8dab-2204d3b3ff66_kong-db-5898fdd8c6-wnv6h"
}
```

---

### 2. 上传分片

**API：** POST 上传域名 + /upload/v2/file/slice

**说明：**
+ 上传域名是`创建文件`接口响应中的`servers`
+ **Content-Type: multipart/form-data**

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| preuploadID | string | **必填** | 预上传ID |
| sliceNo | number | **必填** | 分片序号，从1开始自增 |
| sliceMD5 | string | **必填** | 当前分片md5 |
| slice | file | **必填** | 分片二进制流 |

#### 返回数据
无

#### 示例
**请求示例**

**cURL**
```shell
curl --request POST \
  --url http://openapi-upload-dev.123242.com/upload/v2/file/slice \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5c...' \
  --header 'Platform: open_platform' \
  --header 'content-type: multipart/form-data' \
  --form preuploadID=WvjyUgonimrlI4sjB3sLG5sRBn3x43... \
  --form sliceNo=1 \
  --form sliceMD5=58f06dd588d8ffb3beb46ada6309436b \
  --form 'slice=@E:\新建文件夹\测试分片.txt.part1'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder().build();
MediaType mediaType = MediaType.parse("text/plain");
RequestBody body = new MultipartBody.Builder().setType(MultipartBody.FORM)
  .addFormDataPart("preuploadID","WvjyUgonimrlI4sjB3sLG5sRBn3x43...")
  .addFormDataPart("sliceNo","1")
  .addFormDataPart("sliceMD5","58f06dd588d8ffb3beb46ada6309436b")
  .addFormDataPart("slice","/D:/新建 文本文档 (4).txt",
    RequestBody.create(MediaType.parse("application/octet-stream"),
    new File("/D:/新建 文本文档 (4).txt")))
  .build();
Request request = new Request.Builder()
  .url("http://openapi-upload-dev.123242.com/upload/v2/file/slice")
  .method("POST", body)
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5c...")
  .addHeader("Platform", "open_platform")
  .build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var form = new FormData();
form.append("preuploadID", "WvjyUgonimrlI4sjB3sLG5sRBn3x43...");
form.append("sliceNo", "1");
form.append("sliceMD5", "58f06dd588d8ffb3beb46ada6309436b");
form.append("slice", fileInput.files[0], "/D:/新建 文本文档 (4).txt");

var settings = {
  "url": "http://openapi-upload-dev.123242.com/upload/v2/file/slice",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5c...",
    "Platform": "open_platform"
  },
  "processData": false,
  "mimeType": "multipart/form-data",
  "contentType": false,
  "data": form
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

**NodeJs - Axios**
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
let data = new FormData();
data.append('preuploadID', 'WvjyUgonimrlI4sjB3sLG5sRBn3x43...');
data.append('sliceNo', '1');
data.append('sliceMD5', '58f06dd588d8ffb3beb46ada6309436b');
data.append('slice', fs.createReadStream('/D:/新建 文本文档 (4).txt'));

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'http://openapi-upload-dev.123242.com/upload/v2/file/slice',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5c...',
    'Platform': 'open_platform',
    ...data.getHeaders()
  },
  data : data
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
import mimetypes
from codecs import encode

conn = http.client.HTTPConnection("openapi-upload-dev.123242.com")
dataList = []
boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=preuploadID;'))

dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))

dataList.append(encode("WvjyUgonimrlI4sjB3sLG5sRBn3x43..."))
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=sliceNo;'))

dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))

dataList.append(encode("1"))
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=sliceMD5;'))

dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))

dataList.append(encode("58f06dd588d8ffb3beb46ada6309436b"))
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=slice; filename={0}'.format('/D:/新建 文本文档 (4).txt')))

fileType = mimetypes.guess_type('/D:/新建 文本文档 (4).txt')[0] or 'application/octet-stream'
dataList.append(encode('Content-Type: {}'.format(fileType)))
dataList.append(encode(''))

with open('/D:/新建 文本文档 (4).txt', 'rb') as f:
  dataList.append(f.read())
dataList.append(encode('--'+boundary+'--'))
dataList.append(encode(''))
body = b'\r\n'.join(dataList)
payload = body
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5c...',
  'Platform': 'open_platform',
  'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
}
conn.request("POST", "/upload/v2/file/slice", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**响应示例**

```json
{
	"code": 0,
	"message": "ok",
	"data": null,
	"x-traceID": ""
}
```

---

### 3. 上传完毕

**API：** POST 域名 + /upload/v2/file/upload_complete

**说明：** 分片上传完成后请求

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| preuploadID | string | **必填** | 预上传ID |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| completed | bool | 必填 | 上传是否完成 |
| fileID | number | 必填 | 上传完成文件id |

#### 示例
**请求示例**

**cURL**
```shell
curl --request POST \
  --url https://open-api.123pan.com/upload/v2/file/upload_complete \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5c...' \
  --header 'Platform: open_platform' \
  --data '{
    "preuploadID":"WvjyUgonimrlI4sjB3sLG5sRBn3x43VRBx2dB..."
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\"preuploadID\": \"WvjyUgonimrlI4sjB3sLG5sRBn3x43VRBx2dB...\"}");
Request request = new Request.Builder()
  .url("https://open-api.123pan.com/upload/v2/file/upload_complete")
  .method("POST", body)
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5c...")
  .addHeader("Platform", "open_platform")
  .addHeader("Content-Type", "application/json")
  .build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v2/file/upload_complete",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5c...",
    "Platform": "open_platform",
    "Content-Type": "application/json"
  },
  "data": JSON.stringify({
    "preuploadID": "WvjyUgonimrlI4sjB3sLG5sRBn3x43VRBx2dB..."
  }),
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

**NodeJs - Axios**
```javascript
const axios = require('axios');
let data = JSON.stringify({
  "preuploadID": "WvjyUgonimrlI4sjB3sLG5sRBn3x43VRBx2dB..."
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/upload/v2/file/upload_complete',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5c...',
    'Platform': 'open_platform',
    'Content-Type': 'application/json'
  },
  data : data
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
payload = json.dumps({
  "preuploadID": "WvjyUgonimrlI4sjB3sLG5sRBn3x43VRBx2dB..."
})
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5c...',
  'Platform': 'open_platform',
  'Content-Type': 'application/json'
}
conn.request("POST", "/upload/v2/file/upload_complete", payload, headers)
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
		"completed": true,
		"fileID": 11522654
	},
	"x-traceID": "65562117-5c67-4d69-98cb-0f65201f83d3_test-kong-7787db5b5-wggzb"
}
```

---

## 单步上传相关API

### 1. 获取上传域名

**API：** GET 域名 + /upload/v2/file/domain

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
无

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| data | array | 必填 | 上传域名，存在多个可以任选其一 |

#### 示例
**请求示例**

**cURL**
```shell
curl --request GET \
  --url https://open-api.123pan.com/upload/v2/file/domain \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5c...' \
  --header 'Platform: open_platform'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("text/plain");
RequestBody body = RequestBody.create(mediaType, "");
Request request = new Request.Builder()
  .url("https://open-api.123pan.com/upload/v2/file/domain")
  .method("GET", body)
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5c...")
  .addHeader("Platform", "open_platform")
  .build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v2/file/domain",
  "method": "GET",
  "timeout": 0,
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5c...",
    "Platform": "open_platform"
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
  url: 'https://open-api.123pan.com/upload/v2/file/domain',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5c...',
    'Platform': 'open_platform'
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

conn = http.client.HTTPSConnection("open-api.123pan.com")
payload = ''
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5c...',
  'Platform': 'open_platform'
}
conn.request("GET", "/upload/v2/file/domain", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**响应示例**

```json
{
	"code": 0,
	"message": "ok",
	"data": [
		"https://openapi-upload.123pan.com"
	],
	"x-traceID": ""
}
```

---

### 2. 单步上传

**API：** POST 上传域名 + /upload/v2/file/single/create

**说明：**
+ 文件名要小于256个字符且不能包含以下任何字符："\/:*?|><
+ 文件名不能全部是空格
+ 此接口限制开发者上传单文件大小为1GB
+ 上传域名是`获取上传域名`接口响应中的域名
+ 此接口用于实现小文件单步上传一次HTTP请求交互即可完成上传

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| parentFileID | number | **必填** | 父目录id，上传到根目录时填写 0 |
| filename | string | **必填** | 文件名要小于255个字符且不能包含以下任何字符："\/:*?|><。（注：不能重名）<br/>containDir 为 true 时，传入路径+文件名，例如：/你好/123/测试文件.mp4 |
| etag | string | **必填** | 文件md5 |
| size | number | **必填** | 文件大小，单位为 byte 字节 |
| file | file | **必填** | 文件二进制流 |
| duplicate | number | 非必填 | 当有相同文件名时，文件处理策略（1保留两者，新文件名将自动添加后缀，2覆盖原文件） |
| containDir | bool | 非必填 | 上传文件是否包含路径，默认false |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| fileID | number | 必填 | 文件ID。当123云盘已有该文件,则会发生秒传。此时会将文件ID字段返回。唯一 |
| completed | bool | 必填 | 是否上传完成（如果 completed 为 true 时，则说明上传完成） |

#### 示例
**请求示例**

**cURL**
```shell
curl --request POST \
  --url https://openapi-upload.123242.com/upload/v2/file/single/create \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1...' \
  --header 'Platform: open_platform' \
  --header 'content-type: multipart/form-data' \
  --form 'file=@C:\Users\mfy\Downloads\测试.exe' \
  --form parentFileID=11522394 \
  --form 'filename=测试.exe' \
  --form etag=511215951b857390c3f30c17d0dae8ee \
  --form size=35763200
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("text/plain");
RequestBody body = new MultipartBody.Builder().setType(MultipartBody.FORM)
  .addFormDataPart("file","/D:/新建 文本文档 (4).txt",
    RequestBody.create(MediaType.parse("application/octet-stream"),
    new File("/D:/新建 文本文档 (4).txt")))
  .addFormDataPart("parentFileID","11522394")
  .addFormDataPart("filename","新建 文本文档 (4).txt")
  .addFormDataPart("etag","511215951b857390c3f30c17d0dae8ee")
  .addFormDataPart("size","35763200")
  .build();
Request request = new Request.Builder()
  .url("https://openapi-upload.123242.com/upload/v2/file/single/create")
  .method("POST", body)
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1...")
  .addHeader("Platform", "open_platform")
  .build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var form = new FormData();
form.append("file", fileInput.files[0], "/D:/新建 文本文档 (4).txt");
form.append("parentFileID", "11522394");
form.append("filename", "新建 文本文档(4).txt");
form.append("etag", "511215951b857390c3f30c17d0dae8ee");
form.append("size", "35763200");

var settings = {
  "url": "https://openapi-upload.123242.com/upload/v2/file/single/create",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1...",
    "Platform": "open_platform"
  },
  "processData": false,
  "mimeType": "multipart/form-data",
  "contentType": false,
  "data": form
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

**NodeJs - Axios**
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
let data = new FormData();
data.append('file', fs.createReadStream('/D:/新建 文本文档 (4).txt'));
data.append('parentFileID', '11522394');
data.append('filename', '新建 文本文档(4).txt');
data.append('etag', '511215951b857390c3f30c17d0dae8ee');
data.append('size', '35763200');

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://openapi-upload.123242.com/upload/v2/file/single/create',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1...',
    'Platform': 'open_platform',
    ...data.getHeaders()
  },
  data : data
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
import mimetypes
from codecs import encode

conn = http.client.HTTPSConnection("openapi-upload.123242.com")
dataList = []
boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'

# 文件字段
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=file; filename={0}'.format('/D:/新建 文本文档 (4).txt')))

fileType = mimetypes.guess_type('/D:/新建 文本文档 (4).txt')[0] or 'application/octet-stream'
dataList.append(encode('Content-Type: {}'.format(fileType)))
dataList.append(encode(''))

with open('/D:/新建 文本文档 (4).txt', 'rb') as f:
  dataList.append(f.read())

# parentFileID
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=parentFileID;'))
dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))
dataList.append(encode("11522394"))

# filename
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=filename;'))
dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))
dataList.append(encode("新建 文本文档(4).txt"))

# etag
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=etag;'))
dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))
dataList.append(encode("511215951b857390c3f30c17d0dae8ee"))

# size
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=size;'))
dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))
dataList.append(encode("35763200"))

dataList.append(encode('--'+boundary+'--'))
dataList.append(encode(''))
body = b'\r\n'.join(dataList)
payload = body
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1...',
  'Platform': 'open_platform',
  'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
}
conn.request("POST", "/upload/v2/file/single/create", payload, headers)
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
		"fileID": 11522653,
		"completed": true
	},
	"x-traceID": ""
}
```

---

> 更新日期: 2025-10-01
> 基于: 123云盘开放平台官方文档 v2
> 原文: https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/
