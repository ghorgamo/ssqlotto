#!/usr/bin/env python3
"""
双色球历史开奖数据爬取与全自动更新引擎 (fetch_ssq_data.py)
从中国福利彩票官方接口 (cwl.gov.cn) 或网易/中彩网抓取真实最新500期数据，
自动重新计算全盘33红球与16蓝球的遗漏期数矩阵，并刷新 JSON、CSV 及静态 index.html。
"""

import os
import sys
import json
import time
import argparse
import datetime
import urllib.request
import urllib.error
import csv

OFFICIAL_API_URL = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "ssq_history_1000.json")
DEFAULT_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "ssq_history_1000.csv")
DEFAULT_HTML_PATH = os.path.join(PROJECT_ROOT, "index.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "http://www.cwl.gov.cn/ygfw/zq/ssq/",
    "X-Requested-With": "XMLHttpRequest"
}

def fetch_page_from_cwl(page_no=1, page_size=50):
    """从福彩网官方接口获取开奖数据"""
    params = f"?name=ssq&issueCount=&issueStart=&issueEnd=&dayStart=&dayEnd=&pageNo={page_no}&pageSize={page_size}&week=&systemType=PC"
    req = urllib.request.Request(OFFICIAL_API_URL + params, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                raw_bytes = response.read()
                data = json.loads(raw_bytes.decode("utf-8"))
                return data.get("result", [])
    except Exception as e:
        print(f"[!] 请求福彩接口第 {page_no} 页出错: {e}", file=sys.stderr)
        return None

def parse_record(item):
    """解析单条福彩返回的开奖记录"""
    issue = str(item.get("code", "")).strip()
    date_str = str(item.get("date", "")).split()[0].strip()
    red_str = item.get("red", "")
    blue_str = item.get("blue", "")
    
    red_list = [f"{int(x):02d}" for x in red_str.split(",") if x.strip()]
    red_list.sort()
    blue = f"{int(blue_str):02d}" if blue_str else "00"
    
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
    """严格按时间顺序递推计算每期每个号码的遗漏期数"""
    current_red_omissions = {r: 0 for r in range(1, 34)}
    current_blue_omissions = {b: 0 for b in range(1, 17)}
    
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

def compute_statistics(history):
    n_issues = len(history)
    red_counts = {f"{r:02d}": 0 for r in range(1, 34)}
    blue_counts = {f"{b:02d}": 0 for b in range(1, 17)}
    red_max_om = {f"{r:02d}": 0 for r in range(1, 34)}
    blue_max_om = {f"{b:02d}": 0 for b in range(1, 17)}
    
    for rec in history:
        for r in rec["red"]:
            red_counts[r] += 1
        blue_counts[rec["blue"]] += 1
        for r, om in rec["red_omissions"].items():
            if om > red_max_om[r]: red_max_om[r] = om
        for b, om in rec["blue_omissions"].items():
            if om > blue_max_om[b]: blue_max_om[b] = om

    latest_rec = history[-1]
    
    red_stats = []
    for rank, (num, cnt) in enumerate(sorted(red_counts.items(), key=lambda x: (-x[1], x[0])), start=1):
        cat = "热号" if rank <= 10 else ("温号" if rank <= 23 else "冷号")
        cat_code = "hot" if rank <= 10 else ("warm" if rank <= 23 else "cold")
        cur_om = latest_rec["red_omissions"][num]
        max_om = red_max_om[num]
        avg_om = round(n_issues / cnt, 1) if cnt > 0 else n_issues
        theory_diff = cnt - round(n_issues * 6 / 33, 1)
        red_stats.append({
            "rank": rank,
            "number": num,
            "count": cnt,
            "frequency_percent": round(cnt / n_issues * 100, 2),
            "current_omission": cur_om,
            "max_omission": max_om,
            "avg_omission": avg_om,
            "theory_diff": round(theory_diff, 1),
            "category": cat,
            "category_code": cat_code
        })
        
    blue_stats = []
    for rank, (num, cnt) in enumerate(sorted(blue_counts.items(), key=lambda x: (-x[1], x[0])), start=1):
        cat = "热号" if rank <= 5 else ("温号" if rank <= 11 else "冷号")
        cat_code = "hot" if rank <= 5 else ("warm" if rank <= 11 else "cold")
        cur_om = latest_rec["blue_omissions"][num]
        max_om = blue_max_om[num]
        avg_om = round(n_issues / cnt, 1) if cnt > 0 else n_issues
        theory_diff = cnt - round(n_issues / 16, 1)
        blue_stats.append({
            "rank": rank,
            "number": num,
            "count": cnt,
            "frequency_percent": round(cnt / n_issues * 100, 2),
            "current_omission": cur_om,
            "max_omission": max_om,
            "avg_omission": avg_om,
            "theory_diff": round(theory_diff, 1),
            "category": cat,
            "category_code": cat_code
        })
        
    return {
        "n_issues": n_issues,
        "start_issue": history[0]["issue"],
        "end_issue": history[-1]["issue"],
        "start_date": history[0]["date"],
        "end_date": history[-1]["date"],
        "red_stats": red_stats,
        "blue_stats": blue_stats
    }

def update_html_with_history(history, html_path=DEFAULT_HTML_PATH):
    if not os.path.exists(html_path):
        return
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    clean_history = []
    for h in history:
        clean_history.append({
            "i": h["issue"],
            "d": h["date"],
            "w": h["weekday"],
            "r": [int(x) for x in h["red"]],
            "b": int(h["blue"]),
            "s": h["sum"],
            "p": h["span"],
            "ac": h["ac"],
            "oe": h["odd_even"],
            "bs": h["big_small"]
        })
    json_str = json.dumps(clean_history, separators=(',', ':'))
    
    # 查找并替换 RAW_HISTORY = [...]
    start_tag = "const RAW_HISTORY = "
    end_tag = ";\n    let filteredHistory"
    start_pos = content.find(start_tag)
    if start_pos != -1:
        end_pos = content.find(end_tag, start_pos)
        if end_pos != -1:
            new_content = content[:start_pos + len(start_tag)] + json_str + content[end_pos:]
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[+] 静态前端 {html_path} 数据已同步更新！")

def main():
    parser = argparse.ArgumentParser(description="双色球官方真实历史数据拉取与更新工具")
    parser.add_argument("--count", type=int, default=1000, help="保留最近的期数，默认500期")
    parser.add_argument("--json", type=str, default=DEFAULT_JSON_PATH, help="输出JSON文件路径")
    parser.add_argument("--csv", type=str, default=DEFAULT_CSV_PATH, help="输出CSV文件路径")
    parser.add_argument("--html", type=str, default=DEFAULT_HTML_PATH, help="输出HTML文件路径")
    args = parser.parse_args()
    
    print(f"[*] 开始连接中国福彩官方 API 检索最近 {args.count} 期真实开奖数据...")
    raw_results = []
    page = 1
    page_size = 50
    
    while len(raw_results) < args.count:
        items = fetch_page_from_cwl(page_no=page, page_size=page_size)
        if not items:
            print(f"[!] 无法继续从福彩接口获取更多数据。")
            break
        raw_results.extend(items)
        print(f" -> 进度: 已获取 {len(raw_results)} 期记录...")
        if len(items) < page_size:
            break
        page += 1
        time.sleep(0.3)
        
    if len(raw_results) == 0:
        print("[*] 提示：当前环境无外网访问权限，检查本地已有数据...")
        if os.path.exists(args.json):
            print(f"[+] 本地已有数据文件: {args.json}")
            sys.exit(0)
        else:
            print("[!] 未找到本地数据文件，请在有外网的环境下运行本脚本。")
            sys.exit(1)
            
    # 解析并按期号升序排序
    parsed = [parse_record(item) for item in raw_results]
    parsed.sort(key=lambda x: x["issue"])
    
    if len(parsed) > args.count:
        parsed = parsed[-args.count:]
        
    recalculate_omissions(parsed)
    stats = compute_statistics(parsed)
    
    full_data = {
        "metadata": {
            "title": "双色球最近500期中奖号码与全量遗漏冷热统计数据",
            "total_issues": len(parsed),
            "date_range": f"{stats['start_date']} 至 {stats['end_date']}",
            "issue_range": f"{stats['start_issue']} 至 {stats['end_issue']}",
            "latest_issue": parsed[-1]["issue"],
            "latest_draw": f"红球: {' '.join(parsed[-1]['red'])} 蓝球: {parsed[-1]['blue']}",
            "source": "中国福利彩票官方数据中心",
            "updated_at": datetime.datetime.now().isoformat()
        },
        "stats": stats,
        "history": parsed
    }
    
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)
    print(f"[+] 成功写入 JSON 数据集: {args.json} (共 {len(parsed)} 期)")
    
    csv_rows = []
    for rec in parsed:
        csv_rows.append({
            "期号": rec["issue"],
            "开奖日期": rec["date"],
            "星期": rec["weekday"],
            "红球1": rec["red"][0],
            "红球2": rec["red"][1],
            "红球3": rec["red"][2],
            "红球4": rec["red"][3],
            "红球5": rec["red"][4],
            "红球6": rec["red"][5],
            "蓝球": rec["blue"],
            "和值": rec["sum"],
            "跨度": rec["span"],
            "AC值": rec["ac"],
            "奇偶比": rec["odd_even"],
            "大小比": rec["big_small"]
        })
    with open(args.csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"[+] 成功写入 CSV 数据集: {args.csv}")
    
    update_html_with_history(parsed, args.html)
    dlt_html_path = os.path.join(PROJECT_ROOT, "dlt.html")
    if os.path.exists(dlt_html_path):
        update_html_with_history(parsed, dlt_html_path)
    
    # 500期兼容备份
    if len(parsed) >= 500:
        backup_json = os.path.join(PROJECT_ROOT, "data", "ssq_history_500.json")
        backup_csv = os.path.join(PROJECT_ROOT, "data", "ssq_history_500.csv")
        sub_500 = parsed[-500:]
        with open(backup_json, "w", encoding="utf-8") as f:
            json.dump({"metadata": full_data["metadata"], "stats": compute_statistics(sub_500), "history": sub_500}, f, ensure_ascii=False, indent=2)
        with open(backup_csv, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows[-500:])
    print(f"[✔] 全量数据与看板更新完毕！最新期号: {parsed[-1]['issue']} ({parsed[-1]['date']})")

if __name__ == "__main__":
    main()
