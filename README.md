# python-spider

## 介绍
python爬虫 及selenium自动登录

## 小工具

- [滑块验证码破解](https://gitee.com/Euphoria_wang/python-spider/blob/master/slideUnlock.py)

## 目录

### [自动化实战](#自动化实战)

1. #### [QQ空间自动登录](https://gitee.com/Euphoria_wang/python-spider/tree/master/QzoneLogin "悬停显示")

2. #### [12306自动登录](https://gitee.com/Euphoria_wang/python-spider/blob/master/12306Login.py "悬停显示")

### [爬虫实战](#爬虫实战)

1. []( "悬停显示")
2. 

## 自动化实战

### QzoneLogin.py 

功能：QQ空间自动登录

### 12306Login.py

功能：12306自动登录

使用说明：验证码识别使用的超级鹰，百度搜索'超级鹰'注册并下载Python示例代码，并与此代码放在同一个文件夹下

超级鹰不会用自行百度(不负责任~)

注意事项：

```python
# 导入超级鹰示例代码
from chaojiying import Chaojiying_Client
```

```python
chaojiying = Chaojiying_Client('超级鹰用户名', '密码', 'ID')  # 用户中心>>软件ID 生成一个替换 96001
im = open('../documents/a.jpeg', 'rb').read()  # 本地图片文件路径 来替换 a.jpeg
    # print(chaojiying.PostPic(im, 9004))  # 1902 验证码类型 官方网站>>价格体系
```

```python
username_tag.send_keys('xxx')     # 12306用户名
password_tag.send_keys('xxx') 	# 12306密码
```



## 爬虫实战

3.  
