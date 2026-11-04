import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置随机种子
np.random.seed(42)

# 1. 模拟基础参数
total_steps = 8500
steps = np.arange(total_steps)
start_reward = 0.1  # 调整起始奖励
window_size = 100

# ====================
# 2. 模拟 Online-DPO
# ====================
odpo_end = 0.58  # Online-DPO 最终 Proxy Reward 通常低于 PPO，但更不易 Hacking
odpo_k = 0.0004  # 收敛速度与 PPO 类似
# 基础趋势
odpo_base = odpo_end - (odpo_end - start_reward) * np.exp(-odpo_k * steps)

# Online-DPO 基于偏好对更新，波动通常小于直接最大化 Reward 的 PPO
odpo_noise_std = 0.12  
odpo_raw = odpo_base + np.random.normal(0, odpo_noise_std, total_steps)

# 严格截断在 0-1 之间
odpo_raw = np.clip(odpo_raw, 0, 1)
odpo_ma = pd.Series(odpo_raw).rolling(window=window_size, min_periods=1).mean()

# ====================
# 3. 开始绘图
# ====================
plt.figure(figsize=(10, 6), dpi=120)

# 绘制 Online-DPO (浅紫色噪点 + 深紫色主线)
plt.plot(steps, odpo_raw, color='#C5B0D5', alpha=0.5, linewidth=0.5)
plt.plot(steps, odpo_ma, color='#9467BD', linewidth=2.5, label='Online-DPO MA(100)')

# 设置坐标轴标签 (去除 title 保持一致)
plt.title('Online-DPO Training Reward', fontsize=16)
plt.xlabel('step', fontsize=14)
plt.ylabel('reward', fontsize=14)

# 添加网格线
plt.grid(True, linestyle='-', color='lightgray', alpha=0.7)

# 调整y轴的显示范围，使其严格在 0 到 1 的范围内稍微留白
plt.ylim(0, 1.05)

# 设置图例
plt.legend(loc='upper left', fontsize=12, framealpha=1.0)

# 调整布局并显示
plt.tight_layout()
plt.show()

# 如果需要保存图片，可以取消下面这行的注释：
plt.savefig('fig5-4_dpo_reward.png', dpi=300, bbox_inches='tight')