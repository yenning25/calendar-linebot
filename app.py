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
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
    DatetimePickerAction,
    FlexMessage, 
    BubbleContainer, 
    BoxComponent, 
    ButtonComponent,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent
)
import os

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
    buttons_template = ButtonsTemplate(
        title="請選擇",
        text="請點選以下功能：",
        actions=[
            PostbackAction(
                label="查詢",
                data="action=search"
            ),
            PostbackAction(
                label="共用",
                data="action=group"
            ),
            PostbackAction(
                label="我的",
                data="action=my"
            ),
        ]
    )

    message = TemplateMessage(
        alt_text="功能選單",
        template=buttons_template
    )
    reply_message(event, [message])

@line_handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data

    if data == "action=search":
        # 回覆一個帶日期選擇器的 FlexMessage
        flex = FlexMessage(
            alt_text="選擇日期時間",
            contents=BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        ButtonComponent(
                            style="primary",
                            color="#ff9933",
                            action=DatetimePickerAction(
                                label="選擇日期時間",
                                data="action=datetime",
                                mode="datetime",
                                initial="2025-01-01T00:00",
                                min="2024-01-01T00:00",
                                max="2026-12-31T23:59"
                            )
                        )
                    ]
                )
            )
        )
        reply_message(event, [flex])


def reply_message(event, messages):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        )