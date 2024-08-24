#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import time

import requests

from SM2 import *
from SM3 import *


class XFT:
    def __init__(self, env):
        if env == "生产环境":
            self.appid = "54712c79-36f1-4f99-b467-db15d5c122d2"
            self.privateKey = "00b88a2510398d98f8d81147cfb5c7843e8eef223d3cc5ee69221538a1ff6f366e"
            self.publicKey = "56c72d559d9cf81382a23ca20828e71d7b9c8958fe2063de5af191c9a779f1d9441ca922dc1e8856fe43c7d9ef9b5268a6b6fbed8a1efc2944c347dddfff62d8"
            self.host = "https://api.cmbchina.com"
        elif env == "测试环境":
            self.appid = "2be2ea59-9e38-4fb2-831c-ccefc69ab36e"
            self.privateKey = "0a30c52ecf2dc4e8b28628118d992e183d8d0730eba5bcbb46b9267a0a668026"
            self.publicKey = "23387b356c56cd907959cb41125a44b48eab373452f47a0d0985b967ea6d9c9e415bada1c21a93f6095376e938ef058b58dff610282e8ab992fa03b2a7566e08"
            self.host = "https://api.cmburl.cn:8065"
        # 网关校验时间戳
        self.timestamp = str(int(time.time()))
        self.query = f"?CSCAPPUID={self.appid}&CSCPRJCOD=XGB33702&CSCREQTIM={self.timestamp}&CSCUSRNBR=A0001&CSCUSRUID=AUTO0001"

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
        # print(signStr)

        apisign = sm2_test.test_SM2_SM3(signStr.encode('utf-8'))
        # print("apisign: " + apisign)

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
        print(result)
        # print("X-CorrelationID: " + res.headers.get('X-CorrelationID'))
        print("状态码及描述：" + str(code) + " " + reason)
        return result


def get(url, data, header):
    res = requests.get(url, params=data, headers=header)
    result = res.text
    code = getHttpStatus(res)
    reason = getHttpMessage(res)
    print(result)
    # print("X-CorrelationID: " + res.headers.get('X-CorrelationID'))
    print("状态码及描述：" + str(code) + " " + reason)
    print(result)


def post(url, header, querystr):
    res = requests.post(url, headers=header, data=querystr)
    result = res.text
    code = getHttpStatus(res)
    reason = getHttpMessage(res)
    print(result)
    # print("X-CorrelationID: " + res.headers.get('X-CorrelationID'))
    print("状态码及描述：" + str(code) + " " + reason)
    return result


def put(url, header, querystr):
    # if querystr != None and querystr != "":
    #     data = eval(querystr)
    res = requests.put(url, headers=header, data=querystr)
    result = res.text
    print(result)
    code = getHttpStatus(res)
    reason = getHttpMessage(res)
    print("状态码及描述：" + str(code) + " " + reason)
    return result


def delete(url, querystr):
    res = requests.delete(url)
    result = res.text
    print(result)


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


# 生成国密秘钥对


if __name__ == "__main__":
    # 查询组织结构
    # api = "/ORG/orgqry/xft-service-organization/org/v1/get/page"
    # querystr = {
    #   "codes": [
    #     "0000"
    #   ]
    # }
    # xft = XFT("生产环境")
    # xft.post(api, querystr)

    # 查询员工信息
    api = "/hrm/hrm2/xft-employeeprofile/employee/external/api/query/staffInfo"
    querystr = {
        "queryFilterList": [
            {
                "fieldKey": "stfName",
                "fieldQueryMethod": "EQUAL",
                "fieldValue": "李小涛"
            }
        ],
        "queryResultType": {
            "queryType": "FIELD",

            "queryFieldList": [
                "sex",
                "seniorityBeginDate",
                "firstWorkDate"
            ]
        },
        "currentPage": "1",
        "pageSize": "10"
    }
    xft = XFT("生产环境")
    xft.post(api, querystr)

    # appid = "54712c79-36f1-4f99-b467-db15d5c122d2"
    # privateKey = "00b88a2510398d98f8d81147cfb5c7843e8eef223d3cc5ee69221538a1ff6f366e"
    # publicKey = "56c72d559d9cf81382a23ca20828e71d7b9c8958fe2063de5af191c9a779f1d9441ca922dc1e8856fe43c7d9ef9b5268a6b6fbed8a1efc2944c347dddfff62d8"
    # host = "https://api.cmbchina.com"
    # sm2_test = SM2(privateKey, publicKey)
    # # 网关校验时间戳
    # timestamp = str(int(time.time()))
    # # print("时间戳：" + timestamp)
    # # 签名校验方式-verify
    # verify = "sm3withsm2"  # 非对称签名
    # query = f"?CSCAPPUID={appid}&CSCPRJCOD=XGB33702&CSCREQTIM={timestamp}CSCUSRNBR=A0001&CSCUSRUID=AUTO0001"
    # path = "/ORG/orgqry/xft-service-organization/org/v1/get/page" + query
    # url = host + path
    # # print("请求地址：" + url)
    # # post传递参数
    # bodyStr = {
    #     # "codes": [
    #     #   "0000"
    #     # ]
    # }
    # fin_body1 = json.dumps(bodyStr)
    # digest = Hash_sm3(fin_body1, 0)
    # # print("digest: " + digest)
    # method = "POST"
    # # 对appid等参数进行拼接
    # temp = ' '
    # changeLine = '\n'
    # includeDigest = 'x-alb-digest: '
    # includeTime = 'x-alb-timestamp: '
    # signStr = method + temp + path + changeLine + includeDigest + fin_body1 + changeLine + includeTime + timestamp
    # # print(signStr)
    #
    # apisign = sm2_test.test_SM2_SM3(signStr.encode('utf-8'))
    # # print("apisign: " + apisign)
    #
    # header = {
    #     "Content-Type": "application/json;charset=UTF-8",
    #     "Connection": "close",
    #     "appid": appid,
    #     "apisign": apisign,
    #     "x-alb-verify": verify,
    #     "x-alb-digest": digest,
    #     "x-alb-timestamp": timestamp
    # }
    # data = {
    # }
    # values_json = json.dumps(bodyStr)
    # if method == "GET":
    #     get(url, data, header)
    # elif method == "POST":
    #     post(url, header, values_json)
    # elif method == "PUT":
    #     put(url, header, bodyStr)
    # elif method == "DELETE":
    #     delete(url, bodyStr)
