# 图床 API 文档

## 目录
- [上传流程说明](#上传流程说明)
- [图片管理](#图片管理)
  - [1. 删除图片](#1-删除图片)
  - [2. 移动图片](#2-移动图片)
- [获取图片信息](#获取图片信息)
  - [1. 获取图片列表](#1-获取图片列表)
  - [2. 获取图片详情](#2-获取图片详情)
- [上传图片](#上传图片)
  - [1. 创建目录](#1-创建目录)
  - [2. 创建文件](#2-创建文件)
  - [3. 获取上传地址&上传分片](#3-获取上传地址上传分片)
  - [4. 上传完毕](#4-上传完毕)
  - [5. 异步轮询获取上传结果](#5-异步轮询获取上传结果)
- [复制云盘图片](#复制云盘图片)
  - [1. 创建复制任务](#1-创建复制任务)
  - [2. 获取复制任务详情](#2-获取复制任务详情)
  - [3. 获取复制失败文件列表](#3-获取复制失败文件列表)
- [图床离线迁移](#图床离线迁移)
  - [1. 创建离线迁移任务](#1-创建离线迁移任务)
  - [2. 获取离线迁移任务](#2-获取离线迁移任务)

---

## 上传流程说明

1. **创建文件**
    1. 请求创建文件接口，接口返回的`reuse`为true时，表示秒传成功，上传结束。
    2. 非秒传情况将会返回预上传ID`preuploadID`与分片大小`sliceSize`，请将文件根据分片大小切分。
2. **获取上传地址**
    1. 非秒传时，携带返回的`preuploadID`，自定义分片序号`sliceNo`(从数字1开始)。
    2. 获取上传地址`presignedURL`。
3. **上传文件**
    1. 向返回的地址`presignedURL`发送PUT请求，上传文件分片。
    2. 注：PUT请求的header中请不要携带Authorization、Platform参数。
4. **文件比对（非必需）**
    1. 所有分片上传后，调用列举已上传分片接口，将本地与云端的分片MD5比对。
    2. 注：如果您的文件小于`sliceSize`，该操作将会返回空值，可以跳过此步。
5. **上传完成**
    1. 请求上传完毕接口，若接口返回的`async`为false且`fileID`不为0时，上传完成。
    2. 若接口返回的`async`为true时，则需下一步，调用异步轮询获取上传结果接口，获取上传最终结果。
6. **轮询查询**
    1. 若异步轮询获取上传结果接口返回的`completed`为false，请至少1秒后再次调用此接口，查询上传结果。
    2. 注：该步骤需要等待，建议轮询获取结果。123云盘服务器会校验用户预上传时的MD5与实际上传成功的MD5是否一致。

### 说明

图床上传流程与文件上传类似，主要区别在于：
- 图床文件会自动获得下载直链
- 适合用于图片等静态资源的存储和分发
- 支持自定义域名访问

---

## 图片管理

### 1. 删除图片

**API:** POST 域名 + /api/v1/oss/file/delete

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileIDs | array | **必填** | 文件id数组,参数长度最大不超过100 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/oss/file/delete' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "fileIDs": [
        "yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO"
    ]
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"fileIDs\": [\n        \"yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO\"\n    ]\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/file/delete")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/file/delete",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "fileIDs": [
      "yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO"
    ]
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
  "fileIDs": [
    "yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO"
  ]
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/oss/file/delete',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
    "fileIDs": [
        "yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO"
    ]
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/api/v1/oss/file/delete", payload, headers)
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
    "x-traceID": "821c1654-3f6f-4536-b4a1-59bfb714b82b_kong-db-5898fdd8c6-d258b"
}
```

---

### 2. 移动图片

**API:** POST 域名 + /api/v1/oss/file/move

**说明:** 批量移动文件,单级最多支持100个

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileIDs | array | **必填** | 文件id数组 |
| toParentFileID | string | **必填** | 要移动到的目标文件夹id,移动到根目录时填写空 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/oss/file/move' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "fileIDs": [
        "yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO"
    ],
    "toParentFileID": "ymjew503t0l000d7w32x751ex14jo8adDIYPAIDOBIY0DcxvDwFO"
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"fileIDs\": [\n        \"yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO\"\n    ],\n    \"toParentFileID\": \"ymjew503t0l000d7w32x751ex14jo8adDIYPAIDOBIY0DcxvDwFO\" \n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/file/move")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/file/move",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "fileIDs": [
      "yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO"
    ],
    "toParentFileID": "ymjew503t0l000d7w32x751ex14jo8adDIYPAIDOBIY0DcxvDwFO"
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
  "fileIDs": [
    "yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO"
  ],
  "toParentFileID": "ymjew503t0l000d7w32x751ex14jo8adDIYPAIDOBIY0DcxvDwFO"
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/oss/file/move',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
  "fileIDs": [
    "yk6baz03t0l000d7w33fbyt8704m2bohDIYPAIDOBIY0DcxvDwFO"
  ],
  "toParentFileID": "ymjew503t0l000d7w32x751ex14jo8adDIYPAIDOBIY0DcxvDwFO"
})
headers = {
  'Content-Type': 'application/json',
  'Platform': 'open_platform',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/api/v1/oss/file/move", payload, headers)
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
    "x-traceID": "a6fd87a0-b963-44d5-bdfd-e3c30e22c83d_kong-db-5898fdd8c6-t5pvc"
}
```

---

## 获取图片信息

### 1. 获取图片列表

**API:** POST 域名 + /api/v1/oss/file/list

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| parentFileId | string | 选填 | 父级目录Id, 默认为空表示筛选根目录下的文件 |
| limit | number | **必填** | 每页文件数量,最大不超过100 |
| startTime | number | 选填 | 筛选开始时间(时间戳格式,例如 1730390400) |
| endTime | number | 选填 | 筛选结束时间(时间戳格式,例如 1730390400) |
| lastFileId | string | 选填 | 翻页查询时需要填写 |
| type | number | **必填** | 固定为1 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| lastFileId | string | **必填** | -1代表最后一页(无需再翻页查询) 其他代表下一页开始的文件id,携带到请求参数中 |
| fileList | array | **必填** | 文件列表 |
| fileList.fileId | string | **必填** | 文件ID |
| fileList.filename | string | **必填** | 文件名 |
| fileList.type | number | **必填** | 0-文件 1-文件夹 |
| fileList.size | number | **必填** | 文件大小 |
| fileList.etag | string | **必填** | md5 |
| fileList.status | number | **必填** | 文件审核状态。大于100为审核驳回文件 |
| fileList.createAt | string | **必填** | 创建时间 |
| fileList.updateAt | string | **必填** | 更新时间 |
| fileList.downloadURL | string | **必填** | 下载链接 |
| fileList.userSelfURL | string | **必填** | 自定义域名链接 |
| fileList.totalTraffic | number | **必填** | 流量统计 |
| fileList.parentFileId | string | **必填** | 父级ID |
| fileList.parentFilename | string | **必填** | 父级文件名称 |
| fileList.extension | string | **必填** | 后缀名称 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/oss/file/list' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "parentFileId": "ymjew503t0m000d5qavemj7c19gu1js0DIYPAIDOBIY0DcxvDwFO",
    "limit": 100,
    "type": 1
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"parentFileId\": \"ymjew503t0m000d5qavemj7c19gu1js0DIYPAIDOBIY0DcxvDwFO\",\n    \"limit\": 100,\n    \"type\": 1\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/file/list")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/file/list",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "parentFileId": "ymjew503t0m000d5qavemj7c19gu1js0DIYPAIDOBIY0DcxvDwFO",
    "limit": 100,
    "type": 1
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
  "parentFileId": "ymjew503t0m000d5qavemj7c19gu1js0DIYPAIDOBIY0DcxvDwFO",
  "limit": 100,
  "type": 1
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/oss/file/list',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
    "parentFileId": "ymjew503t0m000d5qavemj7c19gu1js0DIYPAIDOBIY0DcxvDwFO",
    "limit": 100,
    "type": 1
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/api/v1/oss/file/list", payload, headers)
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
        "lastFileId": "-1",
        "fileList": [
            {
                "fileId": "ymjew503t0l000d7w32x751ex14jo8adDIYPAIDOBIY0DcxvDwFO",
                "filename": "测试图床目录1",
                "parentFileId": "ymjew503t0m000d5qavemj7c19gu1js0DIYPAIDOBIY0DcxvDwFO",
                "type": 1,
                "etag": "",
                "size": 0,
                "status": 0,
                "s3KeyFlag": "",
                "storageNode": "",
                "createAt": "2025-03-03 15:43:46",
                "updateAt": "2025-03-03 15:43:46",
                "downloadURL": "",
                "ossIndex": 42,
                "totalTraffic": 0,
                "parentFilename": "img_oss",
                "extension": "",
                "userSelfURL": ""
            },
            {
                "fileId": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
                "filename": "测试图床目录",
                "parentFileId": "ymjew503t0m000d5qavemj7c19gu1js0DIYPAIDOBIY0DcxvDwFO",
                "type": 1,
                "etag": "",
                "size": 0,
                "status": 0,
                "s3KeyFlag": "",
                "storageNode": "",
                "createAt": "2025-03-03 15:07:54",
                "updateAt": "2025-03-03 15:07:54",
                "downloadURL": "",
                "ossIndex": 42,
                "totalTraffic": 0,
                "parentFilename": "img_oss",
                "extension": "",
                "userSelfURL": ""
            }
        ]
    },
    "x-traceID": "5e0aa7b9-b430-41d0-bca0-647e28f47ec6_kong-db-5898fdd8c6-wnv6h"
}
```

---

### 2. 获取图片详情

**API:** GET 域名 + /api/v1/oss/file/detail

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileID | string | **必填** | 文件ID |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileId | string | **必填** | 文件ID |
| filename | string | **必填** | 文件名 |
| type | number | **必填** | 0-文件 1-文件夹 |
| size | number | **必填** | 文件大小 |
| etag | string | **必填** | md5 |
| status | number | **必填** | 文件审核状态。大于100为审核驳回文件 |
| createAt | string | **必填** | 创建时间 |
| updateAt | string | **必填** | 更新时间 |
| downloadURL | string | **必填** | 下载链接 |
| userSelfURL | string | **必填** | 自定义域名链接 |
| totalTraffic | number | **必填** | 流量统计 |
| parentFileId | string | **必填** | 父级ID |
| parentFilename | string | **必填** | 父级文件名称 |
| extension | string | **必填** | 后缀名称 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location --request GET 'https://open-api.123pan.com/api/v1/oss/file/detail?fileID=ymjew503t0m000d7w32xormjidkak3rgDIYPAIDOBIY0DcxvDwFO' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/file/detail?fileID=ymjew503t0m000d7w32xormjidkak3rgDIYPAIDOBIY0DcxvDwFO")
.method("GET", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/file/detail?fileID=ymjew503t0m000d7w32xormjidkak3rgDIYPAIDOBIY0DcxvDwFO",
  "method": "GET",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
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
  url: 'https://open-api.123pan.com/api/v1/oss/file/detail?fileID=ymjew503t0m000d7w32xormjidkak3rgDIYPAIDOBIY0DcxvDwFO',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("GET", "/api/v1/oss/file/detail?fileID=ymjew503t0m000d7w32xormjidkak3rgDIYPAIDOBIY0DcxvDwFO", payload, headers)
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
        "fileId": "ymjew503t0m000d7w32xormjidkak3rgDIYPAIDOBIY0DcxvDwFO",
        "filename": "测试图床.jpg",
        "parentFileId": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
        "type": 0,
        "etag": "e62623f4906aeba8f8d8f5de19e1e34e",
        "size": 22027358,
        "status": 2,
        "s3KeyFlag": "1817178140-0",
        "storageNode": "m76",
        "createAt": "2025-03-03 16:38:26",
        "updateAt": "2025-03-03 16:38:26",
        "downloadURL": "https://vip.123pan.cn/1815309870/ymjew503t0m000d7w32xormjidkak3rgDIYPAIDOBIY0DcxvDwFO.jpg",
        "ossIndex": 43,
        "totalTraffic": 0,
        "parentFilename": "测试图床目录",
        "extension": "jpg",
        "userSelfURL": "https://vip.123pan.cn/1815309870/ymjew503t0m000d7w32xormjidkak3rgDIYPAIDOBIY0DcxvDwFO.jpg"
    },
    "x-traceID": "fe8e8c6e-e7bd-44f2-bc83-3243e7e07ee5_kong-db-5898fdd8c6-wgsts"
}
```

---

## 上传图片

### 1. 创建目录

**API:** POST 域名 + /upload/v1/oss/file/mkdir

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| name | []string | **必填** | 目录名(注:不能重名) |
| parentID | string | **必填** | 父目录id,上传到根目录时为空 |
| type | number | **必填** | 固定为1 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| list | array | **必填** | 目录列表 |
| list.filename | string | **必填** | 目录名 |
| list.dirID | string | **必填** | 目录ID |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/upload/v1/oss/file/mkdir' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "name": "测试图床目录",
    "parentID": "",
    "type": 1
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"name\": \"测试图床目录\",\n    \"parentID\": \"\",\n    \"type\": 1\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/upload/v1/oss/file/mkdir")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v1/oss/file/mkdir",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "name": "测试图床目录",
    "parentID": "",
    "type": 1
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
  "name": "测试图床目录",
  "parentID": "",
  "type": 1
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/upload/v1/oss/file/mkdir',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
    "name": "测试图床目录",
    "parentID": "",
    "type": 1
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/upload/v1/oss/file/mkdir", payload, headers)
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
    "list": [
      {
        "filename": "测试图床目录",
        "dirID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO"
      }
    ]
  },
  "x-traceID": "e572aaa3-53f1-4c93-b36f-3f162333dbaa_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 2. 创建文件

**API:** POST 域名 + /upload/v1/oss/file/create

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| parentFileID | string | **必填** | 父目录id,上传到根目录时填写空 |
| filename | string | **必填** | 文件名要小于255个字符且不能包含以下任何字符:"\/:*?|><。(注:不能重名) |
| etag | string | **必填** | 文件md5 |
| size | number | **必填** | 文件大小,单位为byte字节 |
| type | number | **必填** | 固定为1 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileID | string | 非必填 | 文件ID。当123云盘已有该文件,则会发生秒传。此时会将文件ID字段返回。唯一 |
| preuploadID | string | **必填** | 预上传ID(如果reuse为true时,该字段不存在) |
| reuse | boolean | **必填** | 是否秒传,返回true时表示文件已上传成功 |
| sliceSize | number | **必填** | 分片大小,必须按此大小生成文件分片再上传 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/upload/v1/oss/file/create' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "parentFileID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
    "filename": "测试图床.jpg",
    "etag": "e62623f4906aeba8f8d8f5de19e1e34e",
    "size": 22032384,
    "type": 1
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"parentFileID\": \"yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO\",\n    \"filename\": \"测试图床.jpg\",\n    \"etag\": \"e62623f4906aeba8f8d8f5de19e1e34e\",\n    \"size\": 22032384,\n    \"type\": 1\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/upload/v1/oss/file/create")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v1/oss/file/create",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "parentFileID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
    "filename": "测试图床.jpg",
    "etag": "e62623f4906aeba8f8d8f5de19e1e34e",
    "size": 22032384,
    "type": 1
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
  "parentFileID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
  "filename": "测试图床.jpg",
  "etag": "e62623f4906aeba8f8d8f5de19e1e34e",
  "size": 22032384,
  "type": 1
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/upload/v1/oss/file/create',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
  "parentFileID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
  "filename": "测试图床.jpg",
  "etag": "e62623f4906aeba8f8d8f5de19e1e34e",
  "size": 22032384,
  "type": 1
})
headers = {
  'Content-Type': 'application/json',
  'Platform': 'open_platform',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/upload/v1/oss/file/create", payload, headers)
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
    "fileID": "",
    "reuse": false,
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gv...(过长省略)",
    "sliceSize": 104857600
  },
  "x-traceID": "854f0197-36a9-4367-8b46-206a377f4327_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 3. 获取上传地址&上传分片

**API:** POST 域名 + /upload/v1/oss/file/get_upload_url

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| preuploadID | string | **必填** | 预上传ID |
| sliceNo | number | **必填** | 分片序号,从1开始自增 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| presignedURL | string | **必填** | 上传地址 |

#### 示例

**获取上传地址请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/upload/v1/oss/file/get_upload_url' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvf...(过长省略)",
    "sliceNo": 1
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"preuploadID\": \"h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvf...(过长省略)\",\n    \"sliceNo\": 1\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/upload/v1/oss/file/get_upload_url")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v1/oss/file/get_upload_url",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvf...(过长省略)",
    "sliceNo": 1
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
  "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvf...(过长省略)",
  "sliceNo": 1
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/upload/v1/oss/file/get_upload_url',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvf...(过长省略)",
    "sliceNo": 1
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/upload/v1/oss/file/get_upload_url", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**获取上传地址响应示例**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "presignedURL": "https://m74.123624.com/123-846/e62623f4/1815309870-0/e62623f4906aeba8f8d8f5de19e1e34e?X-Amz-Algorithm=AWS4-HMAC-SHA256...(过长省略)",
    "isMultipart": false
  },
  "x-traceID": "b6ef3daa-f4af-407c-a8ee-4df6e9fec0ea_kong-db-5898fdd8c6-wnv6h"
}
```

**PUT上传分片请求示例**

**cURL**
```shell
curl --location --request PUT 'https://m74.123624.com/123-846/e62623f4/1815309870-0/e...(过长省略)' \
--header 'Content-Type: application/octet-stream' \
--data-binary '@/C:/Users/mfy/Downloads/测试图床.jpg'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/octet-stream");
RequestBody body = RequestBody.create(mediaType, "@/C:/Users/mfy/Downloads/测试图床.jpg");
Request request = new Request.Builder()
.url("https://m74.123624.com/123-846/e62623f4/1815309870-0/e...(过长省略)")
.method("PUT", body)
.addHeader("Content-Type", "application/octet-stream")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://m74.123624.com/123-846/e62623f4/1815309870-0/e...(过长省略)",
  "method": "PUT",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/octet-stream"
  },
  "data": "@/C:/Users/mfy/Downloads/测试图床.jpg",
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

**NodeJs - Axios**
```javascript
const axios = require('axios');
let data = '@/C:/Users/mfy/Downloads/测试图床.jpg';

let config = {
  method: 'put',
  maxBodyLength: Infinity,
  url: 'https://m74.123624.com/123-846/e62623f4/1815309870-0/e...(过长省略)',
  headers: {
    'Content-Type': 'application/octet-stream'
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

conn = http.client.HTTPSConnection("m74.123624.com")
payload = "@/C:/Users/mfy/Downloads/测试图床.jpg"
headers = {
  'Content-Type': 'application/octet-stream'
}
conn.request("PUT", "/123-846/e62623f4/1815309870-0/e...(过长省略)", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**PUT上传分片响应示例**

无响应内容,请求响应200表示分片上传成功

---

### 4. 上传完毕

**API:** POST 域名 + /upload/v1/oss/file/upload_complete

**说明:** 文件上传完成后请求

#### 建议
调用该接口前,请优先列举已上传的分片,在本地进行md5比对

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
| :---: | :---: | :---: | :---: |
| fileID | string | 非必填 | 当下方completed字段为true时,此处的fileID就为文件的真实ID(唯一) |
| async | bool | **必填** | 是否需要异步查询上传结果。false为无需异步查询,已经上传完毕。true为需要异步查询上传结果。 |
| completed | bool | **必填** | 上传是否完成 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/upload/v1/oss/file/upload_complete' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOr...(过长省略)"
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"preuploadID\": \"h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOr...(过长省略)\"\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/upload/v1/oss/file/upload_complete")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v1/oss/file/upload_complete",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOr...(过长省略)"
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
  "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOr...(过长省略)"
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/upload/v1/oss/file/upload_complete',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOr...(过长省略)"
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/upload/v1/oss/file/upload_complete", payload, headers)
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
    "async": true,
    "completed": false,
    "fileID": ""
  },
  "x-traceID": "27bde78d-228d-4c24-b616-d4ea9c361f54_kong-db-5898fdd8c6-wgsts"
}
```

---

### 5. 异步轮询获取上传结果

**API:** POST 域名 + /upload/v1/oss/file/upload_async_result

**说明:** 异步轮询获取上传结果

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
| :---: | :---: | :---: | :---: |
| completed | bool | **必填** | 上传合并是否完成,如果为false,请至少1秒后发起轮询 |
| fileID | string | **必填** | 上传成功的文件ID |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/upload/v1/oss/file/upload_async_result' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOrfsL...(过长省略)"
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"preuploadID\": \"h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOrfsL...(过长省略)\"\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/upload/v1/oss/file/upload_async_result")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v1/oss/file/upload_async_result",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOrfsL...(过长省略)"
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
  "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOrfsL...(过长省略)"
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/upload/v1/oss/file/upload_async_result',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
  "preuploadID": "h1Kiaaaaaaac/0IDD87IFbIf8T0UWrTNwNNGbGoeklBYFtnlDwBIhd9OfdMjm4abJfDPccrScqQIPdjFasHxGxV//V7bzfUbEEaEt8N6RT2PI/dC/gvyvfEykuOrfsL...(过长省略)"
})
headers = {
  'Content-Type': 'application/json',
  'Platform': 'open_platform',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/upload/v1/oss/file/upload_async_result", payload, headers)
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
    "fileID": "rehu6baz03t0l000d7freterfbyq51l4izkneDIYPAIDOBIY0DcxvDwFO"
  },
  "x-traceID": "1f8a00aa-1d95-4bfb-8908-2ccec540b06f_kong-db-5898fdd8c6-wnv6h"
}
```

---

## 复制云盘图片

### 1. 创建复制任务

**API:** POST 域名 + /api/v1/oss/source/copy

**说明:** 图床复制任务创建(可创建的任务数:3,fileIDs长度限制:100,当前一个任务处理完后将会继续处理下个任务)

该接口将会复制云盘里的文件或目录对应的图片到对应图床目录,每次任务包含的图片总数限制1000张,图片格式:png, gif, jpeg, tiff, webp,jpg,tif,svg,bmp,图片大小限制:100M,文件夹层级限制:15层

如果图床目录下存在相同etag、size的图片将会视为同一张图片,将覆盖原图片

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileIDs | array | **必填** | 文件id数组(string数组) |
| toParentFileID | string | **必填** | 要移动到的图床目标文件夹id,移动到根目录时为空 |
| sourceType | string | **必填** | 复制来源(1=云盘) |
| type | number | **必填** | 业务类型,固定为1 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| taskID | string | **必填** | 复制任务ID,可通过该ID,调用查询复制任务状态 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/oss/source/copy' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "fileIDs": [
        "14802190",
        "14802189"
    ],
    "toParentFileID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
    "sourceType": 1,
    "type": 1
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"fileIDs\": [\n        \"14802190\",\n        \"14802189\"\n    ],\n    \"toParentFileID\": \"yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO\",\n    \"sourceType\": 1,\n    \"type\": 1\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/source/copy")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/source/copy",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "fileIDs": [
      "14802190",
      "14802189"
    ],
    "toParentFileID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
    "sourceType": 1,
    "type": 1
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
  "fileIDs": [
    "14802190",
    "14802189"
  ],
  "toParentFileID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
  "sourceType": 1,
  "type": 1
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/oss/source/copy',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
    "fileIDs": [
        "14802190",
        "14802189"
    ],
    "toParentFileID": "yk6baz03t0l000d7w33fbyq51l4izkneDIYPAIDOBIY0DcxvDwFO",
    "sourceType": 1,
    "type": 1
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/api/v1/oss/source/copy", payload, headers)
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
        "taskID": "1ketmmu1000d86isuyq33su100w1bnp6"
    },
    "x-traceID": "37e67458-c3b3-462b-82b5-71a43d9848a7_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 2. 获取复制任务详情

**API:** GET 域名 + /api/v1/oss/source/copy/process

**说明:** 该接口将会获取图床复制任务执行情况

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| taskID | string | **必填** | 复制任务ID |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| status | int | **必填** | 任务状态: 1进行中,2结束,3失败,4等待 |
| failMsg | string | **必填** | 失败原因 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/oss/source/copy/process?taskID=1ketmmu1000d86isuyq33su100w1bnp6' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/source/copy/process?taskID=1ketmmu1000d86isuyq33su100w1bnp6")
.method("GET", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/source/copy/process?taskID=1ketmmu1000d86isuyq33su100w1bnp6",
  "method": "GET",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
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
  url: 'https://open-api.123pan.com/api/v1/oss/source/copy/process?taskID=1ketmmu1000d86isuyq33su100w1bnp6',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("GET", "/api/v1/oss/source/copy/process?taskID=1ketmmu1000d86isuyq33su100w1bnp6", payload, headers)
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
        "status": 2,
        "failMsg": ""
    },
    "x-traceID": "9c4eea65-23ca-4f37-b305-89a6d7bb1f5a_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 3. 获取复制失败文件列表

**API:** GET 域名 + /api/v1/oss/source/copy/fail

**说明:** 查询图床复制任务失败文件列表(注:记录的是符合对应格式、大小的图片的复制失败原因)

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| taskID | string | **必填** | 复制任务ID |
| limit | number | **必填** | 每页文件数量,最大不超过100 |
| page | number | **必填** | 页码数 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| total | number | **必填** | 总数 |
| list | array | **必填** | 失败文件列表 |
| list.fileId | number | **必填** | 文件Id |
| list.filename | string | **必填** | 文件名 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location --request GET 'https://open-api.123pan.com/api/v1/oss/source/copy/fail?taskID=1ketmmu1000d86isuyq33su100w1bnp6&limit=100&page=1' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/source/copy/fail?taskID=1ketmmu1000d86isuyq33su100w1bnp6&limit=100&page=1")
.method("GET", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/source/copy/fail?taskID=1ketmmu1000d86isuyq33su100w1bnp6&limit=100&page=1",
  "method": "GET",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
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
  url: 'https://open-api.123pan.com/api/v1/oss/source/copy/fail?taskID=1ketmmu1000d86isuyq33su100w1bnp6&limit=100&page=1',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("GET", "/api/v1/oss/source/copy/fail?taskID=1ketmmu1000d86isuyq33su100w1bnp6&limit=100&page=1", payload, headers)
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
        "total": 0,
        "list": null
    },
    "x-traceID": "61f58d82-056c-496c-abf8-c52adb2a52a9_kong-db-5898fdd8c6-wnv6h"
}
```

