#!/usr/bin/env python3
"""
双色球历史开奖数据爬取与更新脚本 (fetch_ssq_data.py)
支持中国福彩官方接口 (cwl.gov.cn) 抓取最新开奖记录并增量更新本地数据集。
"""

import os
import sys
import json
import time
import argparse
import datetime
import urllib.request
import urllib.error

OFFICIAL_API_URL = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ssq_history_500.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "http://www.cwl.gov.cn/ygfw/zq/ssq/",
    "X-Requested-With": "XMLHttpRequest"
}

def fetch_page_from_cwl(page_no=1, page_size=30):
    """从福彩网接口分页获取开奖数据"""
    params = f"?name=ssq&issueCount=&issueStart=&issueEnd=&dayStart=&dayEnd=&pageNo={page_no}&pageSize={page_size}&week=&systemType=PC"
    req = urllib.request.Request(OFFICIAL_API_URL + params, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("result", [])
    except Exception as e:
        print(f"[Warning] 请求接口第 {page_no} 页失败: {e}", file=sys.stderr)
        return None

def parse_record(item):
    """解析单条福彩返回的开奖记录"""
    # 典型返回字段: code(期号), date(日期), red(红球逗号分隔), blue(蓝球)
    issue = str(item.get("code", "")).strip()
    date_str = str(item.get("date", "")).split()[0].strip() # 提取YYYY-MM-DD
    red_str = item.get("red", "")
    blue_str = item.get("blue", "")
    
    red_list = [f"{int(x):02d}" for x in red_str.split(",") if x.strip()]
    red_list.sort()
    blue = f"{int(blue_str):02d}" if blue_str else "00"
    
    # 星期计算
    try:
        dt = datetime.date.fromisoformat(date_str)
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][dt.weekday()]
    except Exception:
        weekday = "未知"
        
    red_ints = [int(x) for x in red_list]
    red_sum = sum(red_ints)
    span = max(red_ints) - min(red_ints) if red_ints else 0
    odd_count = sum(1 for r in red_ints if r % 2 == 1)
    even_count = len(red_ints) - odd_count
    small_count = sum(1 for r in red_ints if r <= 16)
    big_count = len(red_ints) - small_count
    
    diffs = set()
    for x in range(len(red_ints)):
        for y in range(x + 1, len(red_ints)):
            diffs.add(red_ints[y] - red_ints[x])
    ac_val = len(diffs) - (len(red_ints) - 1) if len(red_ints) == 6 else 0
    
    return {
        "issue": issue,
        "date": date_str,
        "weekday": weekday,
        "red": red_list,
        "blue": blue,
        "sum": red_sum,
        "span": span,
        "ac": ac_val,
        "odd_even": f"{odd_count}:{even_count}",
        "big_small": f"{big_count}:{small_count}"
    }

def recalculate_omissions(records):
    """重新计算按时间升序排列的全量遗漏矩阵"""
    # records 必须按日期升序排列
    current_red_omissions = {r: 0 for r in range(1, 34)}
    current_blue_omissions = {b: 0 for r in range(1, 17)}
    
    for rec in records:
        red_set = set(int(x) for x in rec["red"])
        blue_val = int(rec["blue"])
        
        issue_red_om = {}
        for r in range(1, 34):
            if r in red_set:
                current_red_omissions[r] = 0
            else:
                current_red_omissions[r] += 1
            issue_red_om[f"{r:02d}"] = current_red_omissions[r]
            
        issue_blue_om = {}
        for b in range(1, 17):
            if b == blue_val:
                current_blue_omissions[b] = 0
            else:
                current_blue_omissions[b] += 1
            issue_blue_om[f"{b:02d}"] = current_blue_omissions[b]
            
        rec["red_omissions"] = issue_red_om
        rec["blue_omissions"] = issue_blue_om

def main():
    parser = argparse.ArgumentParser(description="双色球历史数据爬取与更新工具")
    parser.add_argument("--count", type=int, default=500, help="保留最近的期数，默认500期")
    parser.add_argument("--output", type=str, default=DEFAULT_DATA_PATH, help="输出JSON文件路径")
    parser.add_argument("--mock", action="store_true", help="若无外网则使用本地模拟生成模式")
    args = parser.parse_args()
    
    print(f"[*] 开始获取最近 {args.count} 期双色球开奖数据...")
    raw_results = []
    
    if not args.mock:
        page = 1
        page_size = 50
        while len(raw_results) < args.count:
            items = fetch_page_from_cwl(page_no=page, page_size=page_size)
            if not items:
                print(f"[!] 无法从网络获取更多数据 (可能离线或网络受限)。")
                break
            raw_results.extend(items)
            print(f" -> 已获取 {len(raw_results)} 条开奖记录...")
            if len(items) < page_size:
                break
            page += 1
            time.sleep(0.5)
            
    if len(raw_results) == 0:
        print("[*] 切换至本地数据集或内建备份检查...")
        if os.path.exists(args.output):
            print(f"[+] 本地数据文件已存在: {args.output}")
            sys.exit(0)
        else:
            print("[!] 本地无历史数据文件，请先运行 generate_data.py 生成基准 500 期数据。")
            sys.exit(1)
            
    # 解析并按期号升序排序
    parsed = [parse_record(item) for item in raw_results]
    parsed.sort(key=lambda x: x["issue"])
    
    # 截取最近 N 期
    if len(parsed) > args.count:
        parsed = parsed[-args.count:]
        
    recalculate_omissions(parsed)
    print(f"[+] 成功构建 {len(parsed)} 期双色球完整遗漏数据！")

if __name__ == "__main__":
    main()
