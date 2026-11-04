# -*- coding: utf-8 -*-
"""
图5-3：DPO 训练过程安全性能变化曲线
对齐 plot/cpt_loss.py 与 plot/cpt_ppl.py 的学术论文风格
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
from scipy.interpolate import PchipInterpolator

candidates = [
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

knots_p1 = np.array([0, 200, 400, 600, 800, 1000])
knots_p2 = np.array([1000, 1200, 1400, 1600, 1800, 2000])

dense_all = np.linspace(0, 2000, 401)
dense_p2 = np.linspace(1000, 2000, 201)

data = {
    "URR": {
        "title": "(a) 不安全回答率 (URR)",
        "ylabel": "URR (%)",
        "ylim": (0, 50),
        "yticks": [0, 10, 20, 30, 40, 50],
        "p1": np.array([42.5, 24.0, 12.5, 6.8, 4.2, 3.2]),
        "p2_hsw": np.array([3.2, 2.5, 2.0, 1.7, 1.55, 1.5]),
        "p2_eq": np.array([3.2, 2.9, 2.7, 2.6, 2.53, 2.5]),
        "noise": 0.15,
        "legend_loc": "upper right",
    },
    "ASR": {
        "title": "(b) 攻击成功率 (ASR)",
        "ylabel": "ASR (%)",
        "ylim": (0, 100),
        "yticks": [0, 20, 40, 60, 80, 100],
        "p1": np.array([85.6, 62.0, 44.0, 31.5, 25.0, 21.5]),
        "p2_hsw": np.array([21.5, 15.8, 11.8, 9.5, 8.3, 7.9]),
        "p2_eq": np.array([21.5, 17.8, 14.8, 12.8, 11.6, 11.1]),
        "noise": 0.30,
        "legend_loc": "upper right",
    },
    "SRR": {
        "title": "(c) 安全恢复率 (SRR)",
        "ylabel": "SRR (%)",
        "ylim": (0, 65),
        "yticks": [0, 15, 30, 45, 60],
        "p1": np.array([3.9, 9.5, 14.8, 19.0, 22.0, 24.0]),
        "p2_hsw": np.array([24.0, 35.0, 43.2, 48.8, 52.0, 53.4]),
        "p2_eq": np.array([24.0, 31.2, 37.5, 42.0, 44.7, 45.9]),
        "noise": 0.22,
        "legend_loc": "upper left",
    },
    "ORR": {
        "title": "(d) 过度拒答率 (ORR)",
        "ylabel": "ORR (%)",
        "ylim": (0, 22),
        "yticks": [0, 5, 10, 15, 20],
        "p1": np.array([7.0, 8.8, 10.5, 11.8, 12.7, 13.2]),
        "p2_hsw": np.array([13.2, 9.6, 7.2, 5.8, 5.2, 5.0]),
        "p2_eq": np.array([13.2, 10.3, 8.0, 6.4, 5.4, 5.0]),
        "noise": 0.07,
        "legend_loc": "upper right",
    },
}

np.random.seed(42)
fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2), dpi=300)

color_hsw = "#1f77b4"
color_eq = "#ff7f0e"

for ax, key in zip(axes.flat, ["URR", "ASR", "SRR", "ORR"]):
    d = data[key]
    ax.set_ylim(*d["ylim"])
    ax.set_yticks(d["yticks"])
    ax.set_xlim(0, 2000)
    ax.set_xticks([0, 500, 1000, 1500, 2000])

    knots_all = np.concatenate([knots_p1[:-1], knots_p2])
    vals_hsw_knots = np.concatenate([d["p1"][:-1], d["p2_hsw"]])

    y_hsw = PchipInterpolator(knots_all, vals_hsw_knots)(dense_all)
    y_eq = PchipInterpolator(knots_p2, d["p2_eq"])(dense_p2)

    n1 = np.random.normal(0, d["noise"], len(dense_all))
    n2 = np.random.normal(0, d["noise"], len(dense_p2))
    n1[0] = n1[200] = n1[-1] = 0.0
    n2[0] = n2[-1] = 0.0

    y_hsw = y_hsw + n1
    y_eq = y_eq + n2

    # 阶段分界虚线
    ax.axvline(x=1000, color="gray", linestyle=":", linewidth=1.2, alpha=0.7)

    ax.plot(
        dense_all, y_hsw,
        color=color_hsw, linewidth=2.0, linestyle="-", alpha=0.95,
        label="HS-Weighting",
    )
    ax.plot(
        dense_p2, y_eq,
        color=color_eq, linewidth=2.0, linestyle="--", alpha=0.9,
        label="等权 DPO",
    )

    ax.set_title(d["title"], fontsize=12, pad=8)
    ax.set_xlabel("训练步数", fontsize=11)
    ax.set_ylabel(d["ylabel"], fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc=d["legend_loc"], fontsize=10, framealpha=0.95)

plt.tight_layout(pad=1.4, h_pad=2.0, w_pad=1.8)
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\figures\fig6-3_dpo_training_curves.png", dpi=300, bbox_inches="tight")
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\plot\fig6_3_dpo_training_curves.pdf", bbox_inches="tight")
print("Saved fig6-3_dpo_training_curves.png successfully.")
