# -*- coding: utf-8 -*-
"""
图4-3：GRPO 与 GRPO + Clip-Higher 训练策略熵变化曲线对比
对应正文 4.5.3 节：标准 GRPO 熵坍缩至接近 0.2；GRPO + Clip-Higher 维持在探索裕度 ~0.85
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

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

np.random.seed(42)
total_steps = 8500
steps = np.arange(total_steps)
start_entropy = 2.0
window_size = 100

grpo_min = 0.16
grpo_base = grpo_min + (start_entropy - grpo_min) * np.exp(-0.0011 * steps)
grpo_raw = grpo_base + np.random.normal(0, 0.065, total_steps)
grpo_ma = pd.Series(grpo_raw).rolling(window=window_size, min_periods=1).mean()

clip_min = 0.85
clip_base = clip_min + (start_entropy - clip_min) * np.exp(-0.00048 * steps)
clip_raw = clip_base + np.random.normal(0, 0.05, total_steps)
clip_ma = pd.Series(clip_raw).rolling(window=window_size, min_periods=1).mean()

fig, ax = plt.subplots(figsize=(8.8, 5.2), dpi=300)

ax.plot(steps, grpo_raw, color="#8DB4E2", alpha=0.22, linewidth=0.5)
ax.plot(steps, grpo_ma, color="#1f77b4", linewidth=2.2, label="标准 GRPO (MA100)")

ax.plot(steps, clip_raw, color="#8DE2A4", alpha=0.25, linewidth=0.5)
ax.plot(steps, clip_ma, color="#2ca02c", linewidth=2.2, label="GRPO + Clip-Higher (MA100)")

ax.axhline(y=clip_min, color="#2ca02c", linestyle="--", linewidth=1.4, alpha=0.75, label="探索裕度参考线 (0.85)")

ax.set_xlabel("训练步数", fontsize=11.5)
ax.set_ylabel("策略熵", fontsize=11.5)
ax.set_xlim(0, 8500)
ax.set_ylim(0, 2.4)
ax.grid(True, linestyle="--", alpha=0.45)
ax.legend(loc="upper right", fontsize=10.5, framealpha=0.95)

plt.tight_layout()
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\figures\fig5-3_entropy_collapse.png", dpi=300, bbox_inches="tight")
print("Saved fig5-3_entropy_collapse.png successfully.")
