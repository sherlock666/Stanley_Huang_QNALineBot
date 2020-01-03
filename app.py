import requests
import re
import configparser
import os
import random
import pandas as pd
import runpy
#叫入並執行其他.py用
import urllib
import time
import tempfile
import json
from bs4 import BeautifulSoup
from flask import Flask, request, abort
#from imgurpython import ImgurClient
from argparse import ArgumentParser
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction, URITemplateAction,PostbackTemplateAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,VideoSendMessage, ImageSendMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,ImagemapSendMessage, BaseSize, URIImagemapAction,
    ImagemapArea, MessageImagemapAction,
    Video, ExternalLink
)

##### Function Import #####
import subprocess

##### Main #####

app = Flask(__name__)

### another way using config.ini
config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static')

client_id = config['imgur_api']['Client_ID']
client_secret = config['imgur_api']['Client_Secret']
album_id = config['imgur_api']['Album_ID']
access_token = config['imgur_api']['Access_token']
refresh_token = config['imgur_api']['Refresh_token']
API_Get_Image = config['other_api']['API_Get_Image']

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static')



### this part is constant  don't change
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'

##### QNA 設定區 勿動 #####

@app.route("/qnamaker", methods=['POST'])
def get_answer(message_text):

    #url = "https://chevadymeowbotqna.azurewebsites.net/qnamaker/knowledgebases/4535ecb8-21ee-42c6-90a4-5b2529a710c4/generateAnswer"
    url = "https://clinicqabot.azurewebsites.net/qnamaker/knowledgebases/765f23c6-e11d-4c09-8219-c65613543492/generateAnswer"
    
    response = requests.post(
        url,
        json.dumps({'question': message_text}),
        headers={'Content-Type': 'application/json',
                'Authorization': '74a100ce-d665-4af2-9576-a3e641b5de47'
        }
        )

    data = response.json()

    try:
        if "error" in data:
            return data["error"]["message"]
        else:    
            answer = data['answers'][0]['answer']
            return answer
    except Exception:
        return "Error occurs when finding answer"

    
##### 處理訊息 #####

@handler.add(MessageEvent, message=TextMessage)

def handle_message(event):
    event.message.text = get_answer(event.message.text)
    profile = line_bot_api.get_profile(event.source.user_id)
    print("event.reply_token:", event.reply_token)
    print("event.source.user_name:", profile.display_name)
    print("event.source.user_id:", event.source.user_id)
    print("event.message.text:", event.message.text)
    print("event.source.type:", event.source.type)
    ##event.message.text = get_answer(event.message.text)
    

######## 客製功能區 ########       
    if event.message.text == "aaa" :
        content = "哈囉"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0

#### 天氣預報 ####
    if event.message.text == "!天氣預報":
        content = "請輸入欲查詢地點\n(目前限台灣本島+離島)\n\n使用方式如下(已設有防呆):\n!台北市\n!臺北市\n!台北\n!臺北\n!taipei"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "!台北市" or event.message.text == "!臺北市" or event.message.text == "!台北" or event.message.text == "!臺北" or event.message.text == "!taipei":
        content = weather(L=0)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!新北市" or event.message.text == "!新北" or event.message.text == "!new taipei":
        content = weather(L=1)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!桃園市" or event.message.text == "!taoyuan":
        content = weather(L=2)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!台中市" or event.message.text == "!臺中市" or event.message.text == "!台中" or event.message.text == "!臺中" or event.message.text == "!taichung":
        content = weather(L=3)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!台南市" or event.message.text == "!臺南市" or event.message.text == "!台南" or event.message.text == "!臺南" or event.message.text == "!tainan":
        content = weather(L=4)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!高雄市" or event.message.text == "!高雄" or event.message.text == "!kaohsiung":
        content = weather(L=5)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!基隆市" or event.message.text == "!基隆" or event.message.text == "!keelung":
        content = weather(L=6)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!新竹縣" or event.message.text == "!hsinchu county":
        content = weather(L=7)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!新竹市" or event.message.text == "!hsinchu city":
        content = weather(L=8)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!苗栗縣" or event.message.text == "!苗栗" or event.message.text == "!miaoli":
        content = weather(L=9)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!彰化縣" or event.message.text == "!彰化" or event.message.text == "!changhua":
        content = weather(L=10)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!南投縣" or event.message.text == "!南投" or event.message.text == "!nantou":
        content = weather(L=11)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!雲林縣" or event.message.text == "!雲林" or event.message.text == "!yunlin":
        content = weather(L=12)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!嘉義縣" or event.message.text == "!chiayi county":
        content = weather(L=13)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!嘉義市" or event.message.text == "!chiayi city":
        content = weather(L=14)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!屏東縣" or event.message.text == "!屏東" or event.message.text == "!pingtung":
        content = weather(L=15)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!宜蘭縣" or event.message.text == "!宜蘭" or event.message.text == "!ilan":
        content = weather(L=16)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!花蓮縣" or event.message.text == "!花蓮" or event.message.text == "!hualien":
        content = weather(L=17)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!臺東縣" or event.message.text == "!台東" or event.message.text == "!taitung":
        content = weather(L=18)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!澎湖縣" or event.message.text == "!澎湖" or event.message.text == "!penghu":
        content = weather(L=19)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!金門縣" or event.message.text == "!金門" or event.message.text == "!jinmen":
        content = weather(L=20)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!連江縣" or event.message.text == "!連江" or event.message.text == "!lianjiang":
        content = weather(L=21)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0

