#!/usr/bin/env python3
"""
体彩超级大乐透历史开奖数据爬取与全自动更新引擎 (fetch_dlt_data.py)
从中国体育彩票官方接口 (sporttery.cn) 或网易/新浪彩票抓取最新 1000 期官方开奖数据，
自动重新计算全盘 35 前区号码与 12 后区号码的遗漏期数矩阵，并刷新 JSON、CSV 及静态 index.html / dlt.html。
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
import re

OFFICIAL_API_URL = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "dlt_history_1000.json")
DEFAULT_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "dlt_history_1000.csv")
DEFAULT_HTML_PATH = os.path.join(PROJECT_ROOT, "dlt.html")
INDEX_HTML_PATH = os.path.join(PROJECT_ROOT, "index.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://static.sporttery.cn/",
    "X-Requested-With": "XMLHttpRequest"
}

def fetch_page_from_sporttery(page_no=1, page_size=100):
    """从体彩网官方接口获取开奖数据"""
    url = f"{OFFICIAL_API_URL}?gameNo=85&provinceId=0&pageSize={page_size}&isVerify=1&pageNo={page_no}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                raw_bytes = response.read()
                data = json.loads(raw_bytes.decode("utf-8"))
                val = data.get("value", {})
                if isinstance(val, dict):
                    return val.get("list", [])
                elif isinstance(val, list):
                    return val
                return data.get("list", [])
    except Exception as e:
        print(f"[!] 请求体彩接口第 {page_no} 页出错: {e}", file=sys.stderr)
        return None

def parse_record(item):
    """解析单条体彩返回的开奖记录"""
    issue_raw = str(item.get("lotteryDrawNum", item.get("issue", item.get("code", "")))).strip()
    if len(issue_raw) == 5:
        issue = "20" + issue_raw
    else:
        issue = issue_raw
        
    date_str = str(item.get("lotteryDrawTime", item.get("date", ""))).split()[0].strip()
    
    # 号码提取
    res_str = str(item.get("lotteryDrawResult", item.get("result", ""))).strip()
    if res_str:
        tokens = [x for x in re.split(r'[,\s+]+', res_str) if x.strip()]
        if len(tokens) >= 7:
            front_list = [f"{int(x):02d}" for x in tokens[:5]]
            back_list = [f"{int(x):02d}" for x in tokens[5:7]]
        else:
            front_list = []
            back_list = []
    else:
        front_raw = item.get("front", item.get("red", []))
        back_raw = item.get("back", item.get("blue", []))
        if isinstance(front_raw, str):
            front_list = [f"{int(x):02d}" for x in re.split(r'[,\s+]+', front_raw) if x.strip()]
        else:
            front_list = [f"{int(x):02d}" for x in front_raw]
        if isinstance(back_raw, str):
            back_list = [f"{int(x):02d}" for x in re.split(r'[,\s+]+', back_raw) if x.strip()]
        else:
            back_list = [f"{int(x):02d}" for x in back_raw]
            
    front_list.sort()
    back_list.sort()
    
    try:
        dt = datetime.date.fromisoformat(date_str)
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][dt.weekday()]
    except Exception:
        weekday = "未知"
        
    front_ints = [int(x) for x in front_list]
    back_ints = [int(x) for x in back_list]
    
    front_sum = sum(front_ints)
    front_span = max(front_ints) - min(front_ints) if front_ints else 0
    odd_count = sum(1 for r in front_ints if r % 2 == 1)
    even_count = len(front_ints) - odd_count
    # 大小比：1-17为小，18-35为大
    small_count = sum(1 for r in front_ints if r <= 17)
    big_count = len(front_ints) - small_count
    
    diffs = set()
    for x in range(len(front_ints)):
        for y in range(x + 1, len(front_ints)):
            diffs.add(front_ints[y] - front_ints[x])
    ac_val = len(diffs) - (len(front_ints) - 1) if len(front_ints) == 5 else 0
    
    back_sum = sum(back_ints)
    back_span = max(back_ints) - min(back_ints) if back_ints else 0
    
    return {
        "issue": issue,
        "date": date_str,
        "weekday": weekday,
        "front": front_list,
        "back": back_list,
        "sum": front_sum,
        "span": front_span,
        "ac": ac_val,
        "odd_even": f"{odd_count}:{even_count}",
        "big_small": f"{big_count}:{small_count}",
        "back_sum": back_sum,
        "back_span": back_span
    }

def recalculate_omissions(records):
    """递推计算每期前区 1-35 与后区 1-12 的全量遗漏期数"""
    cur_front_om = {f: 0 for f in range(1, 36)}
    cur_back_om = {b: 0 for b in range(1, 13)}
    
    for rec in records:
        f_set = set(int(x) for x in rec["front"])
        b_set = set(int(x) for x in rec["back"])
        
        issue_f_om = {}
        for f in range(1, 36):
            if f in f_set:
                cur_front_om[f] = 0
            else:
                cur_front_om[f] += 1
            issue_f_om[f"{f:02d}"] = cur_front_om[f]
            
        issue_b_om = {}
        for b in range(1, 13):
            if b in b_set:
                cur_back_om[b] = 0
            else:
                cur_back_om[b] += 1
            issue_b_om[f"{b:02d}"] = cur_back_om[b]
            
        rec["front_omissions"] = issue_f_om
        rec["back_omissions"] = issue_b_om

def compute_statistics(history):
    n_issues = len(history)
    front_counts = {f"{f:02d}": 0 for f in range(1, 36)}
    back_counts = {f"{b:02d}": 0 for b in range(1, 13)}
    front_max_om = {f"{f:02d}": 0 for f in range(1, 36)}
    back_max_om = {f"{b:02d}": 0 for b in range(1, 13)}
    
    for rec in history:
        for f in rec["front"]:
            front_counts[f] += 1
        for b in rec["back"]:
            back_counts[b] += 1
        for f, om in rec["front_omissions"].items():
            if om > front_max_om[f]: front_max_om[f] = om
        for b, om in rec["back_omissions"].items():
            if om > back_max_om[b]: back_max_om[b] = om

    latest_rec = history[-1]
    
    front_stats = []
    # 35个球：前30%约为前11个(热)，中间40%为12-25(温)，后30%为26-35(冷)
    for rank, (num, cnt) in enumerate(sorted(front_counts.items(), key=lambda x: (-x[1], x[0])), start=1):
        cat = "热号" if rank <= 11 else ("温号" if rank <= 25 else "冷号")
        cat_code = "hot" if rank <= 11 else ("warm" if rank <= 25 else "cold")
        cur_om = latest_rec["front_omissions"][num]
        prob_pct = (cnt / n_issues) * 100 if n_issues > 0 else 0
        expected = n_issues * (5 / 35)
        bias = cnt - expected
        bias_pct = (bias / expected) * 100 if expected > 0 else 0
        
        front_stats.append({
            "rank": rank,
            "number": num,
            "category": cat,
            "category_code": cat_code,
            "frequency": cnt,
            "frequency_pct": round(prob_pct, 2),
            "current_omission": cur_om,
            "max_omission": front_max_om[num],
            "expected": round(expected, 1),
            "bias": round(bias, 1),
            "bias_pct": round(bias_pct, 2)
        })
        
    back_stats = []
    # 12个球：前4个(热)，中间4个(温)，后4个(冷)
    for rank, (num, cnt) in enumerate(sorted(back_counts.items(), key=lambda x: (-x[1], x[0])), start=1):
        cat = "热号" if rank <= 4 else ("温号" if rank <= 8 else "冷号")
        cat_code = "hot" if rank <= 4 else ("warm" if rank <= 8 else "cold")
        cur_om = latest_rec["back_omissions"][num]
        prob_pct = (cnt / n_issues) * 100 if n_issues > 0 else 0
        expected = n_issues * (2 / 12)
        bias = cnt - expected
        bias_pct = (bias / expected) * 100 if expected > 0 else 0
        
        back_stats.append({
            "rank": rank,
            "number": num,
            "category": cat,
            "category_code": cat_code,
            "frequency": cnt,
            "frequency_pct": round(prob_pct, 2),
            "current_omission": cur_om,
            "max_omission": back_max_om[num],
            "expected": round(expected, 1),
            "bias": round(bias, 1),
            "bias_pct": round(bias_pct, 2)
        })

    return {
        "total_issues": n_issues,
        "start_issue": history[0]["issue"],
        "end_issue": history[-1]["issue"],
        "start_date": history[0]["date"],
        "end_date": history[-1]["date"],
        "front_stats": front_stats,
        "back_stats": back_stats
    }

def update_html_dlt(history, html_path):
    """将最新的大乐透开奖数据替换入指定 HTML"""
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
            "f": [int(x) for x in h["front"]],
            "b": [int(x) for x in h["back"]],
            "s": h["sum"],
            "p": h["span"],
            "ac": h["ac"],
            "oe": h["odd_even"],
            "bs": h["big_small"],
            "bsum": h["back_sum"],
            "bspan": h["back_span"]
        })
    json_str = json.dumps(clean_history, separators=(',', ':'))
    
    # 替换 const RAW_DLT = [...]
    m = re.search(r'const RAW_DLT = \[.*?\];', content, re.DOTALL)
    if m:
        new_content = content[:m.start()] + f'const RAW_DLT = {json_str};' + content[m.end():]
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[+] 成功同步最新大乐透数据到 HTML 看板: {html_path}")

def main():
    parser = argparse.ArgumentParser(description="体彩超级大乐透历史开奖数据同步引擎")
    parser.add_argument("--count", type=int, default=1000, help="需要抓取的历史期数 (默认 1000 期)")
    parser.add_argument("--json", type=str, default=DEFAULT_JSON_PATH, help="输出 JSON 数据路径")
    parser.add_argument("--csv", type=str, default=DEFAULT_CSV_PATH, help="输出 CSV 数据路径")
    parser.add_argument("--html", type=str, default=DEFAULT_HTML_PATH, help="输出 HTML 看板路径")
    args = parser.parse_args()
    
    print(f"[*] 启动体彩大乐透数据同步程序 (目标期数: {args.count})...")
    
    raw_results = []
    page = 1
    page_size = 100
    
    while len(raw_results) < args.count:
        items = fetch_page_from_sporttery(page_no=page, page_size=page_size)
        if not items:
            print(f"[!] 无法继续从体彩接口获取第 {page} 页数据。")
            break
        raw_results.extend(items)
        print(f" -> 进度: 已获取 {len(raw_results)} 期记录...")
        if len(items) < page_size:
            break
        page += 1
        time.sleep(0.3)
        
    if len(raw_results) == 0:
        print("[*] 提示：当前环境无外网访问权限，尝试从现有数据初始化...")
        if os.path.exists(args.json):
            print(f"[+] 本地已有数据文件: {args.json}")
            with open(args.json, "r", encoding="utf-8") as f:
                d = json.load(f)
                parsed = d.get("history", [])
        elif os.path.exists(INDEX_HTML_PATH):
            print(f"[+] 从现有 index.html 提取基础 1000 期大乐透数据...")
            with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
                c = f.read()
            m = re.search(r'const RAW_DLT = (\[.*?\]);', c, re.DOTALL)
            if m:
                dlt_items = json.loads(m.group(1))
                parsed = []
                for item in dlt_items:
                    f_list = [f"{x:02d}" for x in item.get("f", item.get("primary", []))]
                    b_list = [f"{x:02d}" for x in item.get("b", item.get("secondary", []))]
                    parsed.append({
                        "issue": item["i"],
                        "date": item["d"],
                        "weekday": item["w"],
                        "front": f_list,
                        "back": b_list,
                        "sum": item.get("s", sum(int(x) for x in f_list)),
                        "span": item.get("p", max(int(x) for x in f_list) - min(int(x) for x in f_list)),
                        "ac": item.get("ac", 0),
                        "odd_even": item.get("oe", "3:2"),
                        "big_small": item.get("bs", "3:2"),
                        "back_sum": item.get("bsum", sum(int(x) for x in b_list)),
                        "back_span": item.get("bspan", max(int(x) for x in b_list) - min(int(x) for x in b_list))
                    })
            else:
                print("[!] 无法提取大乐透数据。", file=sys.stderr)
                sys.exit(1)
        else:
            print("[!] 未找到本地数据文件，请在有外网的环境下运行本脚本。", file=sys.stderr)
            sys.exit(1)
    else:
        # 解析并排序
        parsed = [parse_record(item) for item in raw_results if item]
        # 去重
        seen_issues = set()
        deduped = []
        for p in parsed:
            if p["issue"] and p["issue"] not in seen_issues and len(p["front"]) == 5:
                seen_issues.add(p["issue"])
                deduped.append(p)
        parsed = deduped
        parsed.sort(key=lambda x: x["issue"])
        
    if len(parsed) > args.count:
        parsed = parsed[-args.count:]
        
    recalculate_omissions(parsed)
    stats = compute_statistics(parsed)
    
    full_data = {
        "metadata": {
            "title": f"体彩超级大乐透最近{len(parsed)}期中奖号码与全量遗漏冷热统计数据",
            "total_issues": len(parsed),
            "date_range": f"{stats['start_date']} 至 {stats['end_date']}",
            "issue_range": f"{stats['start_issue']} 至 {stats['end_issue']}",
            "latest_issue": parsed[-1]["issue"],
            "latest_draw": f"前区: {' '.join(parsed[-1]['front'])} 后区: {' '.join(parsed[-1]['back'])}",
            "source": "中国体育彩票官方数据中心",
            "updated_at": datetime.datetime.now().isoformat()
        },
        "stats": stats,
        "history": parsed
    }
    
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)
    print(f"[+] 成功写入 JSON 数据集: {args.json} (共 {len(parsed)} 期)")
    
    csv_rows = []
    for rec in parsed:
        csv_rows.append({
            "期号": rec["issue"],
            "开奖日期": rec["date"],
            "星期": rec["weekday"],
            "前区1": rec["front"][0],
            "前区2": rec["front"][1],
            "前区3": rec["front"][2],
            "前区4": rec["front"][3],
            "前区5": rec["front"][4],
            "后区1": rec["back"][0],
            "后区2": rec["back"][1],
            "前区和值": rec["sum"],
            "前区跨度": rec["span"],
            "AC值": rec["ac"],
            "奇偶比": rec["odd_even"],
            "大小比": rec["big_small"],
            "后区和值": rec["back_sum"],
            "后区跨度": rec["back_span"]
        })
    with open(args.csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"[+] 成功写入 CSV 数据集: {args.csv}")
    
    update_html_dlt(parsed, args.html)
    update_html_dlt(parsed, INDEX_HTML_PATH)
    print(f"[✔] 大乐透全量数据与看板更新完毕！最新期号: {parsed[-1]['issue']} ({parsed[-1]['date']})")

if __name__ == "__main__":
    main()
