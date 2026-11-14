# -*- coding: utf-8 -*-
"""
Regenerate clean, large-font Matplotlib charts and crisp LaTeX equations
for the minimalist academic PPT redesign (zero clutter, large readable labels).
"""
import os
import shutil
import subprocess
import tempfile
import numpy as np
from PIL import Image
import pymupdf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.size"] = 13

OUT_DIR = os.path.join("ppt", "slides_assets")
os.makedirs(OUT_DIR, exist_ok=True)


def trim_white(im: Image.Image, pad: int = 10, bg_thresh: int = 250) -> Image.Image:
    if im.mode == "RGBA":
        arr = np.array(im)
        if arr[:, :, 3].min() < 250:
            ys, xs = np.where(arr[:, :, 3] > 5)
            if len(xs) == 0:
                return im
            return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad),
                            min(im.width, xs.max() + 1 + pad), min(im.height, ys.max() + 1 + pad)))
        im = im.convert("RGB")
    arr = np.array(im.convert("RGB"))
    ys, xs = np.where(np.any(arr < bg_thresh, axis=2))
    if len(xs) == 0:
        return im
    return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad),
                    min(im.width, xs.max() + 1 + pad), min(im.height, ys.max() + 1 + pad)))


def render_eq(name: str, body: str, dpi: int = 550):
    tex = r"""\documentclass[12pt]{article}
\usepackage[paperwidth=18cm,paperheight=8cm,margin=0.2cm]{geometry}
\usepackage{amsmath,amssymb,bm}
\usepackage{xcolor}
\usepackage{xeCJK}
\setCJKmainfont{SimHei}
\pagestyle{empty}
\definecolor{navy}{HTML}{003B66}
\definecolor{ink}{HTML}{1A1A1A}
\begin{document}
\color{ink}
""" + body + r"""
\end{document}
"""
    tmpdir = tempfile.mkdtemp(prefix="eq_")
    try:
        with open(os.path.join(tmpdir, "eq.tex"), "w", encoding="utf-8") as f:
            f.write(tex)
        subprocess.run(["xelatex", "-interaction=nonstopmode", "eq.tex"], cwd=tmpdir, capture_output=True, check=True)
        doc = pymupdf.open(os.path.join(tmpdir, "eq.pdf"))
        pix = doc[0].get_pixmap(dpi=dpi, alpha=True)
        im = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
        im = trim_white(im, pad=8)
        im.save(os.path.join(OUT_DIR, f"{name}.png"))
        print("EQ:", name, im.size)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def build_clean_equations():
    render_eq("eq_sft_quality_clean", r"""
\[
Q(x, y) = 0.12\,q_1 + 0.28\,q_2 + \mathbf{0.36\,q_3} + 0.24\,q_4, \qquad
\mathrm{accept}(x, y) = \mathbb{I}[Q \ge 0.75]\cdot\mathbb{I}[\mathcal{F}^{-}(y)=\varnothing]\cdot\mathbb{I}[q_3 \ge 0.6]\cdot\mathbb{I}[q_4 \ge 0.8]
\]
""")
    render_eq("eq_dft_clean", r"""
\[
\begin{aligned}
\mathcal{L}_{\mathrm{CE}}(\theta) &= \mathbb{E}\!\Bigl[-\sum_{t} \log p_t\Bigr]
&&\Longrightarrow\quad g_{\mathrm{CE}}(p) = 1 - p \\[6pt]
\mathcal{L}_{\mathrm{DFT}}(\theta) &= \mathbb{E}\!\Bigl[-\sum_{t} \mathrm{sg}(p_t)\log p_t\Bigr]
&&\Longrightarrow\quad g_{\mathrm{DFT}}(p) = p(1 - p)
\end{aligned}
\]
""")
    render_eq("eq_margin_clean", r"""
\[
s_k = x \oplus h_{\le k}, \qquad
m_\theta(s_k) = \beta \Bigl[ S_\theta^{\mathrm{avg}}(s_k, r_k) - S_\theta^{\mathrm{avg}}(s_k, u_k) \Bigr]
\]
""")
    render_eq("eq_prefix_clean", r"""
\[
\log \frac{\pi_\theta(h_{\le k}\oplus r_k \mid x)}{\pi_\theta(h_{\le k}\oplus u_k \mid x)}
= \log \frac{\pi_\theta(r_k \mid s_k)}{\pi_\theta(u_k \mid s_k)}
\]
""")
    render_eq("eq_hsw_clean", r"""
\[
\begin{aligned}
\phi_i &= \nu + (1-\nu)\,\frac{|\mathcal{B}_{\mathrm{rec}}|\exp(-m_i/\tau)}{\sum_{j\in\mathcal{B}_{\mathrm{rec}}}\exp(-m_j/\tau)}, \qquad
\psi_t = \frac{1+\zeta^{t-1}}{2}\Bigl(1 - \max_{t'}\cos\bigl(\mathbf{e}(y_t), \mathbf{e}(\bar{y}_{t'})\bigr)\Bigr) \\[6pt]
w_{i,t} &= \mathrm{sg}\!\left(\phi_i \cdot \frac{T\,[(1-\eta)+\eta\psi_t]}{\sum_{t'} [(1-\eta)+\eta\psi_{t'}]}\right)
\end{aligned}
\]
""")


def style_clean_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#333333")
    ax.spines["bottom"].set_color("#333333")
    ax.grid(axis="y", linestyle="--", linewidth=0.6, color="#D8DEE9")
    ax.set_axisbelow(True)


