# -*- coding: utf-8 -*-
"""
图2-6：CPT 训练过程中领域数据与通用数据的困惑度变化曲线
对应正文 2.5.4 节：领域 PPL 18.7 -> 8.2；混合训练通用 PPL 9.5 -> 10.3 -> 9.8；纯领域训练通用 PPL 9.5 -> 12.6
领域 PPL 由图2-5 的损失曲线反推：ln PPL_domain = 2 L - ln PPL_general，保证两图在任意时刻一致
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

total_steps = 1000
progress = np.linspace(0, 100, total_steps)

general_mixed = np.zeros_like(progress)
mask_rise = progress <= 15
mask_fall = progress > 15
general_mixed[mask_rise] = 9.5 + (10.3 - 9.5) * np.sin((progress[mask_rise] / 15) * (np.pi / 2))
general_mixed[mask_fall] = 9.8 + (10.3 - 9.8) * np.exp(-(progress[mask_fall] - 15) / 20)

# 与 cpt_loss.py 相同的损失曲线（30% 进度处完成 80% 降幅）
initial_loss = (np.log(18.7) + np.log(9.5)) / 2
final_loss = (np.log(8.2) + np.log(9.8)) / 2
tau_progress = 30 / np.log(5)
loss = final_loss + (initial_loss - final_loss) * np.exp(-progress / tau_progress)
domain_ppl = np.exp(2 * loss - np.log(general_mixed))

general_pure = 9.5 + 3.1 * (progress / 100) ** 1.2

np.random.seed(42)
domain_ppl += np.random.normal(0, 0.06, total_steps)
general_mixed += np.random.normal(0, 0.04, total_steps)
general_pure += np.random.normal(0, 0.06, total_steps)

fig, ax = plt.subplots(figsize=(8.8, 5.4), dpi=300)

ax.plot(progress, domain_ppl, color="#1f77b4", linewidth=2.0, alpha=0.92, label="领域数据 PPL（1:1 混合训练）")
ax.plot(progress, general_mixed, color="#2ca02c", linewidth=2.0, alpha=0.92, label="通用数据 PPL（1:1 混合训练）")
ax.plot(progress, general_pure, color="#d62728", linewidth=2.2, linestyle="--", alpha=0.88, label="通用数据 PPL（纯领域训练）")

ax.set_xlabel("训练进度 (%)", fontsize=11.5)
ax.set_ylabel("困惑度 (PPL)", fontsize=11.5)
ax.set_xlim(0, 100)
ax.set_ylim(6, 20)
ax.grid(True, linestyle="--", alpha=0.45)
ax.legend(loc="upper right", fontsize=10, framealpha=0.95)

plt.tight_layout()
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.savefig(os.path.join(base_dir, "figures", "fig2-6_cpt_ppl.png"), dpi=300, bbox_inches="tight")
print("Saved fig2-6_cpt_ppl.png successfully.")
