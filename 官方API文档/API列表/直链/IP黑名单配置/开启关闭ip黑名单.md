# 开启关闭ip黑名单

**API：** POST 域名 + /api/v1/developer/config/forbide-ip/switch  
**注：** 此接口需要开通开发者权益

### Header 参数
| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| Authorization | string | 必填 | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |
| Content-Type | string | 必填 | application/json |


### Body 参数
| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| Status | number | 必填 | 状态：2禁用 1启用 |


### 返回数据
| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| Done | boolean | 必填 | 操作是否完成 |


### 示例
**请求示例**

```bash
curl --request POST \
  --url https://open-api.123pan.com/api/v1/developer/config/forbide-ip/switch \
  --header 'Accept: */*' \
  --header 'Accept-Encoding: gzip, deflate, br' \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略' \
  --header 'Connection: keep-alive' \
  --header 'Content-Type: application/json' \
  --header 'Platform: open_platform' \
  --header 'User-Agent: PostmanRuntime-ApipostRuntime/1.1.0' \
  --data '{
    "Status": 1
}'
```

```java
OkHttpClient client = new OkHttpClient();

MediaType mediaType = MediaType.parse("text/plain");
RequestBody body = RequestBody.create(mediaType, "{\n    \"Status\": 1\n}");
Request request = new Request.Builder()
  .url("https://open-api.123pan.com/api/v1/developer/config/forbide-ip/switch")
  .post(body)
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略")
  .addHeader("Platform", "open_platform")
  .addHeader("Content-Type", "application/json")
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
  "url": "https://open-api.123pan.com/api/v1/developer/config/forbide-ip/switch",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略",
    "Platform": "open_platform",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "PostmanRuntime-ApipostRuntime/1.1.0",
    "Connection": "keep-alive"
  },
  "data": "{\n    \"Status\": 1\n}"
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

```javascript
import axios from "axios";

const options = {
  method: 'POST',
  url: 'https://open-api.123pan.com/api/v1/developer/config/forbide-ip/switch',
  headers: {
    Authorization: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略',
    Platform: 'open_platform',
    'Content-Type': 'application/json',
    Accept: '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'PostmanRuntime-ApipostRuntime/1.1.0',
    Connection: 'keep-alive'
  },
  data: '{\n    "Status": 1\n}'
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

payload = "{\n    \"Status\": 1\n}"

headers = {
    'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...过长省略",
    'Platform': "open_platform",
    'Content-Type': "application/json",
    'Accept': "*/*",
    'Accept-Encoding': "gzip, deflate, br",
    'User-Agent': "PostmanRuntime-ApipostRuntime/1.1.0",
    'Connection': "keep-alive"
    }

conn.request("POST", "/api/v1/developer/config/forbide-ip/switch", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```



**Body示例：**

**HTTP状态码： 200 OK**

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



> 更新: 2025-06-28 10:50:32  
> 原文: <https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/xwx77dbzrkxquuxm>