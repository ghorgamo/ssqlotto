#!/usr/bin/env python3
"""
双色球开奖数据多维统计与冷热分析引擎 (analyze_ssq.py)
输出冷/热/温号排名、遗漏值极值、形态学指标及控制台可视化图表。
"""

import os
import sys
import json
import argparse

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ssq_history_500.json")

def load_data(filepath=DEFAULT_DATA_PATH):
    if not os.path.exists(filepath):
        print(f"[Error] 数据文件未找到: {filepath}", file=sys.stderr)
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def print_header(title):
    print("\n" + "=" * 68)
    print(f"  {title}")
    print("=" * 68)

def analyze_and_print(data, top_n=10):
    metadata = data.get("metadata", {})
    stats = data.get("stats", {})
    history = data.get("history", [])
    
    print_header(f"{metadata.get('title', '双色球走势分析')} - 数据报告")
    print(f"分析期数范围: {metadata.get('issue_range')} (共 {metadata.get('total_issues')} 期)")
    print(f"开奖日期范围: {metadata.get('date_range')}")
    
    latest = history[-1]
    print(f"\n最新开奖期号: {latest['issue']} ({latest['date']} {latest['weekday']})")
    print(f"中奖号码: 红球 [{', '.join(latest['red'])}] + 蓝球 [{latest['blue']}]")
    print(f"形态属性: 和值={latest['sum']} | 跨度={latest['span']} | AC值={latest['ac']} | 奇偶比={latest['odd_even']} | 大小比={latest['big_small']}")
    
    # 打印红球冷热出球数排名
    print_header("🔴 红球出球数排名与冷/热/温分类 (1-33号)")
    print(f"{'排名':<4}{'号码':<6}{'出球次数':<10}{'出现频率':<10}{'当前遗漏':<10}{'最大遗漏':<10}{'状态分类':<8}")
    print("-" * 68)
    
    red_stats = stats.get("red_stats", [])
    for row in red_stats:
        cat_badge = row['category']
        if row['category_code'] == 'hot':
            cat_badge = f"🔥 {row['category']}"
        elif row['category_code'] == 'warm':
            cat_badge = f"🌤️ {row['category']}"
        else:
            cat_badge = f"❄️ {row['category']}"
            
        print(f"{row['rank']:<4}{row['number']:<6}{row['count']:<10}{str(row['frequency_percent'])+'%':<10}{row['current_omission']:<10}{row['max_omission']:<10}{cat_badge:<8}")
        
    # 打印蓝球冷热出球数排名
    print_header("🔵 蓝球出球数排名与冷/热/温分类 (1-16号)")
    print(f"{'排名':<4}{'号码':<6}{'出球次数':<10}{'出现频率':<10}{'当前遗漏':<10}{'最大遗漏':<10}{'状态分类':<8}")
    print("-" * 68)
    
    blue_stats = stats.get("blue_stats", [])
    for row in blue_stats:
        cat_badge = row['category']
        if row['category_code'] == 'hot':
            cat_badge = f"🔥 {row['category']}"
        elif row['category_code'] == 'warm':
            cat_badge = f"🌤️ {row['category']}"
        else:
            cat_badge = f"❄️ {row['category']}"
            
        print(f"{row['rank']:<4}{row['number']:<6}{row['count']:<10}{str(row['frequency_percent'])+'%':<10}{row['current_omission']:<10}{row['max_omission']:<10}{cat_badge:<8}")

    # 打印极值概括
    hottest_red = red_stats[0]
    coldest_red = red_stats[-1]
    max_om_red = max(red_stats, key=lambda x: x["current_omission"])
    
    hottest_blue = blue_stats[0]
    coldest_blue = blue_stats[-1]
    max_om_blue = max(blue_stats, key=lambda x: x["current_omission"])
    
    print_header("📌 核心极值提炼与关注预警")
    print(f"• 红球最热号: {hottest_red['number']} 号 (累计开出 {hottest_red['count']} 次，频率 {hottest_red['frequency_percent']}%)")
    print(f"• 红球最冷号: {coldest_red['number']} 号 (累计开出 {coldest_red['count']} 次，频率 {coldest_red['frequency_percent']}%)")
    print(f"• 红球当前最大遗漏: {max_om_red['number']} 号 (连续 {max_om_red['current_omission']} 期未开出，历史最大遗漏 {max_om_red['max_omission']} 期)")
    print(f"• 蓝球最热号: {hottest_blue['number']} 号 (累计开出 {hottest_blue['count']} 次，频率 {hottest_blue['frequency_percent']}%)")
    print(f"• 蓝球当前最大遗漏: {max_om_blue['number']} 号 (连续 {max_om_blue['current_omission']} 期未开出，历史最大遗漏 {max_om_blue['max_omission']} 期)")
    print("=" * 68)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="双色球多维走势与冷热统计分析工具")
    parser.add_argument("--data", type=str, default=DEFAULT_DATA_PATH, help="JSON数据文件路径")
    args = parser.parse_args()
    
    dataset = load_data(args.data)
    analyze_and_print(dataset)
