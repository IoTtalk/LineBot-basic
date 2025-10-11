# -*- coding: UTF-8 -*-

import uuid
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, PushMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent

import config
configuration = Configuration(access_token=config.ChannelAccessToken)
handler = WebhookHandler(config.ChannelSecret)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."        

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

msg_queue = []
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global user_id_set
    Msg = event.message.text
    print('    Incoming Msg: {}'.format(Msg))
    
    msg_queue.append(Msg)
    userId = event.source.user_id
    print('    From userId:', userId,)

    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)    
    '''
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )
    '''

def pushLineMsg(Msg):
    for userId in user_id_set:
        try:        
            with ApiClient(configuration) as api_client:        
                api_instance = MessagingApi(api_client)
                push_message_request = PushMessageRequest(to=userId, messages=[TextMessage(text=Msg)])    
                api_response = api_instance.push_message(push_message_request, x_line_retry_key=str(uuid.uuid4()))
                #print("The response of MessagingApi->push_message:\n", api_response)
                print('PushMsg: {}'.format(Msg))
        except Exception as e:
            print('Failed to send message. Error:\n', e)

user_id_set=set()                                    
def saveUserId(userId):
        idFile = open(config.idfilePath, 'a')
        idFile.write(userId+';')
        idFile.close()

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

def init(port=32768):    
    pushLineMsg('LineBot is ready.')
    app.run('127.0.0.1', port=port, threaded=True, use_reloader=False)

idList = loadUserId()
if idList: user_id_set = set(idList)                   

if __name__ == "__main__":
    init()
    