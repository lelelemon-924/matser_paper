# -*- coding: utf-8 -*-
"""
图2-3：基于教师模型标注的 PPL 双阈值选取
(a) Qwen-Max 对 20 个 5% 分位段的标注结果（低信息冗余 / 有效专业文本 / 隐性噪声污染）
(b) 基于标注比例的零训练阈值搜索：各 (下界, 上界) 组合的保留质量得分 F 热力图，框出最优组合

注意：以下数值为与正文对齐的示意数据，需替换为真实标注结果。
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

candidates = [
    "PingFang SC",
    "Heiti TC",
    "Songti SC",
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

# ---------------- 示意数据：Qwen-Max 分位段标注比例（每段 250 条） ----------------
redundant = np.array([
    0.82, 0.66, 0.23, 0.15, 0.10, 0.07, 0.05, 0.04, 0.03, 0.02,
    0.02, 0.01, 0.01, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00,
])
noise = np.array([
    0.03, 0.03, 0.02, 0.03, 0.03, 0.03, 0.04, 0.04, 0.05, 0.06,
    0.07, 0.08, 0.09, 0.11, 0.14, 0.20, 0.58, 0.70, 0.84, 0.94,
])
effective = 1.0 - redundant - noise
n_bins = len(effective)
edges_pct = np.arange(0, 101, 5)


def keep_score(lo, hi):
    """保留区间 [P_lo, P_hi] 的保留质量得分 F（有效召回率 R 与保留纯度 Q 的调和平均）"""
    idx = np.arange(lo // 5, hi // 5)
    kept = effective[idx].sum()
    recall = kept / effective.sum()
    precision = kept / len(idx)
    return 2 * recall * precision / (recall + precision)


lows = np.arange(0, 31, 5)
highs = np.arange(60, 101, 5)
F = np.array([[keep_score(lo, hi) for hi in highs] for lo in lows]) * 100
bi, bj = np.unravel_index(np.argmax(F), F.shape)
print(f"Best: [P{lows[bi]}, P{highs[bj]}]  F = {F[bi, bj]:.1f}")

# ---------------- 绘图 ----------------
fig = plt.figure(figsize=(14.5, 5.0), dpi=300)
gs = GridSpec(1, 2, width_ratios=[1.6, 1.0], wspace=0.22)

c_red, c_eff, c_noise = "#F2B134", "#4C78A8", "#D64545"

# (a) 分位段标注堆叠柱状图
ax1 = fig.add_subplot(gs[0, 0])
x = np.arange(n_bins)
ax1.bar(x, redundant, width=0.82, color=c_red, label="低信息冗余")
ax1.bar(x, effective, width=0.82, bottom=redundant, color=c_eff, label="有效专业文本")
ax1.bar(x, noise, width=0.82, bottom=redundant + effective, color=c_noise, label="隐性噪声污染")
ax1.axvline(1.5, color="#2ca02c", linestyle="--", linewidth=1.8)
ax1.axvline(15.5, color="#2ca02c", linestyle="--", linewidth=1.8)
ax1.axvspan(-0.5, 1.5, color="#888888", alpha=0.10)
ax1.axvspan(15.5, n_bins - 0.5, color="#888888", alpha=0.10)
ax1.text(0.5, 1.035, "冗余 74%", ha="center", va="bottom", fontsize=9.5, color="#9A6A00", fontweight="bold")
ax1.text(17.5, 1.035, "噪声 64% → 89%", ha="center", va="bottom", fontsize=9.5, color="#B22222", fontweight="bold")
ax1.text(8.5, 1.035, "保留区间 $[P_{10}, P_{80}]$（PPL 4.8–35.5）", ha="center", va="bottom",
         fontsize=9.5, color="#2E6B2E", fontweight="bold")
ax1.set_xticks(x)
ax1.set_xticklabels([f"{a}–{b}" for a, b in zip(edges_pct[:-1], edges_pct[1:])], fontsize=8, rotation=45)
ax1.set_xlim(-0.5, n_bins - 0.5)
ax1.set_ylim(0, 1.13)
ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax1.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
ax1.set_xlabel("PPL 分位段（%）", fontsize=10.5)
ax1.set_ylabel("Qwen-Max 标注占比", fontsize=10.5)
ax1.set_title("(a) 教师模型分位段标注：每 5% 分位段抽样 250 条，共 5,000 条", fontsize=11.5, pad=20)
ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=3, fontsize=9.5, frameon=False)

# (b) 阈值组合热力图
ax2 = fig.add_subplot(gs[0, 1])
im = ax2.imshow(F, cmap="YlGnBu", aspect="auto", origin="upper", vmin=F.min(), vmax=F.max())
ax2.set_xticks(np.arange(len(highs)))
ax2.set_xticklabels([f"$P_{{{h}}}$" for h in highs], fontsize=9)
ax2.set_yticks(np.arange(len(lows)))
ax2.set_yticklabels([f"$P_{{{l}}}$" for l in lows], fontsize=9)
ax2.set_xlabel("上界（剔除高 PPL 噪声）", fontsize=10.5)
ax2.set_ylabel("下界（剔除低 PPL 冗余）", fontsize=10.5)
for i in range(len(lows)):
    for j in range(len(highs)):
        val = F[i, j]
        ax2.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=7.6,
                 fontweight="bold" if (i, j) == (bi, bj) else "normal",
                 color="white" if val > F.min() + 0.62 * (F.max() - F.min()) else "#222222")
ax2.add_patch(Rectangle((bj - 0.5, bi - 0.5), 1, 1, fill=False, edgecolor="#D62728", linewidth=2.6))
cbar = fig.colorbar(im, ax=ax2, fraction=0.045, pad=0.03)
cbar.set_label("保留质量得分 $F$（%）", fontsize=9.5)
ax2.set_title(f"(b) 零训练阈值搜索：最优 $[P_{{{lows[bi]}}}, P_{{{highs[bj]}}}]$", fontsize=11.5, pad=20)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.savefig(os.path.join(base_dir, "figures", "ppl_threshold_selection.png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(base_dir, "plot", "ppl_threshold_selection.pdf"), bbox_inches="tight")
print("Saved ppl_threshold_selection.png successfully.")
