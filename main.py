from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.environ["USER_ID"].split("\n")
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['temp']), math.floor(weather['high']), math.floor(weather['low'])

def get_all():
  url = "https://v0.yiketianqi.com/api?unescape=1&version=v62&appid=88969948&appsecret=9HzeaQdq&city=" + city
  res = requests.get(url).json()
  zhishu = res['zhishu']
  
  return res['date'], res['week'], res['wea'], res['tem'], res['tem1'], res['tem2'], res['humidity'], res['air_level'], zhishu['chuanyi']['level'], zhishu['chuanyi']['tips'], zhishu['ziwaixian']['level'], zhishu['ziwaixian']['tips']

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)

we, temperature, highest, lowest = get_weather()
'''
data = {"weather":{"value":wea,"color":get_random_color()},"temperature":{"value":temperature,"color":get_random_color()},"love_days":{"value":get_count(),"color":get_random_color()},"birthday_left":{"value":get_birthday(),"color":get_random_color()},"words":{"value":get_words(),"color":get_random_color()},"highest": {"value":highest,"color":get_random_color()},"lowest":{"value":lowest, "color":get_random_color()}}
'''
date, week, wea, tem, tem_low, tem_high, hum, air_level, chuanyi_level, chuanyi_tips, ziwaixian_level, ziwaixian_tips = get_all()
data = {"date":{"value":date},"city":{"value":city},
        "week":{"value":week},"weather":{"value":wea},
        "temperature":{"value":tem},"min_temperature":{"value":tem_low},
        "max_temperature":{"value":tem_high},"humidity":{"value":hum},
        "air_level":{"value":air_level},"chuanyi_level":{"value":chuanyi_level},
        "chuanyi_tips":{"value":chuanyi_tips},"ziwaixian_level":{"value":ziwaixian_level},
        "ziwaixian_tips":{"value":ziwaixian_tips},"love_days":{"value":get_count()},
        "words":{"value":get_words(), "color":get_random_color()},
        "birthday_left":{"value":get_birthday()},
       "birthday_left":{"value":get_birthday(),"color":get_random_color()}}

count = 0
for user_id in user_ids:
  res = wm.send_template(user_id, template_id, data)
  count+=1

print("发送了" + str(count) + "条消息")
