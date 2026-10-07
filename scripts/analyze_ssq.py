#!/usr/bin/env python3
"""
双色球多维走势与冷热统计分析引擎 (analyze_ssq.py)
支持分析最近 1000 期 (或任意指定期数) 开奖数据，
输出红蓝球出球次数排名、理论期望偏离度、当前遗漏期数、历史最大遗漏与冷热温分类报告。
"""

import os
import sys
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "ssq_history_1000.json")
BACKUP_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "ssq_history_500.json")

def load_data(filepath=None):
    if filepath and os.path.exists(filepath):
        target = filepath
    elif os.path.exists(DEFAULT_JSON_PATH):
        target = DEFAULT_JSON_PATH
    elif os.path.exists(BACKUP_JSON_PATH):
        target = BACKUP_JSON_PATH
    else:
        print(f"[Error] 未找到数据文件: {DEFAULT_JSON_PATH}", file=sys.stderr)
        sys.exit(1)
        
    with open(target, "r", encoding="utf-8") as f:
        return json.load(f)

def print_header(title):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)

def analyze(data, window_size=None):
    metadata = data.get("metadata", {})
    history = data.get("history", [])
    total_len = len(history)
    
    if window_size is None or window_size > total_len:
        window_size = total_len
        
    sub_history = history[-window_size:]
    latest = sub_history[-1]
    
    print_header(f"🎱 双色球最近 {window_size} 期大数据多维统计报告")
    print(f"数据总跨度: {sub_history[0]['issue']} ({sub_history[0]['date']}) 至 {latest['issue']} ({latest['date']})")
    print(f"最新开奖: 第 {latest['issue']} 期 ({latest['date']} {latest['weekday']})")
    print(f"中奖号码: 红球 [{', '.join(latest['red'])}] + 蓝球 [{latest['blue']}]")
    print(f"形态指标: 和值={latest['sum']} | 跨度={latest['span']} | AC值={latest['ac']} | 奇偶={latest['odd_even']} | 大小={latest['big_small']}")
    
    # 统计出球次数与遗漏
    red_counts = {f"{r:02d}": 0 for r in range(1, 34)}
    blue_counts = {f"{b:02d}": 0 for b in range(1, 17)}
    red_max_om = {f"{r:02d}": 0 for r in range(1, 34)}
    blue_max_om = {f"{b:02d}": 0 for b in range(1, 17)}
    
    for rec in sub_history:
        for r in rec["red"]:
            red_counts[r] += 1
        blue_counts[rec["blue"]] += 1
        for r, om in rec.get("red_omissions", {}).items():
            if om > red_max_om[r]: red_max_om[r] = om
        for b, om in rec.get("blue_omissions", {}).items():
            if om > blue_max_om[b]: blue_max_om[b] = om
            
    theory_red = round(window_size * 6 / 33, 1)
    theory_blue = round(window_size / 16, 1)
    
    # 打印红球排名
    print_header(f"🔴 红球 1-33 出球数降序排名与冷/热/温分类 (理论期望: {theory_red}次)")
    print(f"{'排名':<4}{'号码':<6}{'出球次数':<10}{'出球率':<10}{'理论偏差':<10}{'当前遗漏':<10}{'最大遗漏':<10}{'状态分类':<8}")
    print("-" * 72)
    
    sorted_reds = sorted(red_counts.items(), key=lambda x: (-x[1], x[0]))
    for rank, (num, cnt) in enumerate(sorted_reds, start=1):
        cur_om = latest.get("red_omissions", {}).get(num, 0)
        max_om = red_max_om[num]
        freq = round(cnt / window_size * 100, 2)
        diff = round(cnt - theory_red, 1)
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        
        if rank <= 10:
            badge = "🔥 热号"
        elif rank <= 23:
            badge = "🌤️ 温号"
        else:
            badge = "❄️ 冷号"
            
        print(f"{rank:<4}{num:<6}{cnt:<10}{str(freq)+'%':<10}{diff_str:<10}{cur_om:<10}{max_om:<10}{badge:<8}")
        
    # 打印蓝球排名
    print_header(f"🔵 蓝球 1-16 出球数降序排名与冷/热/温分类 (理论期望: {theory_blue}次)")
    print(f"{'排名':<4}{'号码':<6}{'出球次数':<10}{'出球率':<10}{'理论偏差':<10}{'当前遗漏':<10}{'最大遗漏':<10}{'状态分类':<8}")
    print("-" * 72)
    
    sorted_blues = sorted(blue_counts.items(), key=lambda x: (-x[1], x[0]))
    for rank, (num, cnt) in enumerate(sorted_blues, start=1):
        cur_om = latest.get("blue_omissions", {}).get(num, 0)
        max_om = blue_max_om[num]
        freq = round(cnt / window_size * 100, 2)
        diff = round(cnt - theory_blue, 1)
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        
        if rank <= 5:
            badge = "🔥 热号"
        elif rank <= 11:
            badge = "🌤️ 温号"
        else:
            badge = "❄️ 冷号"
            
        print(f"{rank:<4}{num:<6}{cnt:<10}{str(freq)+'%':<10}{diff_str:<10}{cur_om:<10}{max_om:<10}{badge:<8}")
        
    # 极值提炼
    top_r = sorted_reds[0]
    bot_r = sorted_reds[-1]
    max_om_r = max(latest.get("red_omissions", {}).items(), key=lambda x: x[1])
    
    top_b = sorted_blues[0]
    bot_b = sorted_blues[-1]
    max_om_b = max(latest.get("blue_omissions", {}).items(), key=lambda x: x[1])
    
    print_header("📌 核心极值提炼与预警")
    print(f"• 红球出球榜首: {top_r[0]} 号 (累计出球 {top_r[1]} 次，超出理论 {round(top_r[1]-theory_red, 1)} 次)")
    print(f"• 红球出球垫底: {bot_r[0]} 号 (累计出球 {bot_r[1]} 次，低于理论 {round(theory_red-bot_r[1], 1)} 次)")
    print(f"• 红球当前最大遗漏: {max_om_r[0]} 号 (已连续 {max_om_r[1]} 期未开出)")
    print(f"• 蓝球出球榜首: {top_b[0]} 号 (累计出球 {top_b[1]} 次，超出理论 {round(top_b[1]-theory_blue, 1)} 次)")
    print(f"• 蓝球当前最大遗漏: {max_om_b[0]} 号 (已连续 {max_om_b[1]} 期未开出)")
    print("=" * 72)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="双色球多维走势与冷热统计分析工具")
    parser.add_argument("--data", type=str, default=None, help="数据文件路径")
    parser.add_argument("--count", type=int, default=1000, help="分析期数，默认1000期")
    args = parser.parse_args()
    
    dataset = load_data(args.data)
    analyze(dataset, args.count)
