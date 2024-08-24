#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import time

import requests

from .SM2 import *
from .SM3 import *


def getHttpStatus(arg):
    try:
        codes = arg.status_code
        return codes
    except:
        sys.exit(0)


def getHttpMessage(arg):
    try:
        reason = arg.reason
        return reason
    except:
        sys.exit(0)


class XFT:
    """
    说明：
        - 该构造类用于调用薪福通平台API接口。
        - 它包括应用的ID、密钥对、公钥对、以及用于调用的接口地址。

        参数:
        - *appid: 应用程序的唯一标识符。
        - *privateKey: 应用程序的私有密钥，用于签名验证。
        - *publicKey: 应用程序的公有密钥，用于加密通信。
        - *host: 薪福通API服务器的地址。
        - *CSCPRJCOD: 企业号。
        - CSCUSRNBR: 企业在薪福通平台上的用户编号。
        - CSCUSRUID: 薪福通平台为该企业分配的用户UID。
    """

    def __init__(self, **kwargs):
        necessary_fields = {
            "appid": "应用程序的唯一标识符",
            "privateKey": "应用程序的私有密钥，用于签名验证",
            "publicKey": "应用程序的公有密钥，用于加密通信",
            "host": "薪福通API服务器的地址",
            "CSCPRJCOD": "企业号"
        }

        missing_fields = {field: description for field, description in necessary_fields.items() if field not in kwargs}
        assert not missing_fields, ('缺少必要参数:' + str(missing_fields))
        self.appid = kwargs.get("appid")
        self.privateKey = kwargs.get("privateKey")
        self.publicKey = kwargs.get("publicKey")
        self.host = kwargs.get("host")
        self.CSCPRJCOD = kwargs.get("CSCPRJCOD")
        self.CSCUSRNBR = kwargs.get("CSCUSRNBR", "A0001")
        self.CSCUSRUID = kwargs.get("CSCUSRUID", "AUTO0001")
        # 网关校验时间戳
        self.timestamp = str(int(time.time()))
        self.query = (f"?CSCAPPUID={self.appid}&"
                      f"CSCPRJCOD={self.CSCPRJCOD}&"
                      f"CSCREQTIM={self.timestamp}&"
                      f"CSCUSRNBR={self.CSCUSRNBR}&"
                      f"CSCUSRUID={self.CSCUSRUID}")

    def header(self, method, path, bodyStr):
        sm2_test = SM2(self.privateKey, self.publicKey)
        # 签名校验方式-verify
        verify = "sm3withsm2"  # 非对称签名

        digest = Hash_sm3(bodyStr, 0)
        # print("digest: " + digest)
        # 对appid等参数进行拼接
        temp = ' '
        changeLine = '\n'
        includeDigest = 'x-alb-digest: '
        includeTime = 'x-alb-timestamp: '
        signStr = method + temp + path + changeLine + includeDigest + bodyStr + changeLine + includeTime + self.timestamp
        apisign = sm2_test.test_SM2_SM3(signStr.encode('utf-8'))
        header = {
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "close",
            "appid": self.appid,
            "apisign": apisign,
            "x-alb-verify": verify,
            "x-alb-digest": digest,
            "x-alb-timestamp": self.timestamp
        }
        return header

    def post(self, api, bodyStr):
        path = api + self.query
        url = self.host + path
        bodyStr = json.dumps(bodyStr)
        header = self.header("POST", path, bodyStr=bodyStr)
        res = requests.post(url, headers=header, data=bodyStr)
        result = res.text
        code = getHttpStatus(res)
        reason = getHttpMessage(res)
        return {"msg": "状态码及描述：" + str(code) + " " + reason, "data": result}
