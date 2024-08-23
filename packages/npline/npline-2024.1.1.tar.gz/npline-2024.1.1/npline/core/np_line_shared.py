import datetime
import requests
import datetime
from pytz import timezone


class LINE(object):
    def __init__(self, token_id, instance_id=1):
        self.__classname__ = "NPLineNoti"
        self.__author__ = "n.phantawee@gmail.com"
        self.__version__ = 1.00
        self.LINE_ACCESS_TOKEN = token_id
        self.NOTIFY_URL = "https://notify-api.line.me/api/notify"
        self.LINE_HEADER = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + self.LINE_ACCESS_TOKEN,
        }
        self.session = requests.Session()

    # ============================================= Add more methods here =============================================
    def send_to_api(self, payload, file=None):
        retry_flag = True
        while retry_flag:
            try:
                if file is not None:
                    LINE_HEADERS = {
                        "Authorization": "Bearer " + self.LINE_ACCESS_TOKEN
                    }
                    self.session.post(
                        self.NOTIFY_URL,
                        headers=LINE_HEADERS,
                        data=payload,
                        files=file,
                    )
                else:
                    self.session.post(
                        self.NOTIFY_URL,
                        headers=self.LINE_HEADER,
                        data=payload,
                        files=file,
                    )
            except Exception as e:
                pass
            else:
                retry_flag = False

    def get_now_th(self):
        now_th = datetime.datetime.now(timezone("Asia/Bangkok"))
        return now_th.strftime("%Y-%m-%d %H:%M:%S")

    def send_msg(self, message, with_time=False):
        if with_time:
            message = self.get_now_th() + ": " + message  # add time
        payload = {"message": message}
        return self.send_to_api(payload)


# Test the class methods
if __name__ == "__main__":
    a = LINE(token_id="YOUR_NOTIFICATION_KEY", instance_id=1)
    a.send_msg("Hello Dew")
