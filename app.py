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

    url = "https://chevadymeowbotqna.azurewebsites.net/qnamaker/knowledgebases/4535ecb8-21ee-42c6-90a4-5b2529a710c4/generateAnswer"
    
    response = requests.post(
        url,
        json.dumps({'question': message_text}),
        headers={'Content-Type': 'application/json',
                'Authorization': '9b2c32d0-31e2-469b-8ed8-4ad1c93ad90d'
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
    profile = line_bot_api.get_profile(event.source.user_id)
    print("event.reply_token:", event.reply_token)
    print("event.source.user_name:", profile.display_name)
    print("event.source.user_id:", event.source.user_id)
    print("event.message.text:", event.message.text)
    print("event.source.type:", event.source.type)
    ##event.message.text = get_answer(event.message.text)
    if event.message.text == "開始玩" or event.message.text == "功能表" or event.message.text == "最新消息" :
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/DBRnv6d.png',
            alt_text='error 404 not found~',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='error 404 not found~ ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0  
        '''
        student_program="\n\n*****實習計畫*****\n新聞\n電影\n遊戲資訊\n看廢文\n圖片(施工中)"
        tc_program="\n\n*****提攜專區*****\n施工中"
        association_program="\n\n*****協會專區*****\n施工中"
        dt_program="\n\n*****DT專區*****\n施工中"
        campaign_program="\n\n*****Campaign專區*****\n施工中"
        other="\n\n*****其他功能*****\n天氣預報"

        SelfReplyOnly="\n\n*****私聊限定*****\n!本區功能無法於群組使用!\n!請點選本帳號的聊天以使用!\n施工中"
        
        content = ("請輸入功能指令:"+student_program+association_program+dt_program+campaign_program+SelfReplyOnly+other+"\n\n幫助")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
        '''

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
 
    keywords_cm_apple_news = ['!蘋果即時新聞','!蘋果即時','！蘋果即時新聞','！蘋果即時','蘋果即時新聞','蘋果即時']
    keywords_technews = ['!科技新報','！科技新報']
    keywords_panx = ['!PanX泛科技','！PanX泛科技']
    keywords_movie = ['!近期上映電影','！近期上映電影']
    keywords_eyny_movie = ['!eyny','！eyny']
    keywords_gfl_articles = ['!少女前線','！少女前線']
    keywords_tos_articles = ['!神魔之塔','！神魔之塔']
    keywords_fgo_articles = ['!fgo','！fgo']
    keywords_ptt_hot = ['!近期熱門廢文','！近期熱門廢文']
    keywords_ptt_gossiping = ['!即時廢文','！即時廢文']
    keywords_yande_re = ['!yande.re','!抽圖','！yande.re','！抽圖','抽圖','抽']
    keywords_ptt_beauty = ['!PTT表特版','！PTT表特版']
    keywords_imgur_beauty = ['!imgur正妹','！imgur正妹']
   # keywords_fgo_articles = ['!fgo']
   # keywords_fgo_articles = ['!fgo']
    
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

    if event.message.text in keywords_cm_apple_news:
        content0 = apple_newss_content0
        content1 = apple_newss_content1
        content2 = apple_newss_content2
        print (content0)
        print (content1)
        print (content2)
        a=TextSendMessage(text=content0)
        b=TextSendMessage(text=content1)
        c=TextSendMessage(text=content2)
        reply_data=[a,b,c]
        line_bot_api.reply_message(
            event.reply_token,
            reply_data)
        return 0

    if event.message.text in keywords_technews:
        content = technews()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text in keywords_panx:
        content = panx()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

##########***電影***#########
    if event.message.text in keywords_movie:
        content = movie()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text in keywords_eyny_movie:
        content = eyny_movie()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

##########***遊戲資訊***#########
    if event.message.text in keywords_gfl_articles:
        content0 = gfl_articles_content0
        content1 = gfl_articles_content1
        content2 = gfl_articles_content2
        content3 = gfl_articles_content3
        content4 = gfl_articles_content4
        print (content0)
        print (content1)
        print (content2)
        print (content3)
        print (content4)
        a=TextSendMessage(text=content0)
        b=TextSendMessage(text=content1)
        c=TextSendMessage(text=content2)
        d=TextSendMessage(text=content3)
        e=TextSendMessage(text=content4)
        reply_data=[a,b,c,d,e]
        line_bot_api.reply_message(
            event.reply_token,
            reply_data)
        return 0

    if event.message.text in keywords_tos_articles:
        content0 = tos_articles_content0
        content1 = tos_articles_content1
        content2 = tos_articles_content2
        content3 = tos_articles_content3
        content4 = tos_articles_content4
        print (content0)
        print (content1)
        print (content2)
        print (content3)
        print (content4)
        a=TextSendMessage(text=content0)
        b=TextSendMessage(text=content1)
        c=TextSendMessage(text=content2)
        d=TextSendMessage(text=content3)
        e=TextSendMessage(text=content4)
        reply_data=[a,b,c,d,e]
        line_bot_api.reply_message(
            event.reply_token,
            reply_data)
        return 0

    if event.message.text in keywords_fgo_articles:
        content0 = fgo_articles_content0
        content1 = fgo_articles_content1
        content2 = fgo_articles_content2
        content3 = fgo_articles_content3
        content4 = fgo_articles_content4
        print (content0)
        print (content1)
        print (content2)
        print (content3)
        print (content4)
        a=TextSendMessage(text=content0)
        b=TextSendMessage(text=content1)
        c=TextSendMessage(text=content2)
        d=TextSendMessage(text=content3)
        e=TextSendMessage(text=content4)
        reply_data=[a,b,c,d,e]
        line_bot_api.reply_message(
            event.reply_token,
            reply_data)
        return 0

##########***看廢文***#########        
    if event.message.text in keywords_ptt_hot:
        content = ptt_hot()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text in keywords_ptt_gossiping:
        content = ptt_gossiping()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

##########***圖片***#########  
    if event.message.text in keywords_yande_re:
        num=random.randint(100000,500000)
        yande_link=yande_res(num=int(num))
        image_message = ImageSendMessage(
            original_content_url=yande_link,
            preview_image_url=yande_link
        )        
        line_bot_api.reply_message(
            event.reply_token, image_message)
        return 0

    if event.message.text in keywords_ptt_beauty:
        content = ptt_beauty()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text in keywords_imgur_beauty:
        client = ImgurClient(client_id, client_secret)
        images = client.get_album_images(album_id)
        index = random.randint(0, len(images) - 1)
        url = images[index].link
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(
            event.reply_token, image_message)
        return 0
    if event.message.text == "!抽抽樂":
        image = requests.get(API_Get_Image)
        url = image.json().get('Url')
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(
            event.reply_token, image_message)
        return 0

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





############### 領袖營Menu ###############

    if event.message.text == "領袖營":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/OVA6PIl.png',
            alt_text='領袖營攻略手冊',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #Left 1
                MessageImagemapAction(
                    text='行囊準備',
                    area=ImagemapArea(
                        x=0, y=132, width=511, height=108
                    )
                ),
                #Right 1
                MessageImagemapAction(
                    text='遠征行程',
                    area=ImagemapArea(
                        x=539, y=132, width=501, height=108
                    )
                ),
                #Left 2
                MessageImagemapAction(
                    text='營地駐紮',
                    area=ImagemapArea(
                        x=0, y=257, width=511, height=108
                    )
                ),
                #Right 2
                MessageImagemapAction(
                    text='夥伴相認?',
                    area=ImagemapArea(
                        x=539, y=257, width=501, height=108
                    )
                ),
                #Left 3
                MessageImagemapAction(
                    text='戰區概況',
                    area=ImagemapArea(
                        x=0, y=390, width=511, height=108
                    )
                ),
                #Right 3
                MessageImagemapAction(
                    text='黎明前夕',
                    area=ImagemapArea(
                        x=539, y=391, width=501, height=108
                    )
                ),
                #Left 4   
                MessageImagemapAction(
                    text='青金石戰役',
                    area=ImagemapArea(
                        x=0, y=523, width=511, height=108
                    )
                ),
                #Right 4                                                          
                MessageImagemapAction(
                    text='商業競賽',
                    area=ImagemapArea(
                        x=539, y=523, width=501, height=108
                    )
                ),
                #bottom middle                                                          
                MessageImagemapAction(
                    text='叢林盛典?',
                    area=ImagemapArea(
                        x=332, y=658, width=404, height=102
                    )
                )                    
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

############### 行囊準備Menu ###############
    if event.message.text == "行囊準備":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/0G695Fa.png',
            alt_text='prepare list',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='prepare list ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )                                  
        line_bot_api.reply_message(event.reply_token, image_map_messages)
        return 0

############### 遠征行程Menu ###############
    if event.message.text == "遠征行程":
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/olJ8BrL.png',
            alt_text='day 1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='day 1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )            
        image_map_messages_2 = ImagemapSendMessage(
            base_url='https://i.imgur.com/FE43frj.png',
            alt_text='day 2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='day 2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )                       
        line_bot_api.reply_message(event.reply_token, [image_map_messages_1,image_map_messages_2])
        return 0

############### 營地駐紮Menu ###############
    if event.message.text == "營地駐紮":
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/Mq3riSQ.png',
            alt_text='roomtype 1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='roomtype 1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        image_map_messages_2 = ImagemapSendMessage(
            base_url='https://i.imgur.com/i0V2emp.png',
            alt_text='roomtype 2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='roomtype 2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        image_map_messages_3 = ImagemapSendMessage(
            base_url='https://i.imgur.com/gVFUtzy.png',
            alt_text='roomtype 3',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='roomtype 3 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )            
        line_bot_api.reply_message(event.reply_token,[image_map_messages_1,image_map_messages_2,image_map_messages_3])
        return 0

############### 夥伴相認Menu ###############
    if event.message.text == "夥伴相認?":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/iQtkUMO.png',
            alt_text='team ?',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='team ? ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "夥伴相認":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/irvh6C7.png',
            alt_text='夥伴相認Menu',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #Left 1
                MessageImagemapAction(
                    text='夥伴相認-第一組',
                    area=ImagemapArea(
                        x=166, y=207, width=315, height=115
                    )
                ),
                #Right 1
                MessageImagemapAction(
                    text='夥伴相認-第二組',
                    area=ImagemapArea(
                        x=564, y=207, width=312, height=117
                    )
                ),
                #Left 2
                MessageImagemapAction(
                    text='夥伴相認-第三組',
                    area=ImagemapArea(
                        x=164, y=382, width=315, height=118
                    )
                ),
                #Right 2
                MessageImagemapAction(
                    text='夥伴相認-第四組',
                    area=ImagemapArea(
                        x=567, y=383, width=311, height=118
                    )
                ),
                #Left 3
                MessageImagemapAction(
                    text='夥伴相認-第五組',
                    area=ImagemapArea(
                        x=164, y=568, width=317, height=116
                    )
                ),
                #Right 3
                MessageImagemapAction(
                    text='夥伴相認-第六組',
                    area=ImagemapArea(
                        x=564, y=564, width=313, height=115
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

        ##### 小組內容 #####

    if event.message.text == "夥伴相認-第一組":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/Obj0kIW.png',
            alt_text='team 1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='team 1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "夥伴相認-第二組":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/DhdCt0I.png',
            alt_text='team 2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='team 2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "夥伴相認-第三組":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/PgHoNqh.png',
            alt_text='team 3',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='team 3 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "夥伴相認-第四組":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/tIzjo3O.png',
            alt_text='team 4',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='team 4 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "夥伴相認-第五組":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/h8vsiur.png',
            alt_text='team 5',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='team 5 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "夥伴相認-第六組":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/3IyMawy.png',
            alt_text='team 6',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='team 6 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

############### 戰區概況Menu ###############
    if event.message.text == "戰區概況":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/nFFFW3q.png',
            alt_text='RPG MAP',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                ##### rpg1 #####
                MessageImagemapAction(
                    text='rpg1 1-1',
                    area=ImagemapArea(
                        x=885, y=9, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg1 1-2',
                    area=ImagemapArea(
                        x=885, y=94, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg1 2-1',
                    area=ImagemapArea(
                        x=885, y=180, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg1 2-2',
                    area=ImagemapArea(
                        x=885, y=267, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg1 2-4',
                    area=ImagemapArea(
                        x=885, y=354, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg1 3',
                    area=ImagemapArea(
                        x=885, y=440, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg1 5',
                    area=ImagemapArea(
                        x=885, y=526, width=139, height=65
                    )
                ),
                ###### rpg2 ######
                MessageImagemapAction(
                    text='rpg2 1',
                    area=ImagemapArea(
                        x=885, y=611, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg2 2',
                    area=ImagemapArea(
                        x=885, y=699, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg2 3',
                    area=ImagemapArea(
                        x=885, y=785, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg2 4',
                    area=ImagemapArea(
                        x=885, y=872, width=139, height=65
                    )
                ),
                MessageImagemapAction(
                    text='rpg2 5',
                    area=ImagemapArea(
                        x=885, y=957, width=139, height=65
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0
############### rpg1  ###############
    if event.message.text == "rpg1 1-1":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/22r7gDo.png',
            alt_text='rpg1 1-1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 1-1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg1 1-2":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/QGsmjsA.png',
            alt_text='rpg1 1-2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 1-2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg1 2-1":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/HXyZoqO.png',
            alt_text='rpg1 2-1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 2-1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg1 2-2":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/auHSbXi.png',
            alt_text='rpg1 2-2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 2-2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg1 2-4":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/O3qF4pf.png',
            alt_text='rpg1 2-4',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 2-4 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg1 3":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/yXFI26T.png',
            alt_text='rpg1 3',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 3 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg1 5":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/fpTFt9w.png',
            alt_text='rpg1 5',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 5 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg1 item-get":
        image_map_messages_item1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/xP1yYZp.png',
            alt_text='rpg1 item1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 item1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        image_map_messages_item2 = ImagemapSendMessage(
            base_url='https://i.imgur.com/2nFAM2X.png',
            alt_text='rpg1 item2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 item2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        image_map_messages_item3 = ImagemapSendMessage(
            base_url='https://i.imgur.com/6OjmQJk.png',
            alt_text='rpg1 item3',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg1 item3 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )            
        line_bot_api.reply_message(event.reply_token,[image_map_messages_item1,image_map_messages_item2,image_map_messages_item3])
        return 0
############### rpg2  ###############
    if event.message.text == "rpg2 1":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/CbvleCB.png',
            alt_text='rpg2 1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg2 1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg2 2":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/bO0JKA3.png',
            alt_text='rpg2 2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg2 2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg2 3":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/9C7TXxd.png',
            alt_text='rpg2 3',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg2 3 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg2 4":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/JJNOMwV.png',
            alt_text='rpg2 4',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg2 4 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

    if event.message.text == "rpg2 5":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/wQMJAvd.png',
            alt_text='rpg2 5',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg2 5 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0



############### RPG1Menu ###############
    if event.message.text == "黎明前夕":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/ovysB7o.png',
            alt_text='RPG1 Menu',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #Left 1
                MessageImagemapAction(
                    text='rpg1 1-1',
                    area=ImagemapArea(
                        x=94, y=234, width=384, height=125
                    )
                ),
                #Right 1
                MessageImagemapAction(
                    text='rpg1 1-2',
                    area=ImagemapArea(
                        x=589, y=234, width=383, height=125
                    )
                ),
                #Left 2
                MessageImagemapAction(
                    text='rpg1 2-1',
                    area=ImagemapArea(
                        x=95, y=430, width=383, height=123
                    )
                ),
                #Right 2
                MessageImagemapAction(
                    text='rpg1 2-2',
                    area=ImagemapArea(
                        x=588, y=427, width=381, height=127
                    )
                ),
                #Left 3
                MessageImagemapAction(
                    text='rpg1 2-4',
                    area=ImagemapArea(
                        x=96, y=624, width=383, height=125
                    )
                ),
                #Right 3
                MessageImagemapAction(
                    text='rpg1 3',
                    area=ImagemapArea(
                        x=588, y=623, width=384, height=126
                    )
                ),
                #Left 4
                MessageImagemapAction(
                    text='rpg1 5',
                    area=ImagemapArea(
                        x=95, y=819, width=383, height=124
                    )
                ),
                #Right 4
                MessageImagemapAction(
                    text='rpg1 item-get',
                    area=ImagemapArea(
                        x=586, y=811, width=391, height=136
                    )
                ),                                         
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0        
############### 青金石戰役Menu ###############
    if event.message.text == "青金石戰役":
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/0QCjZsq.png',
            alt_text='RPG2 Menu',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                MessageImagemapAction(
                    text='rpg2 1',
                    area=ImagemapArea(
                        x=235, y=225, width=568, height=101
                    )
                ),
                MessageImagemapAction(
                    text='rpg2 2',
                    area=ImagemapArea(
                        x=235, y=373, width=568, height=101
                    )
                ),
                MessageImagemapAction(
                    text='rpg2 3',
                    area=ImagemapArea(
                        x=235, y=520, width=568, height=101
                    )
                ),
                 MessageImagemapAction(
                    text='rpg2 4',
                    area=ImagemapArea(
                        x=235, y=667, width=568, height=101
                    )
                ),                   
                MessageImagemapAction(
                    text='rpg2 5',
                    area=ImagemapArea(
                        x=235, y=816, width=568, height=101
                    )
                )
            ]
        )
        image_map_messages_2 = ImagemapSendMessage(
            base_url='https://i.imgur.com/GapQdz6.png',
            alt_text='rpg2 time',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='rpg2 time ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,[image_map_messages_1,image_map_messages_2])
        return 0  
############### 商業競賽Menu ###############
    if event.message.text == "商業競賽":
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/g2nqShi.png',
            alt_text='commercial contest rule',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='commercial contest rule ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        image_map_messages_2 = ImagemapSendMessage(
            base_url='https://i.imgur.com/cLQYwCp.png',
            alt_text='commercial contest score',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='commercial contest score ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )      
        image_map_messages_3 = ImagemapSendMessage(
            base_url='https://i.imgur.com/XLQezjJ.png',
            alt_text='commercial contest question',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                MessageImagemapAction(
                    text='ccq 1&2',
                    area=ImagemapArea(
                        x=194, y=317, width=664, height=143
                    )
                ),
                MessageImagemapAction(
                    text='ccq 3&4',
                    area=ImagemapArea(
                        x=194, y=551, width=664, height=143
                    )
                ),                  
                MessageImagemapAction(
                    text='ccq 5&6',
                    area=ImagemapArea(
                        x=194, y=783, width=664, height=143
                    )
                )
            ]
        )                  
        line_bot_api.reply_message(event.reply_token,[image_map_messages_1,image_map_messages_2,image_map_messages_3])
        return 0 
    ##### ccq team question#####    
    if event.message.text == "ccq 1&2":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/f4hGB7S.png',
            alt_text='ccq 1&2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='ccq 1&2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0
    if event.message.text == "ccq 3&4":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/GVHJuHx.png',
            alt_text='ccq 3&4',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='ccq 3&4 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0
    if event.message.text == "ccq 5&6":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/PARktV8.png',
            alt_text='ccq 5&6',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='ccq 5&6 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

############### 叢林盛典 ###############
    if event.message.text == "叢林盛典":
        image_map_messages = ImagemapSendMessage(
            base_url='https://i.imgur.com/KmDJRG1.png',
            alt_text='party night',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='party night description',
                    area=ImagemapArea(
                        x=230, y=291, width=557, height=147
                    )
                ),
                MessageImagemapAction(
                    text='party night process',
                    area=ImagemapArea(
                        x=230, y=512, width=558, height=156
                    )
                ),
                MessageImagemapAction(
                    text='party night lyrics',
                    area=ImagemapArea(
                        x=229, y=774, width=558, height=149
                    )
                ),                   
            ]
        )
        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0            
    ######## 考驗說明 ########
    if event.message.text == "party night description":
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/x6i76dq.png',
            alt_text='party night description 1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='party night description 1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        ),
        image_map_messages_2= ImagemapSendMessage(
            base_url='https://i.imgur.com/fmfDGW0.png',
            alt_text='party night description 2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='party night description 2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        ),
        image_map_messages_3 = ImagemapSendMessage(
            base_url='https://i.imgur.com/LlCLInS.png',
            alt_text='party night description 3',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='party night description 3 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token,[image_map_messages_1,image_map_messages_2,image_map_messages_3])
        return 0

    ######## 走秀流程 #########
    if event.message.text == "party night process":
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/PARktV8.png',
            alt_text='party night process 1',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='party night process 1 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        ),
        image_map_messages_2 = ImagemapSendMessage(
            base_url='https://i.imgur.com/9AZe5dY.png',
            alt_text='party night process 2',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='party night process 2 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )            
        line_bot_api.reply_message(event.reply_token,[image_map_messages_1,image_map_messages_2])
        return 0     

    ######## 營歌歌詞 #########
    if event.message.text == "party night lyrics ":
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/PARktV8.png',
            alt_text='ccq 5&6',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='ccq 5&6 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        ),
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/PARktV8.png',
            alt_text='ccq 5&6',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='ccq 5&6 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        ),
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/PARktV8.png',
            alt_text='ccq 5&6',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='ccq 5&6 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        ),           
        image_map_messages_1 = ImagemapSendMessage(
            base_url='https://i.imgur.com/PARktV8.png',
            alt_text='ccq 5&6',
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                #just for full size image
                MessageImagemapAction(
                    text='ccq 5&6 ',
                    area=ImagemapArea(
                        x=1034, y=1034, width=1, height=1
                    )
                )
            ]
        )



        line_bot_api.reply_message(event.reply_token,image_map_messages)
        return 0

###############  ###############
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
