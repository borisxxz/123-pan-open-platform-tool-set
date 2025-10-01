# 直链 API 文档

## 目录
- [基础直链操作](#基础直链操作)
  - [1. 获取直链链接](#1-获取直链链接)
  - [2. 启用直链空间](#2-启用直链空间)
  - [3. 禁用直链空间](#3-禁用直链空间)
  - [4. 直链缓存刷新](#4-直链缓存刷新)
- [日志管理](#日志管理)
  - [1. 获取直链流量日志](#1-获取直链流量日志)
  - [2. 获取直链离线日志](#2-获取直链离线日志)
- [IP黑名单配置](#ip黑名单配置)
  - [1. IP黑名单列表](#1-ip黑名单列表)
  - [2. 更新IP黑名单列表](#2-更新ip黑名单列表)
  - [3. 开启关闭IP黑名单](#3-开启关闭ip黑名单)

---

## 基础直链操作

### 1. 获取直链链接

**API：** GET 域名 + /api/v1/direct-link/url

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileID | number | **必填** | 需要获取直链链接的文件的fileID |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| url | string | 必填 | 文件对应的直链链接 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/direct-link/url?fileID=10861131' \
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
.url("https://open-api.123pan.com/api/v1/direct-link/url?fileID=10861131")
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
  "url": "https://open-api.123pan.com/api/v1/direct-link/url?fileID=10861131",
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
  url: 'https://open-api.123pan.com/api/v1/direct-link/url?fileID=10861131',
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
conn.request("GET", "/api/v1/direct-link/url?fileID=10861131", payload, headers)
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
    "url": "https://vip.123pan.cn/1815309870/%E6%B5%8B%E8%AF%95%E7%9B%B4%E9%93%BE%E6%96%87%E4%BB%B6%E5%A4%B9/%E6%88%91%E4%BB%8E%E8%8D%89%E5%8E%9F%E6%9D%A5.mp4"
  },
  "x-traceID": "126fa997-fdae-4cd6-b79f-42e134e17f1d_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 2. 启用直链空间

**API：** POST 域名 + /api/v1/direct-link/enable

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileID | number | **必填** | 启用直链空间的文件夹的fileID |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| filename | string | 必填 | 成功启用直链空间的文件夹的名称 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/direct-link/enable' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...' \
--data '{
    "fileID": 4404009
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"fileID\": 4404009\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/direct-link/enable")
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
  "url": "https://open-api.123pan.com/api/v1/direct-link/enable",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl..."
  },
  "data": JSON.stringify({
    "fileID": 4404009
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
  "fileID": 4404009
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/direct-link/enable',
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
    "fileID": 4404009
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...'
}
conn.request("POST", "/api/v1/direct-link/enable", payload, headers)
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
    "filename": "测试直链目录"
  },
  "x-traceID": "28efdd5c-a663-43c8-a8b7-7a5aecaca0fc_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 3. 禁用直链空间

**API：** POST 域名 + /api/v1/direct-link/disable

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| fileID | number | **必填** | 禁用直链空间的文件夹的fileID |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| filename | string | 必填 | 成功禁用直链空间的文件夹的名称 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/direct-link/disable' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...' \
--data '{
    "fileID": 4404009
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"fileID\": 4404009\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/direct-link/disable")
.method("POST", body)
.addHeader("Content-Type", "application/json")
.addHeader("Platform", "open_platform")
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...")
.build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/direct-link/disable",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ..."
  },
  "data": JSON.stringify({
    "fileID": 4404009
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
  "fileID": 4404009
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/direct-link/disable',
  headers: {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...'
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
  "fileID": 4404009
})
headers = {
  'Content-Type': 'application/json',
  'Platform': 'open_platform',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...'
}
conn.request("POST", "/api/v1/direct-link/disable", payload, headers)
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
    "filename": "测试禁用直链目录"
  },
  "x-traceID": "86f8f6f1-636b-441d-8aca-560ef58771da_kong-db-5898fdd8c6-t5pvc"
}
```

---

### 4. 直链缓存刷新

**API：** POST 域名 + /api/v1/direct-link/cache/refresh

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### Body 参数
此接口无需请求参数

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| code | number | 必填 | 响应码 |
| message | string | 必填 | 响应信息 |
| data | object | 必填 | 响应数据 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location --request POST 'https://open-api.123pan.com/api/v1/direct-link/cache/refresh' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...' \
--header 'Platform: open_platform' \
--header 'Content-Type: application/json'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{}");
Request request = new Request.Builder()
  .url("https://open-api.123pan.com/api/v1/direct-link/cache/refresh")
  .method("POST", body)
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...")
  .addHeader("Platform", "open_platform")
  .addHeader("Content-Type", "application/json")
  .build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/direct-link/cache/refresh",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...",
    "Platform": "open_platform",
    "Content-Type": "application/json"
  },
  "data": JSON.stringify({})
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

**NodeJs - Axios**
```javascript
const axios = require('axios');

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/direct-link/cache/refresh',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...',
    'Platform': 'open_platform',
    'Content-Type': 'application/json'
  },
  data: JSON.stringify({})
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
payload = json.dumps({})
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...',
  'Platform': 'open_platform',
  'Content-Type': 'application/json'
}
conn.request("POST", "/api/v1/direct-link/cache/refresh", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**响应示例**

```json
{
    "code": 0,
    "message": "ok",
    "data": {},
    "x-traceID": ""
}
```

---

## 日志管理

### 1. 获取直链流量日志

**API：** GET 域名 + /api/v1/direct-link/log

> 说明：此接口需要开通开发者权益，并且仅限查询近三天的日志数据

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| pageNum | number | **必填** | 页数 |
| pageSize | number | **必填** | 分页大小 |
| startTime | string | **必填** | 开始时间，格式：2025-01-01 00:00:00 |
| endTime | string | **必填** | 结束时间，格式：2025-01-01 23:59:59 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| total | number | 必填 | 总数 |
| list | array | 必填 |  |
| uniqueID | string | 必填 | 唯一id |
| fileName | string | 必填 | 文件名 |
| fileSize | number | 必填 | 文件大小（字节） |
| filePath | string | 必填 | 文件路径 |
| directLinkURL | string | 必填 | 直链URL |
| fileSource | number | 必填 | 文件来源 1全部文件 2图床 |
| totalTraffic | number | 必填 | 消耗流量（字节） |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/direct-link/log?pageNum=1&pageSize=100&startTime=2025-03-04%2000%3A00%3A00&endTime=2025-03-05%2023%3A59%3A59' \
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
.url("https://open-api.123pan.com/api/v1/direct-link/log?pageNum=1&pageSize=100&startTime=2025-03-04%2000%3A00%3A00&endTime=2025-03-05%2023%3A59%3A59")
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
  "url": "https://open-api.123pan.com/api/v1/direct-link/log?pageNum=1&pageSize=100&startTime=2025-03-04%2000%3A00%3A00&endTime=2025-03-05%2023%3A59%3A59",
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
  url: 'https://open-api.123pan.com/api/v1/direct-link/log?pageNum=1&pageSize=100&startTime=2025-03-04%2000%3A00%3A00&endTime=2025-03-05%2023%3A59%3A59',
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
conn.request("GET", "/api/v1/direct-link/log?pageNum=1&pageSize=100&startTime=2025-03-04%2000%3A00%3A00&endTime=2025-03-05%2023%3A59%3A59", payload, headers)
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
        "uniqueID": "b23ce3be-2e06-4421-8c74-5b69bac99d69",
        "fileName": "Planet.Earth.III.S01E06.Extremes.2160p.iP.WEB-DL.AAC2.0.HLG.H.265-Q66.mkv",
        "fileSize": 2595421554,
        "filePath": "/测试图片/Planet.Earth.III.S01E06.Extremes.2160p.iP.WEB-DL.AAC2.0.HLG.H.265-Q66.mkv",
        "directLinkURL": "http://vipdev.123pan.com/1814435789/测试图片/Planet.Earth.III.S01E06.Extremes.2160p.iP.WEB-DL.AAC2.0.HLG.H.265-Q66.mkv",
        "fileSource": 1,
        "totalTraffic": 2859077463
      },
      {
        "uniqueID": "94bf5252-7d66-4d97-98e9-5b358eef7560",
        "fileName": "video.mp4",
        "fileSize": 729699,
        "filePath": "/测试图片/video.mp4",
        "directLinkURL": "http://vipdev.123pan.com/1814435789/测试图片/video.mp4",
        "fileSource": 1,
        "totalTraffic": 2971802
      }
    ],
    "total": 2
  },
  "x-traceID": ""
}
```

---

### 2. 获取直链离线日志

**API：** GET 域名 + /api/v1/direct-link/offline/logs

> 说明：此接口需要开通开发者权益，并且仅限查询近30天的日志数据

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| startHour | string | **必填** | 开始时间，格式：2025010115 |
| endHour | string | **必填** | 结束时间，格式：2025010116 |
| pageNum | number | **必填** | 页数，从1开始 |
| pageSize | number | **必填** | 分页大小 |

#### 返回数据
| **名称** | | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: | :---: |
| total | | number | 必填 | 总数 |
| list | | array | 必填 |  |
|  | id | string | 必填 | 唯一id |
|  | fileName | string | 必填 | 文件名 |
|  | fileSize | number | 必填 | 文件大小（字节） |
|  | logTimeRange | string | 必填 | 日志时间范围 |
|  | downloadURL | string | 必填 | 下载地址 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location --request GET 'https://open-api.123pan.com/api/v1/direct-link/offline/logs' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...' \
--header 'Platform: open_platform' \
--header 'Content-Type: application/json' \
--data '{
    "startHour": "2025062001",
    "endHour": "2025062023",
    "pageNum": 1,
    "pageSize": 5
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\r\n    \"startHour\": \"2025062001\",\r\n    \"endHour\": \"2025062023\",\r\n    \"pageNum\": 1,\r\n    \"pageSize\": 5\r\n}");
Request request = new Request.Builder()
  .url("https://open-api.123pan.com/api/v1/direct-link/offline/logs")
  .method("GET", body)
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...")
  .addHeader("Platform", "open_platform")
  .addHeader("Content-Type", "application/json")
  .build();
Response response = client.newCall(request).execute();
```

**JavaScript - jQuery**
```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/direct-link/offline/logs",
  "method": "GET",
  "timeout": 0,
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...",
    "Platform": "open_platform",
    "Content-Type": "application/json"
  },
  "data": JSON.stringify({
    "startHour": "2025062001",
    "endHour": "2025062023",
    "pageNum": 1,
    "pageSize": 5
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
  "startHour": "2025062001",
  "endHour": "2025062023",
  "pageNum": 1,
  "pageSize": 5
});

let config = {
  method: 'get',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/direct-link/offline/logs',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...',
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
  "startHour": "2025062001",
  "endHour": "2025062023",
  "pageNum": 1,
  "pageSize": 5
})
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...',
  'Platform': 'open_platform',
  'Content-Type': 'application/json'
}
conn.request("GET", "/api/v1/direct-link/offline/logs", payload, headers)
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
                "id": 12,
                "fileName": "202506201516.gz",
                "fileSize": 317,
                "logTimeRange": "2025-06-20 15:00~16:00",
                "downloadURL": "https://m88.cjjd20.com/123-direct-link-logs/2025...(过长省略)"
            },
            {
                "id": 11,
                "fileName": "202506201516.gz",
                "fileSize": 195,
                "logTimeRange": "2025-06-20 15:00~16:00",
                "downloadURL": "https://m88.cjjd20.com/123-direct-link-logs/2025...(过长省略)"
            }
        ],
        "total": 0
    },
    "x-traceID": ""
}
```

---

## IP黑名单配置

### 1. IP黑名单列表

**API：** GET 域名 + /api/v1/developer/config/forbide-ip/list

> 说明：获取用户配置的黑名单

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| ipList | array | 必填 | IP地址列表 |
| status | number | 必填 | 状态：2禁用 1启用 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/developer/config/forbide-ip/list' \
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
.url("https://open-api.123pan.com/api/v1/developer/config/forbide-ip/list")
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
  "url": "https://open-api.123pan.com/api/v1/developer/config/forbide-ip/list",
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
  url: 'https://open-api.123pan.com/api/v1/developer/config/forbide-ip/list',
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
conn.request("GET", "/api/v1/developer/config/forbide-ip/list", payload, headers)
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
        "ipList": ["192.168.1.1", "10.0.0.1"],
        "status": 1
    },
    "x-traceID": ""
}
```

---

### 2. 更新IP黑名单列表

**API：** POST 域名 + /api/v1/developer/config/forbide-ip/update

> 说明：此接口需要开通开发者权益

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |
| Content-Type | string | 必填 | application/json |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| IpList | array | **必填** | IP地址列表，最多2000个IPv4地址 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| - | - | - | 操作成功无特定返回数据 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/developer/config/forbide-ip/update' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...' \
--data '{
    "IpList": ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"IpList\": [\"192.168.1.1\", \"10.0.0.1\", \"172.16.0.1\"]\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/developer/config/forbide-ip/update")
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
  "url": "https://open-api.123pan.com/api/v1/developer/config/forbide-ip/update",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl..."
  },
  "data": JSON.stringify({
    "IpList": ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
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
  "IpList": ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/developer/config/forbide-ip/update',
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
    "IpList": ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...'
}
conn.request("POST", "/api/v1/developer/config/forbide-ip/update", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**响应示例**

```json
{
    "code": 0,
    "message": "ok",
    "data": {},
    "x-traceID": ""
}
```

---

### 3. 开启关闭IP黑名单

**API：** POST 域名 + /api/v1/developer/config/forbide-ip/switch

> 说明：此接口需要开通开发者权益

#### Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | **必填** | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |
| Content-Type | string | 必填 | application/json |

#### Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Status | number | **必填** | 状态：2禁用 1启用 |

#### 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Done | boolean | 必填 | 操作是否完成 |

#### 示例
**请求示例**

**cURL**
```shell
curl --location 'https://open-api.123pan.com/api/v1/developer/config/forbide-ip/switch' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...' \
--data '{
    "Status": 1
}'
```

**Java**
```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"Status\": 1\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/developer/config/forbide-ip/switch")
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
  "url": "https://open-api.123pan.com/api/v1/developer/config/forbide-ip/switch",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl..."
  },
  "data": JSON.stringify({
    "Status": 1
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
  "Status": 1
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/developer/config/forbide-ip/switch',
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
    "Status": 1
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...'
}
conn.request("POST", "/api/v1/developer/config/forbide-ip/switch", payload, headers)
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
        "Done": true
    },
    "x-traceID": ""
}
```

---

> 更新日期: 2025-10-01
> 基于: 123云盘开放平台官方文档 v1
> 原文: https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/
