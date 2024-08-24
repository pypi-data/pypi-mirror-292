getText = 'getJSON'
word = ''
count = 5
rand = "false"
ltime = 0
norepeat = "false"
detail = "true"
idshow = "false"
proxyusernm = "17610808180"
proxypasswd = "17610808180"


class Response:
    text: str

class IpRecord:
    ip: str
    port: int
    ltime: int
    used: int


import requests
import json
import time
import threading


list = list()
list_lock = threading.Lock()
def get_proxy(proxyusernm, proxypasswd,force=False):
    proxyusernm = proxyusernm
    proxypasswd = proxypasswd
    url = f"http://{proxyusernm}.user.xiecaiyun.com/api/proxies?action={getText}&key=NP31A2C905&count={count}&word={word}&rand={rand}&norepeat={norepeat}&detail={detail}&ltime={ltime}&idshow={idshow}"

    with list_lock: 
        # remove all expired proxies
        for item in list:
            if(item.ltime < time.time()):
                print("remove expired proxy: ", item.ip)
                list.remove(item)
        if(len(list) < 80 or force):
            print("fetch new proxies")
            while(True):
                try:
                    response = requests.get(url)
                except Exception as e:
                    print("fetch proxy error: ", e)
                # response.text = '{"success":true,"result":[{"ip":"182.207.100.12","port":58103,"rip":"223.12.170.48","artx":"中国-山西-太原--电信","ftime":1723802169,"ltime":1723802469},{"ip":"182.207.100.35","port":58150,"rip":"223.150.173.201","artx":"中国-湖南-常德--电信","ftime":1723802158,"ltime":1723802458}]}'
                try:
                    data = json.loads(response.text).get("result")
                    break
                except Exception as e:
                    print("parse proxy error: ", e)
                    time.sleep(1)
                
            for item in data:
                record = IpRecord()
                record.ip = item.get("ip")
                record.port = item.get("port")
                record.ltime = item.get("ltime")
                record.used = 0
                list.append(record)
        list.sort(key=lambda x: x.used)
        if(len(list) == 0):
            return exit("no proxy available")
        list[0].used += 1
        proxyurl="http://"+proxyusernm+":"+proxypasswd+"@"+list[0].ip+":"+str(list[0].port)
        return {
            "http": proxyurl,
            "https": proxyurl
        }









