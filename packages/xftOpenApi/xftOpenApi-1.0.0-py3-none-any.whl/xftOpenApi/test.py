from xftOpenApi import XFT

# 查询组织结构
api = "/ORG/orgqry/xft-service-organization/org/v1/get/page"
querystr = {
    "codes": [
        "0000"
    ]
}
config = {
    "appid": "54712c79-36f1-4f99-b467-db15d5c122d2",
    "privateKey": "00b88a2510398d98f8d81147cfb5c7843e8eef223d3cc5ee69221538a1ff6f366e",
    "publicKey": "56c72d559d9cf81382a23ca20828e71d7b9c8958fe2063de5af191c9a779f1d9441ca922dc1e8856fe43c7d9ef9b5268a6b6fbed8a1efc2944c347dddfff62d8",
    "host": "https://api.cmbchina.com",
    "CSCPRJCOD": "XGB33702",
}

xft = XFT(**config)
a = xft.post(api, querystr)
print(a)
