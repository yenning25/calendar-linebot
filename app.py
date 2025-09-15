from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    PostbackAction,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent
)
import os

# Azure
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 訊息事件
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    quickReplyItems=[
        QuickReplyItem(
             action=PostbackAction(
                 label="英文",
                 data=f"lang=en&text={text}",
                 display_text="英文"
             )
         ),
         QuickReplyItem(
             action=PostbackAction(
                 label="日文",
                 data=f"lang=ja&text={text}",
                 display_text="日文"
             )
         ),
         QuickReplyItem(
             action=PostbackAction(
                 label="繁體中文",
                 data=f"lang=zh&text={text}",
                 display_text="繁體中文"
             )
         ),
         QuickReplyItem(
             action=PostbackAction(
                 label="文言文",
                 data=f"lang=lzh&text={text}",
                 display_text="文言文"
             )
         )
    ]
            
    reply_message(event,[TextMessage(
       text='請選擇要翻譯的語言:',
       quick_reply=QuickReply(
           items=quickReplyItems
       )
    )])
            
# 回覆訊息
def reply_message(event,messages):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        )

# 處理 Azure 翻譯    
def azure_translate(event,messages):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        ) 

if __name__ == "__main__":
    app.run()