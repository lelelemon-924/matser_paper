# -*- coding: utf-8 -*-
"""
图2-3：电力领域语料困惑度（PPL）分布
(a) 按教师模型标注构成堆叠的 PPL 直方图（对数横轴），右轴为各区间有效专业文本占比，显示 P10 / P80 两处拐点
(b) 全量候选语料 PPL 箱线图与分位数
对应正文 2.5.2 节：P10 = 4.8，P50 = 13.6，P80 = 35.5，保留中间 70% 切片

注意：类别构成按 ppl_threshold_selection.py 中各 5% 分位段的标注比例插值估计（按期望计数堆叠），为示意数据，需替换为真实标注结果。
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter
from scipy.interpolate import PchipInterpolator

candidates = [
    "PingFang SC",
    "Heiti TC",
    "Arial Unicode MS",
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
]
available_fonts = {f.name for f in font_manager.fontManager.ttflist}
chosen = next((f for f in candidates if f in available_fonts), None)
rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"] if chosen else ["sans-serif"]
rcParams["axes.unicode_minus"] = False

p10_val = 4.8
p50_target = 13.6
p80_val = 35.5
x_min, x_max = 2.2, 100

# 在对数 PPL 空间用单调平滑的 CDF 生成样本：对数密度单峰、两侧平滑衰减，
# 且 P10 / P50 / P80 精确落在 4.8 / 13.6 / 35.5
cdf_ppl = [x_min, 3.0, p10_val, 8.0, p50_target, 22.0, p80_val, 55.0, 75.0, x_max]
cdf_u = [0.0, 0.02, 0.10, 0.27, 0.50, 0.68, 0.80, 0.895, 0.955, 1.0]
cdf = PchipInterpolator(np.log(cdf_ppl), cdf_u)
grid = np.linspace(np.log(x_min), np.log(x_max), 20001)
rng = np.random.default_rng(42)
n_samples = 8000
u = (np.arange(n_samples) + rng.uniform(size=n_samples)) / n_samples
ppl = np.exp(np.interp(u, cdf(grid), grid))
p50_val = float(np.median(ppl))

# 与 ppl_threshold_selection.py 一致的 20 个 5% 分位段标注比例，在分位段中心之间线性插值
redundant = np.array([
    0.82, 0.66, 0.23, 0.15, 0.10, 0.07, 0.05, 0.04, 0.03, 0.02,
    0.02, 0.01, 0.01, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00,
])
noise = np.array([
    0.03, 0.03, 0.02, 0.03, 0.03, 0.03, 0.04, 0.04, 0.05, 0.06,
    0.07, 0.08, 0.09, 0.11, 0.14, 0.20, 0.58, 0.70, 0.84, 0.94,
])
seg_centers = np.arange(20) * 0.05 + 0.025
p_red = np.interp(u, seg_centers, redundant)
p_noise = np.interp(u, seg_centers, noise)
p_eff = 1.0 - p_red - p_noise

c_red, c_eff, c_noise = "#F2B134", "#4C78A8", "#D64545"

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(12.0, 4.8), dpi=300,
    gridspec_kw={"width_ratios": [1.75, 1.0]}
)

# ---------------- (a) 按标注构成堆叠的对数横轴直方图 ----------------
# 对数等宽分箱，边界对齐 P10 / P80，避免柱子跨越阈值
bins = np.unique(np.concatenate([
    np.geomspace(x_min, p10_val, 9),
    np.geomspace(p10_val, p80_val, 21),
    np.geomspace(p80_val, x_max, 11),
]))
counts, edges, _ = ax1.hist(
    [ppl] * 3, bins=bins, weights=[p_red, p_eff, p_noise], stacked=True, color=[c_red, c_eff, c_noise],
    edgecolor="white", linewidth=0.4,
    label=["低信息冗余", "有效专业文本", "隐性噪声污染"],
)
ax1.axvspan(x_min, p10_val, color="#888888", alpha=0.10, zorder=0)
ax1.axvspan(p80_val, x_max, color="#888888", alpha=0.10, zorder=0)
ax1.axvline(p10_val, color="#2ca02c", linestyle="--", linewidth=1.6)
ax1.axvline(p80_val, color="#2ca02c", linestyle="--", linewidth=1.6)

ax1.set_xscale("log")
ax1.set_xlim(x_min, x_max)
ticks = [3, 4.8, 10, 13.6, 20, 35.5, 60, 100]
ax1.xaxis.set_major_locator(FixedLocator(ticks))
ax1.xaxis.set_minor_locator(NullLocator())
ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
ax1.set_xlabel("困惑度 PPL（对数刻度）", fontsize=11)
ax1.set_ylabel("语料切片频数", fontsize=11)
ymax = counts[-1].max() * 1.22
ax1.set_ylim(0, ymax)
ax1.grid(True, axis="y", linestyle="--", alpha=0.4)

# 右轴：各 PPL 区间有效专业文本占比
total = counts[-1]
eff_share = np.divide(counts[1] - counts[0], total, out=np.zeros_like(total), where=total > 0)
centers = np.sqrt(edges[:-1] * edges[1:])
axr = ax1.twinx()
axr.plot(centers, eff_share * 100, color="#1B3A5C", marker="o", markersize=3.2, linewidth=1.8,
         label="有效专业文本占比（右轴）")
axr.set_ylim(0, 105)
axr.set_ylabel("有效专业文本占比（%）", fontsize=11)

ax1.text(np.sqrt(x_min * p10_val), ymax * 0.93, "冗余区\n$<P_{10}$", ha="center", va="top",
         fontsize=9.5, color="#9A6A00", fontweight="bold")
ax1.text(np.sqrt(p10_val * p80_val), ymax * 0.93, "保留区间 $[P_{10}, P_{80}]$（中间 70%）", ha="center", va="top",
         fontsize=9.5, color="#2E6B2E", fontweight="bold")
ax1.text(np.sqrt(p80_val * x_max), ymax * 0.93, "噪声区\n$>P_{80}$", ha="center", va="top",
         fontsize=9.5, color="#B22222", fontweight="bold")
axr.annotate("拐点 $P_{10}=4.8$", xy=(p10_val, 60), xytext=(2.45, 82),
             fontsize=9, color="#2ca02c", arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.1))
axr.annotate("拐点 $P_{80}=35.5$", xy=(p80_val, 55), xytext=(40, 72),
             fontsize=9, color="#2ca02c", arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.1))

h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = axr.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=4,
           fontsize=9, frameon=False)
ax1.set_title("(a) 候选语料 PPL 分布与标注构成", fontsize=12, pad=8)

# ---------------- (b) 箱线图 ----------------
ax2.boxplot(
    ppl,
    vert=True,
    widths=0.28,
    patch_artist=True,
    showfliers=True,
    boxprops=dict(facecolor="#D0E1F2", edgecolor="#1f77b4", linewidth=1.4),
    medianprops=dict(color="#ff7f0e", linewidth=2.0),
    whiskerprops=dict(color="#1f77b4", linewidth=1.3),
    capprops=dict(color="#1f77b4", linewidth=1.3),
    flierprops=dict(marker="o", markerfacecolor="#90A4AE", markeredgecolor="none", markersize=3.2, alpha=0.45),
)
ax2.axhline(p10_val, color="#2ca02c", linestyle="--", linewidth=1.6, label=f"$P_{{10}} = {p10_val}$")
ax2.axhline(p50_val, color="#ff7f0e", linestyle="-.", linewidth=1.4, label=f"中位数 $P_{{50}} = {p50_val:.1f}$")
ax2.axhline(p80_val, color="#d62728", linestyle="--", linewidth=1.6, label=f"$P_{{80}} = {p80_val}$")
ax2.axhspan(p10_val, p80_val, color="#4C78A8", alpha=0.08)
ax2.set_title("(b) 候选语料 PPL 箱线图与分位数", fontsize=12, pad=8)
ax2.set_ylabel("困惑度 (PPL)", fontsize=11)
ax2.set_xticks([1])
ax2.set_xticklabels(["全量候选语料"])
ax2.set_ylim(0, 108)
ax2.grid(True, linestyle="--", alpha=0.45)
ax2.legend(loc="upper right", fontsize=9.5, framealpha=0.95)

plt.tight_layout(pad=1.2, w_pad=2.2)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.savefig(os.path.join(base_dir, "figures", "ppl_distribution.png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(base_dir, "ppl_distribution.png"), dpi=300, bbox_inches="tight")

kept = ((ppl >= p10_val) & (ppl <= p80_val)).mean()
print("P10/P50/P80 =", np.percentile(ppl, [10, 50, 80]), f"保留区间占比 = {kept:.2%}")
for name, mask in [("<P10", ppl < p10_val), ("[P10,P80]", (ppl >= p10_val) & (ppl <= p80_val)),
                   (">P80", ppl > p80_val)]:
    print(name, "冗余/有效/噪声 =", np.round([p_red[mask].mean(), p_eff[mask].mean(), p_noise[mask].mean()], 3))
print("Saved ppl_distribution.png successfully.")
