# 引入 modal 模块及其子模块 App 和 Image，用于定义云函数应用及其运行环境
import modal
from modal import App, Image

# 创建一个 Modal 应用，命名为 "hello"
app = modal.App("hello")

# 使用 debian_slim 镜像，并安装 requests 库，作为远程函数的运行环境
image = Image.debian_slim().pip_install("requests")

# 使用装饰器 @app.function 定义一个远程函数 hello，指定运行环境为上面配置的 image
@app.function(image=image)
def hello() -> str:
    # 导入 requests 库（在镜像中已安装，此处在运行时导入）
    import requests

    # 向 ipinfo.io 发出请求，获取当前运行环境的 IP 地址对应的地理位置信息
    response = requests.get('https://ipinfo.io/json')

    # 将返回结果解析为 JSON 格式（Python 字典）
    data = response.json()

    # 从字典中提取城市、地区和国家字段
    city, region, country = data['city'], data['region'], data['country']

    # 返回一条包含地理位置的问候语
    return f"Hello from {city}, {region}, {country}!!"

# New - added thanks to student Tue H.!

@app.function(image=image, region="eu")
def hello_europe() -> str:
    import requests
    
    response = requests.get('https://ipinfo.io/json')
    data = response.json()
    city, region, country = data['city'], data['region'], data['country']
    return f"Hello from {city}, {region}, {country}!!"
