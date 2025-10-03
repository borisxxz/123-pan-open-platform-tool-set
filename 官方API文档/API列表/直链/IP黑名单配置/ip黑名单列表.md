# ip黑名单列表

获取开发者功能IP配置黑名单

**API：** GET 域名 + /api/v1/developer/config/forbide-ip/list  
**注：** 获取用户配置的黑名单

### Header 参数
| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| Authorization | string | 必填 | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |


### 返回数据
| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| ipList | array | 必填 | IP地址列表 |
| status | number | 必填 | 状态：2禁用 1启用 |


### 示例
**请求示例**

```bash
curl --request GET \
  --url https://open-api.123pan.com/api/v1/developer/config/forbide-ip/list \
  --header 'Accept: */*' \
  --header 'Accept-Encoding: gzip, deflate, br' \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略' \
  --header 'Connection: keep-alive' \
  --header 'Platform: open_platform' \
  --header 'User-Agent: PostmanRuntime-ApipostRuntime/1.1.0'
```

```java
OkHttpClient client = new OkHttpClient();

Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/developer/config/forbide-ip/list")
.get()
.addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略")
.addHeader("Platform", "open_platform")
.addHeader("Accept", "*/*")
.addHeader("Accept-Encoding", "gzip, deflate, br")
.addHeader("User-Agent", "PostmanRuntime-ApipostRuntime/1.1.0")
.addHeader("Connection", "keep-alive")
.build();

Response response = client.newCall(request).execute();
```

```javascript
const settings = {
  "async": true,
  "crossDomain": true,
  "url": "https://open-api.123pan.com/api/v1/developer/config/forbide-ip/list",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略",
    "Platform": "open_platform",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "PostmanRuntime-ApipostRuntime/1.1.0",
    "Connection": "keep-alive"
  }
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

```javascript
import axios from "axios";

const options = {
  method: 'GET',
  url: 'https://open-api.123pan.com/api/v1/developer/config/forbide-ip/list',
  headers: {
    Authorization: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略',
    Platform: 'open_platform',
    Accept: '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'PostmanRuntime-ApipostRuntime/1.1.0',
    Connection: 'keep-alive'
  }
};

axios.request(options).then(function (response) {
  console.log(response.data);
}).catch(function (error) {
  console.error(error);
});
```

```python
import http.client

conn = http.client.HTTPSConnection("open-api.123pan.com")

payload = ""

headers = {
    'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略",
    'Platform': "open_platform",
    'Accept': "*/*",
    'Accept-Encoding': "gzip, deflate, br",
    'User-Agent': "PostmanRuntime-ApipostRuntime/1.1.0",
    'Connection': "keep-alive"
    }

conn.request("GET", "/api/v1/developer/config/forbide-ip/list", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```



**<font style="color:rgb(64, 64, 64);">HTTP状态码：</font>**<font style="color:rgb(64, 64, 64);"> </font>`<font style="color:rgb(64, 64, 64);">200 OK</font>`

**<font style="color:rgb(64, 64, 64);">Body示例：</font>**

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



> 更新: 2025-06-28 10:51:22  
> 原文: <https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/mxldrm9d5gpw5h2d>