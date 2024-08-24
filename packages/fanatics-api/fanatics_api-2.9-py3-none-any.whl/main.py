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
from get_proxy import IpCluster
from json_to_excel import json_to_excel, json_to_csv

last_file_num = 0


class Response:
    text: str






def fetch_single_data(serialNumber, url, headers, failed_file, time_sleep, ipCluster):

    proxy = ipCluster.get_proxy()
    i = 0
    while proxy:
        payload = {
            "serialNumber": serialNumber,
            "vc": "",
            "use24carat": "true"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, proxies=proxy, timeout=2)
        except Exception as e:
            print(f"Request Exception with proxy {proxy}: {e}")
            with open(failed_file, "a") as file:
                file.write(f"{serialNumber} Request Exception: {e}\n")
            i+=1
            print(f"Retry {i} times, delete the proxy because of exception")
            ipCluster.remove_proxy(proxy)
            
            # Get a new proxy and retry
            if i > 3:
                print(f"Retry {i} times, force to get a new proxy")
                i = 0
                proxy = ipCluster.get_proxy(force=True)
            else:
                print(f"Retry {i} times, get a new proxy")
                proxy = ipCluster.get_proxy()
            continue

        time.sleep(time_sleep)

        if response.status_code == 200:
            print(f"Serial Number: {serialNumber}")
            with open(f"data/{serialNumber}.json", "w") as file:
                file.write(response.text)
            break
        if response.status_code == 429:
            ipCluster.deactivate_proxy(proxy)
            print(f"429 Error: {serialNumber}")
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

    ipCluster = IpCluster(max_workers, password)


    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(begin, end):
            serialNumber = prefix + str(i).zfill(6)
            if os.path.exists(f"data/{serialNumber}.json"):
                continue
            futures.append(executor.submit(fetch_single_data, serialNumber, url, headers, failed_file, time_sleep, ipCluster))
        # Start a monitoring thread
        def monitor():
            while any(future.running() for future in futures):
                # get the number of files created speed
                new_file_num = os.listdir("data").__len__()
                global last_file_num
                speed = (new_file_num - last_file_num) * 2
                last_file_num = new_file_num
                print(f"--------------------------Speed: {speed} files/min----------------------")
                # how many ip are alive
                print(f"---------------------Currently {ipCluster.get_ip_list().__len__()} proxies are alive.---------------")
                # print ip lists
                print(f"---------------------Currently {ipCluster.get_ip_list()} proxies are alive.---------------")

                alive_count = sum(future.running() for future in futures)
                print(f"-------------Currently {alive_count} workers are alive.-----------------")

                time.sleep(30)

        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Generated an exception: {exc}")
        monitor_thread.join()

def retry_single_data(serialNumber, url, headers, failed_file, time_sleep, ipCluster):
    proxy = ipCluster.get_proxy()

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
            ipCluster.remove_proxy(proxy)
            proxy = ipCluster.get_proxy()
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

    IpCluster = IpCluster(2*max_workers, password)

    with open(failed_file, "r") as file:
        lines = file.readlines()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(retry_single_data, line.split(" ")[0], url, headers, failed_file, time_sleep, IpCluster): line for line in lines}

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
        default="", 
        help="Output CSV file name (输出CSV文件的名称)"
    )
    parser.add_argument(
        "--to-excel",
        action="store_true",
        help="Convert JSON files to Excel (将JSON文件转换为Excel)"
    )
    parser.add_argument(
        "--output-excel",
        type=str,
        default="",
        help="Output Excel file name (输出Excel文件的名称)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory to store JSON files (存储JSON文件的目录)"
    )


    args = parser.parse_args()

    # print("You are asked to provide the password to continue. (您被要求提供协采云密码以继续。)")
    # password = input("Password: ")
    password = "17610808180"

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
        if(args.start is None or args.end is None):
            print("Please provide both --start and --end arguments for converting JSON to Excel. (请提供用于将JSON转换为Excel的--start和--end参数。)")
        elif not os.path.exists(args.data_dir):
            print("The data directory does not exist. Please provide a valid data directory. (数据目录不存在。请提供有效的数据目录。)")
        else:
            json_to_csv(args.start, args.end, args.prefix, args.output_csv, args.data_dir)


    if args.to_excel:
        if(args.start is None or args.end is None):
            print("Please provide both --start and --end arguments for converting JSON to Excel. (请提供用于将JSON转换为Excel的--start和--end参数。)")
        elif not os.path.exists(args.data_dir):
            print("The data directory does not exist. Please provide a valid data directory. (数据目录不存在。请提供有效的数据目录。)")
        else:
            json_to_excel(args.start, args.end, args.prefix, args.output_excel, args.data_dir)

if __name__ == "__main__":
    main()