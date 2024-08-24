import os
import requests
import time
import json
import csv
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from requests.exceptions import ProxyError, RequestException
from requests.exceptions import SSLError
from http.client import RemoteDisconnected

last_file_num = 0

class Response:
    text: str

class IpRecord:
    ip: str
    port: int
    ltime: int
    used: int

    def __str__(self) -> str:
        return f"{self.ip}:{self.port}, used: {self.used}"
    
    def __repr__(self) -> str:
        return f"{self.ip}:{self.port}, used: {self.used}"


list = list()
list_lock = threading.Lock()

def remove_proxy(proxyurl):
    with list_lock:
        try:
            ip = proxyurl['http'].split('@')[1].split(':')[0]
            port = int(proxyurl['http'].split('@')[1].split(':')[1])
            for item in list:
                if(item.ip == ip and item.port == port):
                    list.remove(item)
                    print("remove proxy: ", ip)
                    break
        except Exception as e:
            print("Remove proxy error:", e)

def get_proxy(proxyusernm, proxypasswd, force=False, proxyNum=40):
    getText = 'getJSON'
    word = ''
    count = 5
    rand = "false"
    ltime = 0
    norepeat = "false"
    detail = "true"
    idshow = "false"
    url = f"http://{proxyusernm}.user.xiecaiyun.com/api/proxies?action={getText}&key=NP31A2C905&count={count}&word={word}&rand={rand}&norepeat={norepeat}&detail={detail}&ltime={ltime}&idshow={idshow}"

    with list_lock:
        # Remove all expired proxies
        list[:] = [item for item in list if item.ltime >= time.time()]

        if len(list) < proxyNum * 1.5 or force:
            print("Fetching new proxies")
            i = 0
            while True:
                try:
                    i += 1
                    response = requests.get(url)
                    data = json.loads(response.text).get("result")
                    break
                    
                except Exception as e:
                    print("Fetch or parse proxy error:", e)
                    time.sleep(1)
                    if(i > 30):
                        exit("Fetch proxy error")
                
            for item in data:
                record = IpRecord()
                record.ip = item.get("ip")
                record.port = item.get("port")
                record.ltime = item.get("ltime")
                record.used = 0
                list.append(record)

        # Sort the list by `used` count
        list.sort(key=lambda x: x.used)

        if len(list) == 0:
            exit("No proxy available")

        # Get the IP of the proxy with the smallest `used` count
        selected_ip = list[0].ip

        # Increment the `used` count for all proxies with the same IP
        for item in list:
            if item.ip == selected_ip:
                item.used += 1

        proxyurl = f"http://{proxyusernm}:{proxypasswd}@{selected_ip}:{list[0].port}"
        return {
            "http": proxyurl,
            "https": proxyurl
        }



def fetch_single_data(serialNumber, url, headers, failed_file, time_sleep, password, workerNum):

    proxy = get_proxy(password, password, proxyNum=workerNum * 2)
    i = 0
    while proxy:
        payload = {
            "serialNumber": serialNumber,
            "vc": "",
            "use24carat": "true"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, proxies=proxy)
        except Exception as e:
            print(f"Request Exception with proxy {proxy}: {e}")
            with open(failed_file, "a") as file:
                file.write(f"{serialNumber} Request Exception: {e}\n")
            i+=1
            print(f"Retry {i} times")
            
            # Get a new proxy and retry
            if i > 3:
                print(f"Retry {i} times, force to get a new proxy")
                i = 0
                proxy = get_proxy(password, password, force=True, proxyNum=workerNum * 2)
            else:
                print(f"Retry {i} times, get a new proxy")
                proxy = get_proxy(password, password, proxyNum=workerNum * 2)
            continue

        time.sleep(time_sleep)

        if response.status_code == 200:
            print(f"Serial Number: {serialNumber}")
            with open(f"data/{serialNumber}.json", "w") as file:
                file.write(response.text)
            break
        if response.status_code == 429:
            remove_proxy(proxy)
            time.sleep(5)
            continue
        else:
            with open(failed_file, "a") as file:
                file.write(f"{serialNumber} {response.status_code} {response.text}\n")
            continue

def fetch_data(prefix, begin, end, failed_file, time_sleep, max_workers, password):
    url = "https://www.fanatics.com/api/authenticity-verification/validate"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.fanatics.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    }

    

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(begin, end):
            serialNumber = prefix + str(i).zfill(6)
            if os.path.exists(f"data/{serialNumber}.json"):
                continue
            futures.append(executor.submit(fetch_single_data, serialNumber, url, headers, failed_file, time_sleep, password, max_workers))
        # Start a monitoring thread
        def monitor():
            while any(future.running() for future in futures):
                # get the number of files created speed
                new_file_num = os.listdir("data").__len__()
                global last_file_num
                speed = (new_file_num - last_file_num) * 2
                last_file_num = new_file_num
                print(f"Speed: {speed} files/min")
                alive_count = sum(future.running() for future in futures)
                print(f"Currently {alive_count} workers are alive.")
                time.sleep(30)

        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Generated an exception: {exc}")
        monitor_thread.join()

