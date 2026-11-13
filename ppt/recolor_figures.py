"""按 PPT 统一的低饱和蓝灰配色重绘论文中的 matplotlib 图。

直接复用 plot/ 下的原始绘图脚本，只替换颜色字符串，并把输出重定向到
ppt/assets/m_*.png；figures/ 与 plot/ 中的论文用图不受影响。
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "assets")

MAIN, MID, SOFT, PALE = "#3A5A80", "#7E9BB8", "#A9B9CC", "#D3DCE7"
SAND, SAND_D = "#B9A27F", "#8A7148"
ROSE, ROSE_D = "#B07B74", "#8E5A54"

JOBS = {
    "ppl_threshold_selection.py": {
        '"#F2B134"': f'"{SAND}"', '"#4C78A8"': '"#6F8DAE"', '"#D64545"': f'"{ROSE}"',
        '"#2ca02c"': f'"{MAIN}"', '"#9A6A00"': f'"{SAND_D}"', '"#B22222"': f'"{ROSE_D}"',
        '"#2E6B2E"': f'"{MAIN}"', 'cmap="YlGnBu"': 'cmap="Blues"', '"#D62728"': f'"{ROSE_D}"',
    },
    "plot_data_ablation.py": {
        '"#1f77b4"': f'"{MID}"', '"#d62728"': f'"{SAND}"', '"#2ca02c"': f'"{MAIN}"',
    },
    "dft_gradient.py": {
        '"#d62728"': f'"{SAND}"', '"#1f77b4"': f'"{MAIN}"', '"#2ca02c"': f'"{MID}"',
        '"#2E6B2E"': f'"{MAIN}"',
    },
    "sqrt_reward.py": {
        '"#2C6CA2"': f'"{MAIN}"', '"#D64545"': f'"{ROSE}"', '"#C49618"': f'"{SAND}"',
    },
    "grpo_dapo.py": {
        '"#8DB4E2"': f'"{PALE}"', '"#1f77b4"': f'"{SOFT}"', '"#FF9999"': '"#9FB1C6"',
        '"#d62728"': f'"{MAIN}"',
    },
    "rl_entropy.py": {
        '"#8DB4E2"': f'"{PALE}"', '"#1f77b4"': f'"{SOFT}"', '"#8DE2A4"': '"#9FB1C6"',
        '"#2ca02c"': f'"{MAIN}"',
    },
    "安全性能变化.py": {'"#1f77b4"': f'"{MAIN}"'},
    "切分对比.py": {
        '"#EBF3FA"': '"#EDF1F6"', '"#4A77A8"': '"#7E9BB8"', '"#1B365D"': '"#2F4B6E"',
        '"#FDEBD0"': '"#F4EFE6"', '"#D35400"': f'"{SAND}"', '"#873600"': '"#6E5A3E"',
        '"#D4EFDF"': '"#E6ECEF"', '"#1E8449"': '"#7F95A6"', '"#145A32"': '"#3F5566"',
        '"#FADBD8"': '"#F3E6E4"', '"#C0392B"': f'"{ROSE}"', '"#78281F"': '"#6E4642"',
        '"#D68B8B"': '"#C9A6A1"',
    },
}

_orig_savefig = Figure.savefig
_done = set()


def _savefig(self, fname, *args, **kwargs):
    base = os.path.basename(str(fname))
    if not base.endswith(".png") or base in _done:
        return
    _done.add(base)
    kwargs["dpi"] = 250
    _orig_savefig(self, os.path.join(OUT, "m_" + base), *args, **kwargs)
    print("  ->", "m_" + base)


Figure.savefig = _savefig


def run():
    for script, repl in JOBS.items():
        path = os.path.join(ROOT, "plot", script)
        src = open(path, encoding="utf-8").read()
        for old, new in repl.items():
            if old not in src:
                print(f"  [warn] {script}: 未找到 {old}")
            src = src.replace(old, new)
        print(script)
        exec(compile(src, path, "exec"), {"__file__": path, "__name__": "__main__"})
        plt.close("all")
    im = Image.open(os.path.join(OUT, "m_fig5-2_token_char_split.png"))
    w, h = im.size
    im.crop((0, 0, w, int(h * 0.93))).save(os.path.join(OUT, "m_fig5-2_crop.png"))


if __name__ == "__main__":
    run()
