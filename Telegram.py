import json
import requests

class TelegramMessenger:
    def __init__(self):
        f = open("telegramconfig.json", "r"); jsonconfig = f.read(); f.close()
        telegramconfigconfig = json.loads(jsonconfig)
        
        self.TELEGRAM_BOT_TOKEN = telegramconfigconfig['bottoken']
        self.TELEGRAM_CHAT_ID = telegramconfigconfig['chatid']
        self.sendTelegramMsg = telegramconfigconfig['sendTelegramMsg']
        

    def telegram_sendmsg(self, msg, notify):
        #notify:  0 means notify user and 1 means deliver the notification without notifying user\n",
        msg = str(msg)
        send_msg = 'https://api.telegram.org/bot' + self.TELEGRAM_BOT_TOKEN +  '/sendMessage?chat_id=' +  self.TELEGRAM_CHAT_ID + '&parse_mode=MarkdownV2&disable_notification=' + notify + '&text=' + '\\\\' + msg
        if self.sendTelegramMsg == 'On':
            #requests.get(url, verify=telegramcert.cer)
            response = requests.get(send_msg,verify=False)
            print (response.text)
        else:
            print ('Telegram message is set to Off. To send msg toggle it to On')