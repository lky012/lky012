"""六合彩 (Mark Six) 過往數據分析與加權隨機選號.

用法: python mark_six_analysis.py <Mark_Six.xlsx>
需要: pandas, numpy, openpyxl
"""
import sys
from collections import Counter

import numpy as np
import pandas as pd

NUM_COLS = ['中獎號碼 1', '2', '3', '4', '5', '6']


def analyze(path: str) -> None:
    df = pd.read_excel(path)
    draws = df[NUM_COLS].values  # 第 0 列為最新一期
    total = len(df)
    print(f"總期數: {total}, 日期範圍: {df['日期'].min()} ~ {df['日期'].max()}")

    freq_all = Counter(draws.flatten())
    freq_100 = Counter(draws[:100].flatten())

    # 遺漏期數: 各號碼距離上次出現的期數
    gap = {}
    for n in range(1, 50):
        hits = np.where((draws == n).any(axis=1))[0]
        gap[n] = int(hits[0]) if len(hits) else total

    rank = sorted(range(1, 50), key=lambda n: -freq_all[n])
    print("全期最熱10:", [(n, freq_all[n]) for n in rank[:10]])
    print("全期最冷10:", [(n, freq_all[n]) for n in rank[-10:]])
    print("最耐未出10:", sorted(gap.items(), key=lambda x: -x[1])[:10])

    sums = draws.sum(axis=1)
    print(f"和值: 平均 {sums.mean():.0f}, P25-P75: "
          f"{np.percentile(sums, 25):.0f}-{np.percentile(sums, 75):.0f}")

    # 權重 = 50% 全期頻率 + 35% 近100期頻率 + 15% 遺漏回補
    w = np.zeros(49)
    for n in range(1, 50):
        w[n - 1] = (0.5 * freq_all[n] / max(freq_all.values())
                    + 0.35 * freq_100[n] / max(freq_100.values())
                    + 0.15 * min(gap[n], 30) / 30)
    w /= w.sum()

    def valid(combo: np.ndarray) -> bool:
        odd = (combo % 2 == 1).sum()
        low = (combo <= 24).sum()
        return 2 <= odd <= 4 and 2 <= low <= 4 and 115 <= combo.sum() <= 185

    rng = np.random.default_rng()
    picks = []
    while len(picks) < 3:
        c = rng.choice(np.arange(1, 50), size=6, replace=False, p=w)
        combo = sorted(int(x) for x in c)
        if valid(np.array(combo)) and combo not in picks:
            picks.append(combo)

    print("\n加權隨機選號:")
    for i, p in enumerate(picks, 1):
        odd = sum(1 for x in p if x % 2)
        low = sum(1 for x in p if x <= 24)
        print(f"  組{i}: {p}  和值={sum(p)} 單:雙={odd}:{6-odd} 小:大={low}:{6-low}")


if __name__ == '__main__':
    analyze(sys.argv[1] if len(sys.argv) > 1 else 'Mark_Six_4.xlsx')
