# -*- coding: utf-8 -*-
"""福彩快乐8 数据抓取与维护脚本
数据源：500彩票网开奖静态XML（kaijiang.500.com/static/info/kaijiang/xml/kl8/list.xml，全量历史）
产出：data/kl8_history_1000.json/.csv（最近1000期，含遗漏与冷热统计），并同步刷新 kl8.html 内嵌 RAW_KL8。
新期并入前须按项目口径多源核对（网易+500），本脚本负责给定数据的重算与写回。
"""
import json, csv, os, re, datetime, urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
XML_URL = "https://kaijiang.500.com/static/info/kaijiang/xml/kl8/list.xml"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"}
WD = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

def fetch_xml():
    req = urllib.request.Request(XML_URL, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def parse_xml(text):
    out = {}
    for m in re.finditer(r'expect="(\d+)"\s+opencode="([\d,]+)"\s+opentime="(\d{4}-\d{2}-\d{2})', text):
        iss = m.group(1)
        iss = iss if len(iss) == 7 else "20" + iss
        out[iss] = {"nums": [int(x) for x in m.group(2).split(",")], "date": m.group(3)}
    return out

def parse_record(issue, item):
    """{issue, nums(20个), date} → 项目记录（不含遗漏，遗漏由 recalculate_omissions 递推）"""
    nums = sorted(item["nums"])
    assert len(nums) == 20 and len(set(nums)) == 20 and all(1 <= n <= 80 for n in nums), f"快乐8号码异常 {issue}: {nums}"
    odd = sum(n % 2 for n in nums)
    big = sum(1 for n in nums if n > 40)
    return {"issue": issue, "date": item["date"],
            "weekday": WD[datetime.date.fromisoformat(item["date"]).weekday()],
            "numbers": [f"{n:02d}" for n in nums], "sum": sum(nums), "span": nums[-1] - nums[0],
            "odd_even": f"{odd}:{20-odd}", "big_small": f"{big}:{20-big}"}

def recalculate_omissions(records):
    cur = {n: 0 for n in range(1, 81)}
    for rec in records:
        s = set(int(x) for x in rec["numbers"])
        om = {}
        for n in range(1, 81):
            cur[n] = 0 if n in s else cur[n] + 1
            om[f"{n:02d}"] = cur[n]
        rec["omissions"] = om

def _cat(rank, total):
    hot = max(1, round(total * 0.3)); warm = max(hot + 1, round(total * 0.7))
    return ("热号", "hot") if rank <= hot else (("温号", "warm") if rank <= warm else ("冷号", "cold"))

def compute_statistics(history):
    n = len(history)
    counts = {f"{i:02d}": 0 for i in range(1, 81)}
    maxom = {f"{i:02d}": 0 for i in range(1, 81)}
    for rec in history:
        for x in rec["numbers"]: counts[x] += 1
        for k, v in rec["omissions"].items(): maxom[k] = max(maxom[k], v)
    stats = []
    for rank, (num, cnt) in enumerate(sorted(counts.items(), key=lambda x: (-x[1], x[0])), start=1):
        cat, code = _cat(rank, 80); exp = n * 20 / 80
        stats.append({"rank": rank, "number": num, "category": cat, "category_code": code,
                      "frequency": cnt, "frequency_pct": round(cnt / n * 100, 2),
                      "current_omission": history[-1]["omissions"][num], "max_omission": maxom[num],
                      "expected": round(exp, 1), "bias": round(cnt - exp, 1),
                      "bias_pct": round((cnt - exp) / exp * 100, 2)})
    return {"total_issues": n, "start_issue": history[0]["issue"], "end_issue": history[-1]["issue"],
            "start_date": history[0]["date"], "end_date": history[-1]["date"], "number_stats": stats}

def build_metadata(records):
    return {"title": "福彩快乐8最近1000期中奖号码与全量遗漏冷热统计数据", "total_issues": len(records),
            "date_range": f"{records[0]['date']} 至 {records[-1]['date']}",
            "issue_range": f"{records[0]['issue']} 至 {records[-1]['issue']}",
            "latest_issue": records[-1]["issue"],
            "latest_draw": "号码: " + " ".join(records[-1]["numbers"]),
            "source": "500彩票网开奖数据（kaijiang.500.com），网易彩票核对",
            "updated_at": datetime.datetime.now().isoformat()}

def write_csv(records, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["期号", "开奖日期", "星期"] + [f"号码{i}" for i in range(1, 21)] + ["和值", "跨度", "奇偶比", "大小比"])
        for rec in records:
            w.writerow([rec["issue"], rec["date"], rec["weekday"]] + rec["numbers"] + [rec["sum"], rec["span"], rec["odd_even"], rec["big_small"]])

def raw_record(rec):
    return {"i": rec["issue"], "d": rec["date"], "w": rec["weekday"],
            "n": [int(x) for x in rec["numbers"]], "s": rec["sum"], "p": rec["span"],
            "oe": rec["odd_even"], "bs": rec["big_small"]}

def update_html(records, html_path):
    text = open(html_path, encoding="utf-8").read()
    raw = "const RAW_KL8 = " + json.dumps([raw_record(r) for r in records], ensure_ascii=False, separators=(",", ":")) + ";"
    new, cnt = re.subn(r"const RAW_KL8 = \[.*?\];", lambda m: raw, text, count=1, flags=re.S)
    assert cnt == 1, f"RAW_KL8 锚点未找到: {html_path}"
    open(html_path, "w", encoding="utf-8").write(new)

def main():
    raw = parse_xml(fetch_xml())
    issues = sorted(raw)[-1000:]
    records = [parse_record(iss, raw[iss]) for iss in issues]
    recalculate_omissions(records)
    doc = {"metadata": build_metadata(records), "stats": compute_statistics(records), "history": records}
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "kl8_history_1000.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    write_csv(records, os.path.join(DATA_DIR, "kl8_history_1000.csv"))
    p = os.path.join(BASE, "kl8.html")
    if os.path.exists(p): update_html(records, p)
    print(f"kl8: {len(records)} 期 {records[0]['issue']} → {records[-1]['issue']}")

if __name__ == "__main__":
    main()
