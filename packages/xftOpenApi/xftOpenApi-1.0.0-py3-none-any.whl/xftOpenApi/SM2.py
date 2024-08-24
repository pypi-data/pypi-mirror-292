from gmssl import sm2, func
import binascii
import base64

class SM2:
    def __init__(self, privateKey, publicKey):
        self.private_Key = privateKey
        self.public_Key = publicKey

    def str_to_hexStr(self, hex_str):
            """
            字符串转hex
            :param hex_str: 字符串
            :return: hex
            """
            hex_data = hex_str.encode('utf-8')
            str_bin = binascii.unhexlify(hex_data)
            return str_bin.decode('utf-8')

    def test_SM2_SM3(self, data):
        random_hex_str = '1234567812345678'.encode('utf-8').hex()
        print('random:%s' % random_hex_str)
        sm2_crypt = sm2.CryptSM2(public_key=self.public_Key, private_key=self.private_Key)
        sign = sm2_crypt.sign_with_sm3(data, random_hex_str)
        print('sign:%s' % sign)
        verify = sm2_crypt.verify_with_sm3(sign, data)
        print('verify:%s' % verify)
        # assert verify
        return sign