############### 功能表功能 ###############
##########*****功能字庫區*****#########    

##########*****廢話字庫區*****#########      
    keywords_test_a = ['喵喵喵','測試測試']
    content_test_a = "我是小喵喵"
 
    keywords_test_b = ['喵~','喵喵~']
    content_test_b = "喵~喵~"
    
    keywords_test_c = ['喵?','喵喵?']
    content_test_c = "喵~~ (////)"
    
    if event.message.text in keywords_test_a:
        content = content_test_a
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0



##########*****休閒娛樂*****#########

##########***新聞***#########

##########***財經專區***#########  
    if event.message.text == "!每日匯率":
        res = requests.get("http://rate.bot.com.tw/xrt?Lang=zh-TW")
        soup = BeautifulSoup(res.text,'html.parser')
        dailydate=soup.select("span[class='time']")[0].text
        content1 = "本匯率資訊取自 台灣銀行告牌匯率\n提供 台幣對:\n美金 日幣 人民幣 港幣\n英鎊 韓元 歐元\n僅供使用者參考 謝謝!!\n\n請直接輸入欲查詢幣別(例如: !日幣)\n"+"最新掛牌時間 : "+dailydate
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content1))

    if event.message.text == "!美金":
        content = exchange_rates(L=1)
        print(content)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0

    if event.message.text == "!日幣":
        content = exchange_rates(L=15)
        print(content)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!人民幣":
        content = exchange_rates(L=37)
        print(content)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!港幣":
        content = exchange_rates(L=3)
        print(content)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!英鎊":
        content = exchange_rates(L=5)
        print(content)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!韓元":
        content = exchange_rates(L=31)
        print(content)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0
    if event.message.text == "!歐元":
        content = exchange_rates(L=29)
        print(content)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content))
        return 0     




#################### 主目錄 #####################
    if event.message.text == "!開始玩":
        fun="\n\n*****休閒娛樂*****\n新聞\n電影\n遊戲資訊\n看廢文\n圖片(施工中)"
        academic="\n\n*****學術專區*****\n施工中"
        medical="\n\n*****醫療新知*****\n施工中"
        financial="\n\n*****財經專區*****\n每日匯率"
        diy="\n\n*****自製小品*****\n猜數字(施工中)"
        other="\n\n*****其他功能*****\n天氣預報"
        SelfReplyOnly="\n\n*****私聊限定*****\n!本區功能無法於群組使用!\n!請點選本帳號的聊天以使用!\n施工中"
        content = ("請輸入功能指令:"+fun+academic+medical+financial+diy+SelfReplyOnly+other+"\n\n幫助")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "!新聞":
        content = "請選擇新聞類型:\n\n蘋果即時新聞\n科技新報\nPanX泛科技\n陸續增加...."
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "!電影":
        content = "請選擇來源:\n\n近期上映電影\neyny\n陸續增加...."
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "!遊戲資訊":
        content = "請選擇遊戲:\n\n神魔之塔\n少女前線\nfgo\n陸續增加...."
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "!看廢文":
        content = "請選擇來源:\n\n近期熱門廢文\n即時廢文"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "!圖片":
        content = "請輸入功能指令:\n\n***動漫區(施工中)***\nyande.re (抓圖)\n\n***其他***\nPTT表特版 (近期大於 10 推的文章)\nimgur正妹(施工中) (imgur 正妹圖片)\n抽抽樂(施工中) (隨便來張正妹圖片)\n陸續增加...."
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "!猜數字":
        content = "施工中~"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
######## 客製功能區 ########                
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
        return 0


if __name__ == '__main__':
    app.run()
