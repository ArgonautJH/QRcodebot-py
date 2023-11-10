import compile
import re
import os
import config
import qrcode
import time
from io import BytesIO
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

#set the bot token for your Slack bot 
bot_token = config.bot_token

#Initialize a Slack Bolt app
app = App(token=config.bot_token)

# 프로세스 처리 진행 여부를 확인하기 위한 함수
processing_flag = False

# QR코드 생성함수(주소를 받아옴)
def generate_qr_code(text_value):
    qr = qrcode.QRCode(
        version=1,  # 1-40
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # L, M, H
        box_size=15,
        border=4,
    )

    qr.add_data(text_value)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    return img
    

# QR코드 업로드 함수
# 이미지를 바이트 코드로 변환하여 PNG형식으로 저장
# 이후 Slack API를 사용하여 지정된 채널에 업로드
def upload_qr_code(client, channel, img):
    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)

    try:
        response = client.files_upload(
            channels=channel,
            file=img_bytes,
            filename="qrcode.png",
            title="QR Code",
        )
    except Exception as e:
        print(f"Error uploading file: {e}")
        
# 메시지를 수신 받아 처리하는 함수
@app.message(re.compile("링크:"))
def aks_qrcode(event, client, say):
    global processing_flag

    if processing_flag:
        say("데이터 처리 중입니다. 잠시 후에 다시 시도해주세요.")
        return

    try:
        processing_flag = True
        say("데이터가 전달되었습니다.")

        if 'blocks' in event and event['blocks']:
            say("데이터 가공 중입니다.")
            rich_text_section_block = event['blocks'][0].get('elements', [{}])[0]
            text_value = rich_text_section_block.get('elements', [{}])[1].get('text', '')
            print('text_value:', text_value)

            img = generate_qr_code(text_value)
            upload_qr_code(client, event["channel"], img)
        else:
            say("링크를 찾을 수 없습니다.")
    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        processing_flag = False

    
#start the Socket Mode handler
if __name__ == "__main__":
    handler = SocketModeHandler(app_token=config.app_token,app=app)
    handler.start()