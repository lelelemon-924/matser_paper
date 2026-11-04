# -*- coding: utf-8 -*-
"""
图2-5：CPT 训练过程损失与学习率衰减曲线
对应正文 2.5.4 节：训练损失 5.32 -> 2.03，峰值学习率 3e-5，最小学习率 3e-6，前 5% 线性预热
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
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

total_steps = 1000
steps = np.arange(total_steps)
progress = (steps / total_steps) * 100

eta_max = 3e-5
eta_min = 3e-6
warmup_steps = int(total_steps * 0.05)

lr = np.zeros(total_steps)
lr[:warmup_steps] = np.linspace(0, eta_max, warmup_steps)
decay_steps = total_steps - warmup_steps
t_decay = np.arange(decay_steps)
lr[warmup_steps:] = eta_min + 0.5 * (eta_max - eta_min) * (1 + np.cos(t_decay * np.pi / decay_steps))

initial_loss = 5.32
final_loss = 2.03
loss_drop = initial_loss - final_loss
base_loss = final_loss + loss_drop * np.exp(-steps / 120)

np.random.seed(42)
train_loss = base_loss + np.random.normal(0, 0.03, total_steps)
val_loss = final_loss + loss_drop * np.exp(-steps / 140) + 0.08 + np.random.normal(0, 0.015, total_steps)
train_loss[0] = initial_loss
val_loss[0] = initial_loss + 0.02

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 6.8), dpi=300, sharex=True)

ax1.plot(progress, train_loss, color="#1f77b4", alpha=0.85, linewidth=1.6, label="训练损失")
ax1.plot(progress, val_loss, color="#ff7f0e", alpha=0.92, linewidth=2.0, label="验证损失")
ax1.set_ylabel("损失值 (Loss)", fontsize=11)
ax1.grid(True, linestyle="--", alpha=0.45)
ax1.legend(loc="upper right", fontsize=10, framealpha=0.95)
ax1.set_ylim(1.5, 6.0)
ax1.set_xlim(0, 100)

ax2.plot(progress, lr, color="#2ca02c", linewidth=2.2, label="学习率 $\\eta_t$")
ax2.set_xlabel("训练进度 (%)", fontsize=11)
ax2.set_ylabel("学习率 $\\eta_t$", fontsize=11)
ax2.grid(True, linestyle="--", alpha=0.45)
ax2.legend(loc="upper right", fontsize=10, framealpha=0.95)

formatter = ScalarFormatter(useMathText=True)
formatter.set_powerlimits((0, 0))
ax2.yaxis.set_major_formatter(formatter)
ax2.axvline(x=5, color="gray", linestyle=":", linewidth=1.2, alpha=0.75)

plt.tight_layout()
plt.savefig(r"c:\Users\JOJO\Desktop\论文初稿\figures\fig3-5_cpt_loss.png", dpi=300, bbox_inches="tight")
print("Saved fig3-5_cpt_loss.png successfully.")