---

## 图床离线迁移

### 1. 创建离线迁移任务

**API:** POST 域名 + /api/v1/oss/offline/download

**说明:**

1. 离线下载任务仅支持http/https任务创建,提交url资源后将在后台自动下载图片资源并上传到对应图床目录
2. url支持的图片格式:png, gif, jpeg, tiff, webp,jpg,tif,svg,bmp,图片大小限制:100M
3. 如果图床目录下存在相同etag、size的图片将会覆盖原图片

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| url | string | **必填** | 下载资源地址(http/https) |
| fileName | string | 非必填 | 自定义文件名称(需携带图片格式,支持格式:png, gif, jpeg, tiff, webp,jpg,tif,svg,bmp) |
| businessDirID | string | 非必填 | 选择下载到指定目录ID。示例:10023。注:不支持下载到根目录,默认下载到名为"来自:离线下载"的目录中 |
| callBackUrl | string | 非必填 | 回调地址,当文件下载成功或者失败,均会通过回调地址通知。回调内容如下:url: 下载资源地址,status: 0 成功,1 失败,fileReason:失败原因,fileID:成功后,该文件在云盘上的ID。请求类型:POST {"url": "http://dc.com/resource.jpg","status": 0,"failReason": "","fileID":100} |
| type | number | **必填** | 业务类型,固定为1 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| taskID | number | **必填** | 离线下载任务ID,可通过该ID,调用查询任务进度接口获取下载进度 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/oss/offline/download' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "url": "https://vip.123pan.cn/1815309870/%E6%B5%8B%E8%AF%95%E7%9B%B4%E9%93%BE%E6%96%87%E4%BB%B6%E5%A4%B9/6ac54ccb31a09a5c1223677ba07c283f.jpeg",
    "type": 1
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"url\": \"https://vip.123pan.cn/1815309870/%E6%B5%8B%E8%AF%95%E7%9B%B4%E9%93%BE%E6%96%87%E4%BB%B6%E5%A4%B9/6ac54ccb31a09a5c1223677ba07c283f.jpeg\",\n    \"type\": 1\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/offline/download")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/offline/download",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "url": "https://vip.123pan.cn/1815309870/%E6%B5%8B%E8%AF%95%E7%9B%B4%E9%93%BE%E6%96%87%E4%BB%B6%E5%A4%B9/6ac54ccb31a09a5c1223677ba07c283f.jpeg",
    "type": 1
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
  "url": "https://vip.123pan.cn/1815309870/%E6%B5%8B%E8%AF%95%E7%9B%B4%E9%93%BE%E6%96%87%E4%BB%B6%E5%A4%B9/6ac54ccb31a09a5c1223677ba07c283f.jpeg",
  "type": 1
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/oss/offline/download',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
  "url": "https://vip.123pan.cn/1815309870/%E6%B5%8B%E8%AF%95%E7%9B%B4%E9%93%BE%E6%96%87%E4%BB%B6%E5%A4%B9/6ac54ccb31a09a5c1223677ba07c283f.jpeg",
  "type": 1
})
headers = {
  'Content-Type': 'application/json',
  'Platform': 'open_platform',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/api/v1/oss/offline/download", payload, headers)
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
        "taskID": 403316
    },
    "x-traceID": "f65dfd51-ad28-47e6-ad21-10da7f46d98a_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 2. 获取离线迁移任务

**API:** GET 域名 + /api/v1/oss/offline/download/process

**说明:** 获取当前离线下载任务状态

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | **必填** | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| taskID | number | **必填** | 离线下载任务ID |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| status | int | **必填** | 下载状态: 0进行中、1下载失败、2下载成功、3重试中 |
| process | int | **必填** | 离线进度百分比0-100 |

#### 示例

**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/oss/offline/download/process?taskID=403316' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/oss/offline/download/process?taskID=403316")
.method("GET", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/oss/offline/download/process?taskID=403316",
  "method": "GET",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
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
  url: 'https://open-api.123pan.com/api/v1/oss/offline/download/process?taskID=403316',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
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
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("GET", "/api/v1/oss/offline/download/process?taskID=403316", payload, headers)
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
    "process": 100,
    "status": 2
  },
  "x-traceID": "1895c15e-dc5b-4f75-a01b-b7113bd176ca_kong-db-5898fdd8c6-t5pvc"
}
```

---

> 更新日期: 2025-10-01
> 基于: 123云盘开放平台官方文档 v1
> 原文: https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/
