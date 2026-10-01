#!/usr/bin/env python3
"""AlphaDesk 下载量统计: 拉 GitHub Release 资产下载数, 追加到 dl_stats.csv。

用法: python3 tools/dl_stats.py          # 记一次(含 Mac/Win/源码包分列)
      python3 tools/dl_stats.py --show    # 看历史趋势

建议每天跑一次(手动或 cron), 攒几周就是转化漏斗:
Release 访问 -> 下载 -> 试用 -> 付费(卖家手工记)。
"""
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = "dennicLiu/alphadesk-app"
CSV = Path(__file__).resolve().parent / "dl_stats.csv"


def fetch():
    r = subprocess.run(
        ["gh", "release", "view", "v1.0.1", "--repo", REPO,
         "--json", "assets", "--jq",
         ".assets[] | \"\\(.name) \\(.downloadCount)\""],
        capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print("拉取失败(网络抖动, 过会儿再跑):", r.stderr.strip()[:100])
        sys.exit(1)
    return r.stdout.strip().splitlines()


def main():
    show = "--show" in sys.argv
    if show:
        if not CSV.exists():
            print("还没有数据, 先跑一次 python3 tools/dl_stats.py")
            return
        for line in CSV.read_text().splitlines()[-15:]:
            print(line)
        return
    rows = fetch()
    counts = {}
    for line in rows:
        name, n = line.rsplit(" ", 1)
        counts[name] = int(n)
    day = datetime.now().strftime("%Y-%m-%d %H:%M")
    new = not CSV.exists()
    with open(CSV, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["时间", "Mac稳定版", "Win公测版", "源码包", "合计"])
        mac = counts.get("AlphaDesk-1.0.1-mac.zip", 0)
        win = counts.get("AlphaDesk-1.0.1-win-beta.zip", 0)
        src = sum(v for k, v in counts.items()
                  if k not in ("AlphaDesk-1.0.1-mac.zip",
                               "AlphaDesk-1.0.1-win-beta.zip"))
        w.writerow([day, mac, win, src, mac + win + src])
    print(f"{day} Mac={mac} Win={win} 源码={src} 合计={mac + win + src}")


if __name__ == "__main__":
    main()
