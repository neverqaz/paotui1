# -*- coding: utf-8 -*-

# pip install pycryptodome
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class Ali_AUTH_TOKEN(object):
    """
    alipay.system.oauth.token(换取授权访问令牌)
    """

    def __init__(self, appid, app_private_key_path,
                 alipay_public_key_path, debug=False):
        self.appid = appid
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        # self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.importKey(fp.read())

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_auth(self, code):
        """获取auth_code"""
        data = self.build_body(code)
        return self.sign_data(data)

    def direct_user(self, auth_token):
        """获取auth_token"""
        data = self.build_body1(auth_token)
        return self.sign_data(data)

    def build_body1(self, auth_token):
        data = {
            "app_id": self.appid,
            "method": "alipay.user.info.share",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            'auth_token': auth_token
        }

        # if return_url is not None:
        #
        #     data["return_url"] = self.return_url

        return data

    def build_body(self, code):
        data = {
            "app_id": self.appid,
            "method": "alipay.system.oauth.token",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            'grant_type': "authorization_code",
            'code': code
        }

        # if return_url is not None:
        #
        #     data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        # ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)

# if __name__ == "__main__":
# return_url = 'http://127.0.0.1:8000/?total_amount=100.00&timestamp=2017-08-15+23%3A53%3A34&sign=e9E9UE0AxR84NK8TP1CicX6aZL8VQj68ylugWGHnM79zA7BKTIuxxkf%2FvhdDYz4XOLzNf9pTJxTDt8tTAAx%2FfUAJln4WAeZbacf1Gp4IzodcqU%2FsIc4z93xlfIZ7OLBoWW0kpKQ8AdOxrWBMXZck%2F1cffy4Ya2dWOYM6Pcdpd94CLNRPlH6kFsMCJCbhqvyJTflxdpVQ9kpH%2B%2Fhpqrqvm678vLwM%2B29LgqsLq0lojFWLe5ZGS1iFBdKiQI6wZiisBff%2BdAKT9Wcao3XeBUGigzUmVyEoVIcWJBH0Q8KTwz6IRC0S74FtfDWTafplUHlL%2Fnf6j%2FQd1y6Wcr2A5Kl6BQ%3D%3D&trade_no=2017081521001004340200204115&sign_type=RSA2&auth_app_id=2016080600180695&charset=utf-8&seller_id=2088102170208070&method=alipay.trade.page.pay.return&app_id=2016080600180695&out_trade_no=20170202185&version=1.0'
# o = urlparse(return_url)
# query = parse_qs(o.query)
# processed_query = {}
# ali_sign = query.pop("sign")[0]


# alipay = AliPay(
#     appid="2016091700530193",
#     app_notify_url="http://123.206.43.75:8080/alipay/return/",
#     app_private_key_path="../trade/keys/private_key.txt",
#     alipay_public_key_path="../trade/keys/alipay_key_2048",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
#     debug=True,  # 默认False,
#     return_url="http://123.206.43.75:8080/alipay/return/"
# # )
#
# for key, value in query.items():
#     processed_query[key] = value[0]
# print (alipay.verify(processed_query, ali_sign))
#
# url = alipay.direct_pay(
#     subject="戴世伟欠五亿",
#     out_trade_no="20170202ssswq11234567561",
#     total_amount=100,
#     return_url="http://123.206.43.75:8080/alipay/return/"
# )
# re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
#
# print(re_url)
