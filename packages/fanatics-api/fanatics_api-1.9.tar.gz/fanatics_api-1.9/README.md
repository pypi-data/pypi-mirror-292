# Fanatics API Data Fetcher

Fanatics API Data Fetcher is a Python tool designed to fetch data from the Fanatics API, retry failed requests, and convert the resulting JSON files into a CSV format.

## Features
- Fetch data based on a range of serial numbers.
- Retry failed serial number requests.
- Convert JSON files into a CSV file.

## Installation

```bash
pip install fanatics-api
```

## Usage

### Fetch Data
To fetch data for a range of serial numbers:

```bash
fanatics-api --fetch --start 1 --end 100 --prefix B --time-sleep 1.0
```

- `--start`: Start number for fetching data.
- `--end`: End number for fetching data.
- `--prefix`: Prefix letter for serial numbers (default is "B").
- `--time-sleep`: Time sleep duration between requests in seconds.

### Retry Failed Requests
To retry requests that failed previously:

```bash
fanatics-api --retry --failed-file failed.txt --time-sleep 1.0
```

- `--failed-file`: Path to the failed file (default is "failed.txt").
- `--time-sleep`: Time sleep duration between requests in seconds.

### Convert JSON Files to CSV
To convert all JSON files in the `data` directory to a CSV file:
```bash
fanatics-api --to-csv --output-csv output.csv
```

- `--output-csv`: Output CSV file name (default is "output.csv").

## Example
```bash
fanatics-api --fetch --start 1 --end 200 --prefix B --time-sleep 2
fanatics-api --retry --failed-file failed.txt --time-sleep 2
fanatics-api --to-csv --output-csv results.csv
```

## License

This project is licensed under the MIT License.


# Fanatics API 数据抓取工具

Fanatics API 数据抓取工具是一个 Python 工具，旨在从 Fanatics API 获取数据、重试失败的请求，并将生成的 JSON 文件转换为 CSV 格式。

## 功能
- 根据一系列序列号抓取数据。
- 重试失败的序列号请求。
- 将 JSON 文件转换为 CSV 文件。

## 安装

```bash
pip install fanatics-api
```

## 使用方法

### 抓取数据

抓取指定序列号范围内的数据:
```bash
fanatics-api --fetch --start 1 --end 100 --prefix B --time-sleep 1.0
```

- `--start`: 开始抓取数据的编号。
- `--end`: 结束抓取数据的编号。
- `--prefix`: 序列号的前缀字母（默认为 "B"）。
- `--time-sleep`: 每次请求之间的休眠时间，以秒为单位。

### 重试失败的请求
重试之前失败的请求:
```bash
fanatics-api --retry --failed-file failed.txt --time-sleep 1.0
```

- `--failed-file`: 失败文件的路径（默认为 "failed.txt"）。
- `--time-sleep`: 每次请求之间的休眠时间，以秒为单位。

### 将 JSON 文件转换为 CSV
将 `data` 目录中的所有 JSON 文件转换为一个 CSV 文件:
```bash
fanatics-api --to-csv --output-csv output.csv
```

- `--output-csv`: 输出 CSV 文件的名称（默认为 "output.csv"）。

## 示例
```bash
fanatics-api --fetch --start 1 --end 200 --prefix B --time-sleep 2
fanatics-api --retry --failed-file failed.txt --time-sleep 2
fanatics-api --to-csv --output-csv results.csv
```
## 许可证

本项目使用 MIT 许可证进行许可。