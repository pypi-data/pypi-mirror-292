#get the access token"
import requests
import sys

def get_access():
   a = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wweb64ffbfdd8bb120&corpsecret=Bl6QdD-rFhQ_QfeFf_s1Dd1_g4arHAqF4EjZvNmqLPY")
   access_token = eval(a.text)["access_token"]
   return access_token

def send_message(token,message):
   url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + token
   paras = {
   "touser" : "TuDou",
   "agentid" : 1000002,
   "msgtype": "text",
   "text" : {
       "content" : "你的快递已到，请携带工卡前往邮件中心领取。\n出发前可查看<a href=\"http://work.weixin.qq.com\">邮件中心视频实况</a>，聪明避开排队。"
   },
   "safe":0,
   "enable_id_trans": 0,
   "enable_duplicate_check": 0,
   "duplicate_check_interval": 1800
   }

   paras["text"].update({"content": message})
   results = requests.post(url,json=paras)
   return results.status_code

if __name__ == "__main__":
   message = sys.argv[1]
   send_message(get_access(),message)
