# 天气持续MCP Server
## weather.py 为调用美国国家气象局实现的天气查询服务
## chinaweather.py 为调用高德地图的天气API实现的中国天气查询服务

# 说明
weather.py和chinaweather.py都引用了settings.py。seetings.py为相关API的常量定义，请根据情况进行修改。

```python
# 高德天气
GD_API_BASE = "https://restapi.amap.com/v3/weather/weatherInfo"
GD_API_KEY  = "your api key"

# 美国国家气象局 (NWS) API 的基础 URL 和请求头
NWS_API_BASE = "https://api.weather.gov"
NWS_USER_AGENT = "weather-app/1.0"
~~~