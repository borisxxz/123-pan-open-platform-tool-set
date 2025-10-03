# 获取access_token

API： POST 域名 +/api/v1/access_token

> 注：此接口有访问频率限制。请获取到access_token后本地保存使用，并在access_token过期前及时重新获取。access_token有效期根据返回的expiredAt字段判断。
>

## Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
|  Platform | string | <font style="color:#000000;">是</font> |  open_platform  |


## Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| clientID | string | 必填 |  |
| clientSecret | string | 必填 |  |


## 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| accessToken | string | 必填 | 访问凭证 |
| expiredAt | string | 必填 | access_token过期时间 |


## 示例
**<font style="color:rgb(51, 51, 51);">请求示例</font>**

```shell
curl --location 'https://open-api.123pan.com/api/v1/access_token' \
--header 'Platform: open_platform' \
--header 'Content-Type: application/json' \
--data '{
	"clientID": "123456789",
	"clientSecret": "123456789"
}'
```

```java
OkHttpClient client = new OkHttpClient().newBuilder()
.build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n\t\"clientID\": \"123456789\",\n\t\"clientSecret\": \"123456789\"\n}");
Request request = new Request.Builder()
.url("https://open-api.123pan.com/api/v1/access_token")
.method("POST", body)
.addHeader("Platform", "open_platform")
.addHeader("Content-Type", "application/json")
.build();
Response response = client.newCall(request).execute();
```

```javascript
var settings = {
  "url": "https://open-api.123pan.com/api/v1/access_token",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Platform": "open_platform",
    "Content-Type": "application/json"
  },
  "data": JSON.stringify({
    "clientID": "123456789",
    "clientSecret": "123456789"
  }),
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

```javascript
const axios = require('axios');
let data = JSON.stringify({
  "clientID": "123456789",
  "clientSecret": "123456789"
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/api/v1/access_token',
  headers: { 
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

```python
import http.client
import json

conn = http.client.HTTPSConnection("open-api.123pan.com")
payload = json.dumps({
    "clientID": "123456789",
    "clientSecret": "123456789"
})
headers = {
    'Platform': 'open_platform',
    'Content-Type': 'application/json'
}
conn.request("POST", "/api/v1/access_token", payload, headers)
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
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyxxxxx...(过长已省略)",
    "expiredAt": "2025-03-23T15:48:37+08:00"
  },
  "x-traceID": "16f60c4d-f022-42d3-b3df-85d1fe2a3ac5_kong-db-5898fdd8c6-wgsts"
}
```



> 更新: 2025-06-17 09:37:58  
> 原文: <https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/gn1nai4x0v0ry9ki>