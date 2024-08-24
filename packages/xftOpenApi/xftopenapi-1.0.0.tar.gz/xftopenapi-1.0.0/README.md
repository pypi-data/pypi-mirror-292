# xftOpenApi

用于调用薪福通API接口

# 安装

```cmd
pip install xftOpenApi
```

需要用到的依赖库：gmssl

```cmd
pip install gmssl -i https://pypi.tuna.tsinghua.edu.cn/simple
```

# 用法

```python
from xftOpenApi import XFT

# 查询组织结构
api = "/ORG/orgqry/xft-service-organization/org/v1/get/page"
querystr = {
    "codes": [
        "0000"
    ]
}
# 添加配置信息
config = {
    "appid": "",
    "privateKey": "",
    "publicKey": "",
    "host": "https://api.cmbchina.com",
    "CSCPRJCOD": "",
}

xft = XFT(**config)
orgqry = xft.post(api, querystr)
print(orgqry)
```

**配置项 config 说明：**

| 参数名称       | 参数说明            | 是否必填 | 备注说明                                                                                             |
|------------|-----------------|------|--------------------------------------------------------------------------------------------------|
| appid      | 应用程序的唯一标识符。     | 是    | 自定义应用的凭证                                                                                         |
| privateKey | 应用程序的私钥，用于签名验证。 | 是    | 自定义应用的私钥                                                                                         |
| publicKey  | 应用程序的公钥，用于加密通信。 | 是    | 需要找招行薪福通技术支持人员申请                                                                                 |
| host       | 薪福通API服务器的地址。   | 是    | 沙盒环境地址：https://api.cmburl.cn:8065 ；生产环境地址：https://api.cmbchina.com                               |
| CSCPRJCOD  | 企业号             | 否    | 登录开放平台，点击右上角登录用户名称，可以查看到企业ID；如果不传，接口处理时默认取CSCAPPUID应用所属企业                                        |
| CSCUSRNBR  | 薪福通企业用户号        | 否    | 在企业内唯一编号。如果是网页应用，建议从用户登录信息中取出；如果API不是用户操作行为(如定时拉取或推送等)允许为空，但部分接口可能会使用该字段，请在联调时注意，可输入A0001        |
| CSCUSRUID  | 薪福通平台用户号        | 否    | 在薪福通内用户的唯一编号。如果是网页应用，建议从用户登录信息中取出；如果API不是用户操作行为(如定时拉取或推送等)允许为空，但部分接口可能会使用该字段，请在联调时注意，可输入AUTO0001 |

**注意：**
在调用API之前，需要先登录开放平台，申请应用，获取appid、privateKey、publicKey等信息。
![img.png](images/img.png)
<font color="red">注意：沙盒环境的企业号与生产环境不同，请注意在不同环境中使用对应的企业号，以防调用失败。</font>
![img_1.png](images/img_1.png)