def build_clean_charts():
    NAVY = "#003B66"
    MID_BLUE = "#4F7CAC"
    GRAY_BAR = "#CBD5E1"
    RED_BAR = "#9E2A2B"

    # 1. Clean SFT Ablation Chart (Large 12pt labels)
    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=300)
    labels = ["去质量筛选 (9.3w)", "去指令演化", "去知识图谱", "去专家种子"]
    pqa = [-2.2, -3.1, -2.5, -4.9]
    fd = [-4.7, -8.7, -7.0, -7.7]
    reg = [-5.0, -6.0, -6.7, -11.0]

    y = np.arange(len(labels))
    h = 0.25
    b1 = ax.barh(y + h, pqa, h, label="PowerQA", color=GRAY_BAR)
    b2 = ax.barh(y, fd, h, label="FaultDiag", color=NAVY)
    b3 = ax.barh(y - h, reg, h, label="RegulationQA", color=RED_BAR)

    ax.axvline(0, color="#333333", lw=1.0)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=12, color="#1A1A1A")
    ax.set_xlabel("相对完整管线的得分变化 (pp)", fontsize=12, color="#1A1A1A")
    ax.set_xlim(-13.5, 0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", lw=0.6, color="#D8DEE9")
    ax.set_axisbelow(True)
    for bars in (b2, b3):
        for bar in bars:
            v = bar.get_width()
            ax.text(v - 0.25, bar.get_y() + bar.get_height() / 2, f"{v:.1f}",
                    va="center", ha="right", fontsize=10.5, color="#1A1A1A", fontweight="bold")
    ax.legend(loc="lower left", frameon=False, fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "chart_sft_ablation_clean.png"), dpi=300)
    plt.close(fig)

    # 2. Clean RoleStyle Chart (Large labels, crisp comparison)
    fig, ax = plt.subplots(figsize=(6.2, 4.1), dpi=300)
    cats = ["展开程度", "安全警示", "表述类型", "逐项警戒\n(最难项)", "总体\nSHR", "联合命中\nJoint-HR"]
    zero = [57.0, 49.3, 58.5, 33.9, 54.9, 20.0]
    few = [64.0, 56.7, 67.0, 42.1, 62.6, 27.0]
    rlaif = [89.5, 88.3, 92.6, 83.2, 90.2, 76.2]

    x = np.arange(len(cats))
    w = 0.25
    ax.bar(x - w, zero, w, label="零样本 Prompt", color=GRAY_BAR)
    ax.bar(x, few, w, label="少样本 Prompt", color=MID_BLUE)
    b3 = ax.bar(x + w, rlaif, w, label="RLAIF (12-tok Prefix)", color=NAVY)

    style_clean_ax(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=11, color="#1A1A1A")
    ax.set_ylabel("命中率 (%)", fontsize=12, color="#1A1A1A")
    ax.set_ylim(0, 115)
    for bar in b3:
        v = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:.1f}",
                ha="center", va="bottom", fontsize=10, fontweight="bold", color=NAVY)
    ax.legend(loc="upper center", ncol=3, frameon=False, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "chart_rolestyle_clean.png"), dpi=300)
    plt.close(fig)

    # 3. Clean External Comparison Chart (Unified grayscale-navy palette, single shared legend)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 3.7), dpi=300, gridspec_kw={"width_ratios": [1.45, 1.0]})

    m1 = ["PowerQA", "FaultDiag", "RegulationQA", "风格命中 SHR", "安全恢复 SRR"]
    q7b_1 = [52.6, 30.3, 18.3, 56.3, 6.4]
    qmax_1 = [73.5, 54.7, 52.0, 69.0, 12.6]
    ours_1 = [81.2, 61.3, 77.0, 89.1, 53.4]

    x1 = np.arange(len(m1))
    w = 0.25
    b_7b = ax1.bar(x1 - w, q7b_1, w, label="Qwen2.5-7B-Instruct", color=GRAY_BAR)
    b_qm = ax1.bar(x1, qmax_1, w, label="Qwen-Max（教师模型）", color=MID_BLUE)
    bo1 = ax1.bar(x1 + w, ours_1, w, label="本文最终模型（7B）", color=NAVY)
    style_clean_ax(ax1)
    ax1.set_xticks(x1)
    ax1.set_xticklabels(m1, fontsize=11.5, color="#1A1A1A")
    ax1.set_ylabel("正向指标（%，越高越好）", fontsize=12, color="#1A1A1A")
    ax1.set_ylim(0, 108)
    for bar in bo1:
        v = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:.1f}",
                 ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=NAVY)

    m2 = ["不安全率 URR", "攻击成功 ASR", "过度拒答 ORR"]
    q7b_2 = [24.5, 62.4, 9.7]
    qmax_2 = [9.5, 31.4, 4.0]
    ours_2 = [1.5, 7.9, 5.0]

    x2 = np.arange(len(m2))
    ax2.bar(x2 - w, q7b_2, w, color=GRAY_BAR)
    ax2.bar(x2, qmax_2, w, color=MID_BLUE)
    bo2 = ax2.bar(x2 + w, ours_2, w, color=NAVY)
    style_clean_ax(ax2)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(m2, fontsize=11.5, color="#1A1A1A")
    ax2.set_ylabel("风险与误拒率（%，越低越好）", fontsize=12, color="#1A1A1A")
    ax2.set_ylim(0, 72)
    for bar in bo2:
        v = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 1.2, f"{v:.1f}",
                 ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=NAVY)

    fig.legend([b_7b, b_qm, bo1], ["Qwen2.5-7B-Instruct", "Qwen-Max（教师模型）", "本文最终模型（7B）"],
               loc="upper center", ncol=3, frameon=False, fontsize=11.5, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(os.path.join(OUT_DIR, "chart_external_clean.png"), dpi=300)
    plt.close(fig)
    print("Clean charts generated.")


if __name__ == "__main__":
    build_clean_equations()
    build_clean_charts()
