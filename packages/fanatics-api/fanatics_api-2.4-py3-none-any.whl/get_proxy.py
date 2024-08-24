from datetime import datetime, timedelta
import threading
import random
import time
import requests
import json


class IpCluster:
    def __init__(self, min_ip, proxyusernm):
        print("Init IpCluster with min_ip:", min_ip)
        self.ip_map = {}
        self.lock = threading.Lock()
        self.min_ip = min_ip
        self.proxyusernm = proxyusernm

    def __remove_expired_proxies(self):
        print("Remove expired proxies")
        """
        Remove proxies that have expired.
        """
        to_remove = []
        for ip, data in self.ip_map.items():
            data["ports"] = [p for p in data["ports"] if datetime.now() < p["expires"]]
            if len(data["ports"]) == 0:
                to_remove.append(ip)

        for ip in to_remove:
            del self.ip_map[ip]

    def get_proxy(self, force=False):
        """
        Always return a proxy with the oldest last_used time.
        """
        print("Get proxy")
        with self.lock:
            self.__remove_expired_proxies()
            i = 0
            while(self.__get_num_active_proxies() < self.min_ip or force):
                self.__add_proxy()
                print("Added new proxies, now have", self.__get_num_active_proxies(), "active proxies")
                time.sleep(1)
                i += 1
                if i > 3 and self.__get_num_active_proxies() != 0:
                    break
            oldest_ip = None
            oldest_port = None
            oldest_time = None
            for ip, data in self.ip_map.items():
                if data["deactivated_until"] is not None and datetime.now() < data["deactivated_until"]:
                    continue
                if oldest_time is None or data["last_used"] is None or data["last_used"] < oldest_time:
                    oldest_time = data["last_used"]
                    oldest_ip = ip
                    oldest_port = random.choice(data["ports"])["port"]
                    if data["last_used"] is None:
                        break
            if oldest_ip is not None:
                self.ip_map[oldest_ip]["last_used"] = datetime.now()
            proxyurl = f"http://{self.proxyusernm}:{self.proxyusernm}@{oldest_ip}:{oldest_port}"
            return {
                "http": proxyurl,
                "https": proxyurl
            }

    def remove_proxy(self, proxyurl):
        """
        Remove the proxy from the ip_map. If the IP has no more ports, remove the IP from the ip_map.
        """
        print("Remove proxy, proxyurl:", proxyurl)
        ip = proxyurl['http'].split('@')[1].split(':')[0]
        port = int(proxyurl['http'].split('@')[1].split(':')[1])
        with self.lock:
            if ip in self.ip_map:
                self.ip_map[ip]["ports"] = [p for p in self.ip_map[ip]["ports"] if p["port"] != port]
                if len(self.ip_map[ip]["ports"]) == 0:
                    del self.ip_map[ip]

    def __add_proxy(self):
        """
        Add proxies to the ip_map.
        """
        print("Add proxy")
        getText = 'getJSON'
        word = ''
        count = int(self.min_ip * 3)
        rand = "false"
        ltime = 0
        norepeat = "false"
        detail = "true"
        idshow = "false"
        url = f"http://{self.proxyusernm}.user.xiecaiyun.com/api/proxies?action={getText}&key=NP31A2C905&count={count}&word={word}&rand={rand}&norepeat={norepeat}&detail={detail}&ltime={ltime}&idshow={idshow}"

        i = 0
        while True:
            try:
                i += 1
                response = requests.get(url)
                data = json.loads(response.text).get("result")
                for item in data:
                    ip = item.get("ip")
                    port = item.get("port")
                    expires = datetime.fromtimestamp(item.get("ltime"))  # Convert to datetime object
                    if ip not in self.ip_map:
                        self.ip_map[ip] = {"ports": [], "last_used": None, "deactivated_until": None}
                    self.ip_map[ip]["ports"].append({"port": port, "expires": expires})
                break
            except Exception as e:
                print("Fetch or parse proxy error:", e)
                time.sleep(1)
                if i > 30:
                    exit("Fetch proxy error")

    def deactivate_proxy(self, proxyurl):
        """
        Deactivate the proxy with the IP. It will be activated again after 1 minute.
        """
        print("Deactivate proxy, proxyurl:", proxyurl)
        with self.lock:
            ip = proxyurl['http'].split('@')[1].split(':')[0]
            if ip in self.ip_map:
                self.ip_map[ip]["deactivated_until"] = datetime.now() + timedelta(minutes=1)
                print(f"Deactivated {ip} until {self.ip_map[ip]['deactivated_until']}")

    def __get_num_active_proxies(self):
        """
        Return the number of active proxies.
        """
        i = 0
        for ip, data in self.ip_map.items():
            if data["deactivated_until"] is None or datetime.now() > data["deactivated_until"]:
                i += 1
        return i
    
    def get_ip_list(self):
        """
        Return the list of active IPs.
        """
        return [ip for ip, data in self.ip_map.items() if data["deactivated_until"] is None or datetime.now() > data["deactivated_until"]]