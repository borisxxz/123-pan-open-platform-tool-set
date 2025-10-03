# 授权code获取access_token

API： POST   域名 + /api/v1/oauth2/access_token

## QueryString 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| client_id | string | 是 | 应用标识，创建应用时分配的 appId |
| client_secret | string | 是 | 应用密钥，创建应用时分配的 secretId |
| grant_type | string | 是 | 身份类型 authorization_code 或 refresh_token |
| code | string | 否 | 授权码 |
| refresh_token | string | 否 | 刷新 token，单次请求有效 |
| redirect_uri | string | 否 | authorization_code时必携带，应用注册的回调地址 |


## 返回数据
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| token_type | string | 是 | Bearer |
| access_token | string | 是 | 用来获取用户信息的 access_token。 刷新后，旧 access_token 立即失效 |
| refresh_token | string | 是 | 单次有效，用来刷新 access_token，90 天有效期。刷新后，返回新的 refresh_token，请保存以便下一次刷新使用。 |
| expires_in | number | 是 | access_token的过期时间，单位秒。 |
| scope | string | 是 | 权限 |


## 示例
**请求示例**

```shell
https://open-api.123pan.com/api/v1/oauth2/access_token?client_id=1cc3f37c84994218b0489226b988128b&client_secret=xxxxx&code=NGE0ZGMWZWITYZRMNY0ZZGNILTKWMJCTOTHHNJM1MMM4MJFH&grant_type=authorization_code&redirect_uri=http://www.baidu.com
```

**响应示例**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCIs...(过长省略)",
  "expires_in": 7200,
  "refresh_token": "ZMY5MTKWNDCTNWZHOS01OWMYLTGYMMUTNZY5YTHIMGRHMJZL",
  "scope": "user:base,file:all:read,file:all:write",
  "token_type": "Bearer"
}
```



> 更新: 2025-03-17 19:17:15  
> 原文: <https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/gammzlhe6k4qtwd9>