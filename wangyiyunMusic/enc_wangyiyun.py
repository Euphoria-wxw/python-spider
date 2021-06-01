from Crypto.Cipher import AES
from base64 import b64encode


e = '010001'  # brx1x(["流泪", "强"])
# brx1x(Sc3x.md)
f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
g = '0CoJUm6Qyw8W8jud'  # brx1x(["爱心", "女孩", "惊恐", "大笑"])
i = 'Hja3ia3Vrc7MZtgs'  # 16为随机值，这里写死成固定值


# 加密过程，相当于网易云音乐.js中的b函数
def enc_params(data, key):
    c = key.encode('utf-8')
    d = '0102030405060708'.encode('utf-8')
    # 处理加密内容
    data = to_16(data)
    e = data.encode('utf-8')

    aes = AES.new(key=c, mode=AES.MODE_CBC, IV=d)  # 创建加密器
    bs = aes.encrypt(e)  # 加密过程
    return str(b64encode(bs), 'utf-8')  # 转化成字符串返回


# 加密内容的长度必须是16的倍数
def to_16(data):
    pad = 16 - len(data) % 16
    # print(pad,len(data))
    data += chr(pad) * pad
    return data


# 获取post请求参数中params,相当于网易云音乐.js中的d函数
def get_params(data):
    first = enc_params(data, g)
    second = enc_params(first, i)
    return second


#  相当于网易云音乐.js中的c函数,
#  encSecKey的值只随16位随机值i而变化，这里因为i写死，所以直接返回固定值
def get_encSecKey():
    return "86d4fc023c9b0b8263f9a0705191bf0af7e730ed657275732bf9c15b9010e162375473b2fe61c70d2439d188824432dd308a127c27f87e11a925a4c10f6cfc7c1586fccd88dbef73b34a12e5aaf3d56fecd4e017c3fba68df385ebc2eeee272d8eef573a1827a4df35583720e73fa5cd23a05298229ea707b118b365c3f29b18"
