# 单个转码文件下载（m3u8或ts）

API： POST 域名 + /api/v1/transcode/m3u8_ts/download

**<font style="color:#DF2A3F;">注意：这里只是返回下载地址，获取到下载地址之后，把地址放在浏览器中即可进行下载</font>**

## Header 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | :---: |
| Authorization | string | <font style="color:#000000;">必填</font> | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |


## Body 参数
| **名称** | **类型** | **是否必填** | **说明** |
| :---: | :---: | :---: | --- |
| fileId | number | 必填 | 文件Id |
| resolution | string | 必填 | 分辨率 |
| type | number | 必填 | 1代表下载m3u8文件<br/>2代表下载ts文件 |
| tsName | string | 选填 | 下载ts文件时必须要指定ts文件的名称<font style="color:#000000;">，ts的名称参考查询某个视频的转码结果</font> |


### body参数示例
#### 下载m3u8文件所需参数
```json
{
    "fileId": 2875008,
    "resolution": "1080P",
    "type": 1
}
```

#### 下载ts文件所需参数
```json
{
    "fileId": 2875008,
    "resolution": "1080P",
    "type": 2,
    "tsName": "001"
}
```

## 返回数据
| **名称** | | **类型** | **是否必填** | **说明** |
| :---: | --- | :---: | :---: | --- |
|  downloadUrl | | string | 必填 | 下载地址，如果转码空间满了，则返回空 |
| isFull | | boolean | 必填 | 转码空间容量是否满了，如果满了，则不会返回下载地址，需要用户购买转码空间之后才能下载 |


### **返回示例**
#### 转码空间满了
```json
{
    "code": 0,
    "message": "ok",
    "data": {
        "downloadUrl": "",
        "isFull": true
    },
    "x-traceID": ""
}
```

#### m3u8文件下载地址
```json
{
    "code": 0,
    "message": "ok",
    "data": {
        "downloadUrl": "https://download-v.cjjd09.com/m88/123-hls-428/hls/a69bef24085bde8d8616d798475b9191_15955377/1080p/stream.m3u8?auth_key=1734674672-3837305-0-c93ec29a48528cad9e7a72a73ea3c0a9&bzc=666&bzs=1814435971&s=1703748374",
        "isFull": false
    },
    "x-traceID": ""
}
```

#### ts文件下载地址
```json
{
    "code": 0,
    "message": "ok",
    "data": {
        "downloadUrl": "https://download-v.cjjd09.com/m88/123-hls-428/hls/a69bef24085bde8d8616d798475b9191_15955377/1080p/001.ts?auth_key=1734674771-11399-0-64791fd3d5b3b8aa5de0e4e91bb058df&bzc=666&bzs=1814435971&s=1703748374",
        "isFull": false
    },
    "x-traceID": ""
}
```



> 更新: 2025-03-17 19:16:45  
> 原文: <https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced/yf97p60yyzb8mzbr>