def retry_single_data(serialNumber, url, headers, failed_file, time_sleep, workerNum, password):
    proxy = get_proxy(password, password, proxyNum=workerNum * 2)

    while proxy:
        payload = {
            "serialNumber": serialNumber,
            "vc": "",
            "use24carat": "true"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, proxies=proxy)
        except requests.exceptions.RequestException as e:
            print(f"Retry Request Exception with proxy {proxy}: {e}")
            proxy = get_proxy(password, password, proxyNum=workerNum * 2)
            continue

        time.sleep(time_sleep)

        if response.status_code == 200:
            print(f"Retry Successful for: {serialNumber}")
            with open(f"data/{serialNumber}.json", "a") as file:
                file.write(response.text)
            return True
        else:
            return False


def retry_failed(failed_file, time_sleep, max_workers, password):
    url = "https://www.fanatics.com/api/authenticity-verification/validate"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.fanatics.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    }

    with open(failed_file, "r") as file:
        lines = file.readlines()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(retry_single_data, line.split(" ")[0], url, headers, failed_file, time_sleep, max_workers, password): line for line in lines}

        for future in as_completed(futures):
            line = futures[future]
            try:
                success = future.result()
                if success:
                    lines.remove(line)
            except Exception as exc:
                print(f"Retry failed with exception: {exc}")

    # Update the failed file
    with open(failed_file, "w") as file:
        file.writelines(lines)


def json_to_csv(output_csv):
    fieldnames = ["HologramID", "SignedBy", "productDescription", "Inscription", "LimitedEdition", "valid"]
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for filename in os.listdir("data"):
            if filename.endswith(".json"):
                HologramID = filename.split(".")[0]
                with open(f"data/{filename}", "r") as file:
                    data = json.load(file)
                    athletes = data.get("athletes", [])
                    if(athletes is None):
                        athletes = []
                    writer.writerow({
                        "HologramID": HologramID,
                        "SignedBy": "，".join(athletes),
                        "productDescription": data.get("productDescription", "").replace(",", "，"),
                        "Inscription": data.get("Inscription", "").replace(",", "，"),
                        "LimitedEdition": data.get("LE", "").replace(",", "，"),
                        "valid": data.get("valid", "")
                    })

def main():
    parser = argparse.ArgumentParser(
        description="Fanatics API Data Fetcher (Fanatics API 数据抓取工具)"
    )
    parser.add_argument(
        "--start", 
        type=int, 
        help="Start number for fetching data (开始抓取数据的编号)"
    )
    parser.add_argument(
        "--end", 
        type=int, 
        help="End number for fetching data (结束抓取数据的编号)"
    )
    parser.add_argument(
        "--prefix", 
        type=str, 
        default="B", 
        help="Prefix letter for serial numbers (序列号的前缀字母)"
    )
    parser.add_argument(
        "--failed-file", 
        type=str, 
        default="failed.txt", 
        help="Path to the failed file (失败文件的路径)"
    )
    parser.add_argument(
        "--time-sleep", 
        type=float, 
        default=1.0, 
        help="Time sleep duration between requests (每次请求之间的休眠时间, 单位：秒)"
    )
    parser.add_argument(
        "--max-workers", 
        type=int, 
        default=5, 
        help="Number of threads to use for fetching data (用于抓取数据的线程数)"
    )
    parser.add_argument(
        "--fetch", 
        action="store_true", 
        help="Fetch data based on start and end range (根据起始和结束范围抓取数据)"
    )
    parser.add_argument(
        "--retry", 
        action="store_true", 
        help="Retry failed serial numbers (重试失败的序列号)"
    )
    parser.add_argument(
        "--to-csv", 
        action="store_true", 
        help="Convert JSON files to CSV (将JSON文件转换为CSV)"
    )
    parser.add_argument(
        "--output-csv", 
        type=str, 
        default="output.csv", 
        help="Output CSV file name (输出CSV文件的名称)"
    )

    args = parser.parse_args()

    print("You are asked to provide the password to continue. (您被要求提供协采云密码以继续。)")
    password = input("Password: ")

    if args.fetch:
        if args.start is not None and args.end is not None:
            if(not os.path.exists("data")):
                os.makedirs("data")
            fetch_data(args.prefix, args.start, args.end + 1, args.failed_file, args.time_sleep, args.max_workers, password)
        else:
            print("Please provide both --start and --end arguments for fetching data. (请提供用于抓取数据的--start和--end参数。)")

    if args.retry:
        retry_failed(args.failed_file, args.time_sleep, args.max_workers, password)

    if args.to_csv:
        json_to_csv(args.output_csv)

if __name__ == "__main__":
    main()