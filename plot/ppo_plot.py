import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置随机种子以保证结果可复现
np.random.seed(42)

# 1. 模拟基础参数
total_steps = 8500
steps = np.arange(total_steps)

# 生成基础趋势线 (模拟PPO学习过程：从2上升并逐渐收敛到接近6)
# 使用指数收敛模型: reward = end_val - (end_val - start_val) * exp(-k * step)
start_reward = 2.0
end_reward = 6.2  # 设定稍微高一点，使最终截断点刚好在6左右
learning_rate_k = 0.00035 # 决定曲线上升的快慢

base_trend = end_reward - (end_reward - start_reward) * np.exp(-learning_rate_k * steps)

# 2. 添加采样噪声
# PPO训练初期往往波动较大，这里使用正态分布模拟环境反馈和策略更新的随机性
noise_std = 2.9 # 调整此参数可以控制浅蓝色区域的"宽度" (方差)
raw_reward = base_trend + np.random.normal(0, noise_std, total_steps)

# 3. 计算滑动平均 (Moving Average)
window_size = 100
# 使用 pandas 的 rolling 窗口计算 MA(100)
smoothed_reward = pd.Series(raw_reward).rolling(window=window_size, min_periods=1).mean()

# 4. 开始绘图
# 设置画布大小，与参考图比例相近
plt.figure(figsize=(10, 6), dpi=120)

# 绘制原始带噪声的奖励曲线，使用浅蓝色，降低透明度，线宽调细
plt.plot(steps, raw_reward, color='#8DB4E2', alpha=0.6, linewidth=0.5, label='raw')

# 绘制平滑后的奖励曲线，使用醒目的橙色，加粗线条
plt.plot(steps, smoothed_reward, color='#FF7F0E', linewidth=2.5, label=f'MA({window_size})')

# 设置图表标题和坐标轴标签
plt.title('reward', fontsize=16)
plt.xlabel('step', fontsize=14)
# plt.ylabel('reward', fontsize=14) # 参考图没有y轴label，可以根据需要取消注释

# 添加网格线，颜色调淡以突出数据曲线
plt.grid(True, linestyle='-', color='lightgray', alpha=0.7)

# 调整y轴的显示范围，使其类似参考图的留白感
plt.ylim(0, 9)

# 设置图例位置和样式
plt.legend(loc='upper left', fontsize=12, framealpha=1.0)

# 移除上边框和右边框（可选，让图表看起来更现代，如果不需要可以注释掉）
# ax = plt.gca()
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)

# 调整布局并显示
plt.tight_layout()
plt.show()

# 如果需要保存为高清图片，可以将 plt.show() 替换为下面这行：
plt.savefig('ppo_reward_simulation.png', dpi=300, bbox_inches='tight')