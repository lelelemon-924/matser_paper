# -*- coding: utf-8 -*-
"""
图5-3：DPO 训练过程安全性能变化曲线（最终实验模型，两阶段均采用 HS-Weighting）
各数据点为每 500 步保存的检查点在三个测试集上的评测结果
对齐 plot/cpt_loss.py 与 plot/cpt_ppl.py 的学术论文风格
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

candidates = [
    "PingFang SC",
    "Heiti TC",
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
    "Arial Unicode MS",
]
available_fonts = {f.name for f in font_manager.fontManager.ttflist}
chosen = next((f for f in candidates if f in available_fonts), None)
rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"] if chosen else ["sans-serif"]
rcParams["axes.unicode_minus"] = False

steps = np.arange(0, 2001, 500)

# 取值须与评测集题量一致：URR 400 题（0.25 的整数倍）、ASR/SRR 800 题（0.125 的整数倍）、ORR 300 题（1/3 的整数倍）
data = {
    "URR": {
        "title": "(a) 不安全回答率 (URR)",
        "ylabel": "URR (%)",
        "ylim": (0, 50),
        "yticks": [0, 10, 20, 30, 40, 50],
        "values": [42.5, 9.0, 2.5, 1.75, 1.5],
        "labels": [(0, "left", (6, 4)), (2, "center", (0, 8)), (4, "right", (-4, 8))],
    },
    "ASR": {
        "title": "(b) 攻击成功率 (ASR)",
        "ylabel": "ASR (%)",
        "ylim": (0, 100),
        "yticks": [0, 20, 40, 60, 80, 100],
        "values": [85.625, 37.5, 21.5, 10.5, 7.875],
        "labels": [(0, "left", (6, 4)), (2, "center", (0, 8)), (4, "right", (-4, 8))],
    },
    "SRR": {
        "title": "(c) 安全恢复率 (SRR)",
        "ylabel": "SRR (%)",
        "ylim": (0, 65),
        "yticks": [0, 15, 30, 45, 60],
        "values": [3.875, 17.0, 24.0, 46.0, 53.375],
        "labels": [(0, "left", (6, -12)), (2, "right", (-6, 4)), (4, "right", (-4, 8))],
    },
    "ORR": {
        "title": "(d) 过度拒答率 (ORR)",
        "ylabel": "ORR (%)",
        "ylim": (0, 22),
        "yticks": [0, 5, 10, 15, 20],
        "values": [7.0, 11.0, 38/3, 19/3, 5.0],
        "labels": [(0, "left", (6, -12)), (2, "center", (0, 8)), (4, "right", (-4, 8))],
    },
}

fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2), dpi=300)

color_hsw = "#1f77b4"

for ax, key in zip(axes.flat, ["URR", "ASR", "SRR", "ORR"]):
    d = data[key]
    values = np.array(d["values"])
    ax.set_ylim(*d["ylim"])
    ax.set_yticks(d["yticks"])
    ax.set_xlim(-100, 2100)
    ax.set_xticks(steps)
    ax.tick_params(axis="x", labelsize=9.5)

    # 阶段分界虚线
    ax.axvline(x=1000, color="gray", linestyle=":", linewidth=1.2, alpha=0.7)

    ax.plot(
        steps, values,
        color=color_hsw, linewidth=1.8, linestyle="-",
        marker="o", markersize=6, markerfacecolor="white", markeredgewidth=1.5,
    )

    # 标注起点、阶段分界点与终点数值
    for idx, ha, offset in d["labels"]:
        ax.annotate(
            f"{values[idx]:.1f}",
            xy=(steps[idx], values[idx]),
            xytext=offset, textcoords="offset points",
            ha=ha, va="bottom", fontsize=9, color=color_hsw,
        )

    y_top = d["ylim"][1]
    ax.text(500, y_top * 0.93, "第一阶段", ha="center", va="top", fontsize=10, color="dimgray")
    ax.text(1500, y_top * 0.93, "第二阶段", ha="center", va="top", fontsize=10, color="dimgray")

    ax.set_title(d["title"], fontsize=12, pad=8)
    ax.set_xlabel("训练步数", fontsize=11)
    ax.set_ylabel(d["ylabel"], fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout(pad=1.4, h_pad=2.0, w_pad=1.8)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.savefig(os.path.join(base_dir, "figures", "fig6-3_dpo_training_curves.png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(base_dir, "plot", "fig6_3_dpo_training_curves.pdf"), bbox_inches="tight")
print("Saved fig6-3_dpo_training_curves.png successfully.")
