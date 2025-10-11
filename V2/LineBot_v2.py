# -*- coding: UTF-8 -*-
import time, threading
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import config

line_bot_api = LineBotApi(config.ChannelAccessToken) #LineBot's Channel access token
handler = WebhookHandler(config.ChannelSecret)       #LineBot's Channel secret
user_id_set=set()                                    #LineBot's Friend's user id 
app = Flask(__name__)


def loadUserId():
    try:
        idFile = open(config.idfilePath, 'r')
        idList = idFile.readlines()
        idFile.close()
        idList = idList[0].split(';')
        idList.pop()
        return idList
    except Exception as e:
        print(e)
        return None

def saveUserId(userId):
        idFile = open(config.idfilePath, 'a')
        idFile.write(userId+';')
        idFile.close()


def pushLineMsg(Msg):
    for userId in user_id_set:
        try:
            line_bot_api.push_message(userId, TextSendMessage(text=Msg))
        except Exception as e:
            print(e)
        print('PushMsg: {}'.format(Msg))


@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']    # get X-Line-Signature header value
    body = request.get_data(as_text=True)              # get request body as text
    #print("Request body: " + body, "Signature: " + signature)
    try:
        handler.handle(body, signature)                # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'

msg_queue = []
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_id_set
    Msg = event.message.text
#    if Msg == 'Hello, world': return
    print('Incoming Msg: {}'.format(Msg))
    msg_queue.append(Msg)
    userId = event.source.user_id
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)
    #line_bot_api.reply_message(event.reply_token,TextSendMessage(text="收到訊息!!"))   # reply api example

def init(port=32768):    
    pushLineMsg('LineBot is ready.')
    app.run('127.0.0.1', port=port, threaded=True, use_reloader=False)

idList = loadUserId()
if idList: user_id_set = set(idList)                   
if __name__ == "__main__":
    init()
    

    
