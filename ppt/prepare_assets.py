# -*- coding: utf-8 -*-
"""
Prepare high-DPI academic assets for HITSZ Master's Defense PPT:
1. Official HITSZ logos (cropped RGBA blue & white variants)
2. 400-DPI vector renders of thesis PDF figures + auto-trimmed PNG figures
3. 600-DPI transparent LaTeX equation images compiled via xelatex
4. Clean Matplotlib academic charts matching the thesis figure aesthetic
"""
import os
import shutil
import subprocess
import tempfile
import zipfile
import numpy as np
from PIL import Image
import pymupdf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Configure Matplotlib for crisp Chinese + English academic typography
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.size"] = 11

OUT_DIR = os.path.join("ppt", "slides_assets")
os.makedirs(OUT_DIR, exist_ok=True)


def trim_white(im: Image.Image, pad: int = 12, bg_thresh: int = 250) -> Image.Image:
    """Trim uniform white borders around an RGB/RGBA image."""
    if im.mode == "RGBA":
        # Composite onto white for bounding box detection if opaque background
        arr = np.array(im)
        if arr[:, :, 3].min() < 250:
            # True transparent image: trim by alpha > 5
            ys, xs = np.where(arr[:, :, 3] > 5)
            if len(xs) == 0:
                return im
            x0 = max(0, xs.min() - pad)
            y0 = max(0, ys.min() - pad)
            x1 = min(im.width, xs.max() + 1 + pad)
            y1 = min(im.height, ys.max() + 1 + pad)
            return im.crop((x0, y0, x1, y1))
        im = im.convert("RGB")
    arr = np.array(im.convert("RGB"))
    non_white = np.any(arr < bg_thresh, axis=2)
    ys, xs = np.where(non_white)
    if len(xs) == 0:
        return im
    x0 = max(0, xs.min() - pad)
    y0 = max(0, ys.min() - pad)
    x1 = min(im.width, xs.max() + 1 + pad)
    y1 = min(im.height, ys.max() + 1 + pad)
    return im.crop((x0, y0, x1, y1))


def prepare_logos():
    print("[1/4] Preparing HITSZ official logos...")
    with zipfile.ZipFile(os.path.join("ppt", "结题答辩.pptx")) as z:
        raw = z.read("ppt/media/image3.png")
    tmp_path = os.path.join(OUT_DIR, "_raw_logo.png")
    with open(tmp_path, "wb") as f:
        f.write(raw)
    im = Image.open(tmp_path).convert("RGBA")
    im_cropped = trim_white(im, pad=6)
    blue_path = os.path.join(OUT_DIR, "hitsz_logo_blue.png")
    im_cropped.save(blue_path)

    # Create pure white variant preserving antialiased alpha channel
    arr = np.array(im_cropped)
    white_arr = arr.copy()
    white_arr[:, :, 0] = 255
    white_arr[:, :, 1] = 255
    white_arr[:, :, 2] = 255
    white_path = os.path.join(OUT_DIR, "hitsz_logo_white.png")
    Image.fromarray(white_arr, mode="RGBA").save(white_path)
    os.remove(tmp_path)
    print("  Saved:", blue_path, im_cropped.size)


def prepare_thesis_figures():
    print("[2/4] Rendering & trimming thesis figures...")
    pdf_map = {
        "fig1-1_总体框架.pdf": "fig1_1_roadmap.png",
        "数据预处理与标签化.pdf": "fig2_1_preprocess.png",
        "数据管线概览.pdf": "fig3_1_sft_pipeline.png",
        "自动化指令演化.pdf": "fig3_2_evol.png",
        "rl_rollout_rm.pdf": "fig4_1_rl_rm.png",
        "fig4-2_sqrt_reward.pdf": "fig4_2_sqrt.png",
        "fig5-1_风险类型.pdf": "fig5_1_risks.png",
    }
    for src, dst in pdf_map.items():
        doc = pymupdf.open(os.path.join("figures", src))
        pix = doc[0].get_pixmap(dpi=360, alpha=False)
        im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        im = trim_white(im, pad=14)
        out_p = os.path.join(OUT_DIR, dst)
        im.save(out_p)
        print(f"  PDF -> {dst}: {im.size}")

    png_map = {
        "ppl_distribution.png": "fig2_2_ppl_dist.png",
        "ppl_threshold_selection.png": "fig2_3_ppl_thresh.png",
        "fig2-4_data_ratio.png": "fig2_4_data_ratio.png",
        "fig2-6_cpt_ppl.png": "fig2_6_cpt_ppl.png",
        "dft_gradient.png": "fig3_3_dft_grad.png",
        "fig4-3_ppo_reward.png": "fig4_3_ppo_reward.png",
        "fig4-4_grpo_reward.png": "fig4_4_grpo_reward.png",
        "fig4-5_entropy_collapse.png": "fig4_5_entropy.png",
        "fig5-2_token_char_split.png": "fig5_2_tok_char.png",
        "fig5-3_gradient_saliency.png": "fig5_3_saliency.png",
        "fig5-4_dpo_training_curves.png": "fig5_4_dpo_curves.png",
    }
    for src, dst in png_map.items():
        im = Image.open(os.path.join("figures", src))
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[3])
            im = bg
        im = trim_white(im, pad=12)
        out_p = os.path.join(OUT_DIR, dst)
        im.save(out_p)
        print(f"  PNG -> {dst}: {im.size}")


def render_latex_equation(name: str, latex_body: str, dpi: int = 550):
    """Compile a LaTeX math snippet via xelatex and convert to transparent PNG."""
    tex_template = r"""\documentclass[12pt]{article}
\usepackage[paperwidth=18cm,paperheight=8cm,margin=0.2cm]{geometry}
\usepackage{amsmath,amssymb,bm}
\usepackage{xcolor}
\usepackage{xeCJK}
\setCJKmainfont{SimHei}
\pagestyle{empty}
\definecolor{hitnavy}{HTML}{003B66}
\definecolor{ink}{HTML}{18222D}
\definecolor{brick}{HTML}{A62B2B}
\begin{document}
\color{ink}
""" + latex_body + r"""
\end{document}
"""
    tmpdir = tempfile.mkdtemp(prefix="eq_")
    try:
        tex_path = os.path.join(tmpdir, "eq.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_template)
        res = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "eq.tex"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
        )
        pdf_path = os.path.join(tmpdir, "eq.pdf")
        if not os.path.exists(pdf_path):
            raise RuntimeError(f"xelatex failed for {name}:\n{res.stdout[-800:]}")
        doc = pymupdf.open(pdf_path)
        pix = doc[0].get_pixmap(dpi=dpi, alpha=True)
        im = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
        im = trim_white(im, pad=8)
        out_path = os.path.join(OUT_DIR, f"{name}.png")
        im.save(out_path)
        print(f"  EQ  -> {name}.png: {im.size}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def prepare_equations():
    print("[3/4] Compiling LaTeX mathematical equations...")
    equations = {
        "eq_sft_quality": r"""
\[
\begin{aligned}
Q(x, y) &= 0.12\,q_1 + 0.28\,q_2 + {\color{hitnavy}\mathbf{0.36\,q_3}} + 0.24\,q_4 \\[4pt]
\mathrm{accept}(x, y) &= \mathbb{I}[Q \ge 0.75] \cdot {\color{brick}\mathbb{I}[\mathcal{F}^{-}(y)=\varnothing]} \cdot \mathbb{I}[q_3 \ge 0.6] \cdot \mathbb{I}[q_4 \ge 0.8]
\end{aligned}
\]
""",
        "eq_dft": r"""
\[
\begin{aligned}
\text{标准 CE：}\quad & \nabla_\theta \ell_t^{\mathrm{CE}} = -\frac{1}{p_t}\nabla_\theta p_t \;\;\Longrightarrow\;\; g_{\mathrm{CE}}(p) = 1 - p \\[5pt]
\text{动态微调 DFT：}\quad & \mathcal{L}_{\mathrm{DFT}}(\theta) = \mathbb{E}\!\Bigl[-\sum_{t=1}^{|y^*|} {\color{hitnavy}\mathrm{sg}(p_t)}\,\log p_t\Bigr] \\[2pt]
& \nabla_\theta \ell_t^{\mathrm{DFT}} = -\mathrm{sg}(p_t)\cdot\frac{1}{p_t}\nabla_\theta p_t = -\nabla_\theta p_t \;\;\Longrightarrow\;\; {\color{hitnavy}g_{\mathrm{DFT}}(p) = p(1 - p)}
\end{aligned}
\]
""",
        "eq_stylerm": r"""
\[
\begin{aligned}
\alpha_{j,t} &= \mathrm{softmax}_t\!\left(\frac{(\mathbf{W}_Q\mathbf{h} + \mathbf{e}_j)^\top \mathbf{W}_K \mathbf{H}_t}{\sqrt{d_a}}\right), \qquad \mathbf{z}_j = \sum_{t=1}^{T}\alpha_{j,t}\,\mathbf{W}_V\mathbf{H}_t \\[5pt]
r(x, o) &= \frac{1}{3}\sum_{j \in \{\mathrm{elab},\,\mathrm{warn},\,\mathrm{role}\}} {\color{hitnavy}\sqrt{P_j(c_j \mid x, o)}} \;\in [0, 1]
\end{aligned}
\]
""",
        "eq_grpo": r"""
\[
\hat{A}_i = \frac{r_i - \mu(r)}{\sigma(r) + \epsilon_{\mathrm{std}}}, \qquad
\mathrm{clip}\!\bigl(\rho_{i,t},\; 1 - \varepsilon_{\mathrm{low}},\; {\color{hitnavy}1 + \varepsilon_{\mathrm{high}}}\bigr)
\quad (\varepsilon_{\mathrm{low}} = 0.20,\;\; {\color{hitnavy}\varepsilon_{\mathrm{high}} = 0.28})
\]
""",
        "eq_recovery_margin": r"""
\[
s_k = x \oplus h_{\le k}, \qquad
m_\theta(s_k) = \beta \Bigl[ S_\theta^{\mathrm{avg}}(s_k, r_k) - S_\theta^{\mathrm{avg}}(s_k, u_k) \Bigr], \quad
{\color{brick}m_\theta(s_k) < 0 \;\Rightarrow\; \text{同状态偏好反转}}
\]
""",
        "eq_prefix_cancel": r"""
\[
\log \frac{\pi_\theta(h_{\le k}\oplus r_k \mid x)}{\pi_\theta(h_{\le k}\oplus u_k \mid x)}
= \log \frac{\cancel{\pi_\theta(h_{\le k}\mid x)}\,\pi_\theta(r_k \mid s_k)}{\cancel{\pi_\theta(h_{\le k}\mid x)}\,\pi_\theta(u_k \mid s_k)}
= {\color{hitnavy}\log \frac{\pi_\theta(r_k \mid s_k)}{\pi_\theta(u_k \mid s_k)}}
\]
""",
        "eq_hsw": r"""
\[
\begin{aligned}
\phi_i &= \nu + (1-\nu)\,\frac{|\mathcal{B}_{\mathrm{rec}}|\exp({\color{brick}-m_i/\tau})}{\sum_{j\in\mathcal{B}_{\mathrm{rec}}}\exp(-m_j/\tau)}, \qquad
\psi_t = \frac{1+\zeta^{t-1}}{2}\Bigl(1 - \max_{t'}\cos\bigl(\mathbf{e}(y_t), \mathbf{e}(\bar{y}_{t'})\bigr)\Bigr) \\[6pt]
\mathcal{L}_{\mathrm{HSW}}(\theta) &= -\mathbb{E}_{(s_i,y_w,y_l)}\!\left[\log\sigma\!\left(\beta\sum_{t} {\color{hitnavy}w_{i,t}^{(w)}}\log\frac{\pi_\theta(y_{w,t}\mid s_i,y_{w,<t})}{\pi_{\mathrm{ref}}(y_{w,t}\mid s_i,y_{w,<t})} - \beta\sum_{t} {\color{hitnavy}w_{i,t}^{(l)}}\log\frac{\pi_\theta(y_{l,t}\mid s_i,y_{l,<t})}{\pi_{\mathrm{ref}}(y_{l,t}\mid s_i,y_{l,<t})}\right)\right]
\end{aligned}
\]
""",
    }
    # Note: \cancel needs cancel package; let's handle eq_prefix_cancel cleanly without \cancel or include \usepackage{cancel}
    for name, body in equations.items():
        if "\\cancel" in body:
            body_fixed = body.replace("\\cancel{\\pi_\\theta(h_{\\le k}\\mid x)}\\,", "\\pi_\\theta(h_{\\le k}\\mid x)\\,")
            render_latex_equation(name, body_fixed)
        else:
            render_latex_equation(name, body)


def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#475569")
    ax.spines["bottom"].set_color("#475569")
    ax.grid(axis="y", linestyle="--", linewidth=0.6, color="#CBD5E1", alpha=0.8)
    ax.set_axisbelow(True)


def prepare_charts():
    print("[4/4] Generating publication-style supplementary charts...")
    NAVY = "#004F80"
    SLATE_BLUE = "#4B799E"
    LIGHT_SLATE = "#94A3B8"
    BRICK = "#A62B2B"
    TEAL = "#2A6F64"

    # Chart 1: SFT Pipeline Ablation Drops (Delta pp on 3 core benchmarks)
    fig, ax = plt.subplots(figsize=(6.2, 3.3), dpi=300)
    variants = [
        "去除质量筛选\n(全量 9.3w 候选)",
        "去除指令演化\n(仅基础指令 6.8w)",
        "去除知识图谱\n(单片段直接生成)",
        "去除专家种子\n(TF-IDF + 通用模板)",
    ]
    d_pqa = [-2.2, -3.1, -2.5, -4.9]
    d_fd = [-4.7, -8.7, -7.0, -7.7]
    d_reg = [-5.0, -6.0, -6.7, -11.0]

    y = np.arange(len(variants))
    h = 0.25
    b1 = ax.barh(y + h, d_pqa, h, label="PowerQA", color=LIGHT_SLATE, edgecolor="none")
    b2 = ax.barh(y, d_fd, h, label="FaultDiag 首因准确率", color=NAVY, edgecolor="none")
    b3 = ax.barh(y - h, d_reg, h, label="RegulationQA 依据正确性", color=BRICK, edgecolor="none")

    ax.axvline(0, color="#334155", linewidth=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(variants, fontsize=9.5, color="#1E293B")
    ax.set_xlabel("相对完整管线（6.8w）的性能变化 (pp)", fontsize=9.5, color="#1E293B")
    ax.set_xlim(-13.2, 0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", linewidth=0.6, color="#CBD5E1", alpha=0.8)
    ax.set_axisbelow(True)
    for bars in (b1, b2, b3):
        for bar in bars:
            val = bar.get_width()
            ax.text(val - 0.22, bar.get_y() + bar.get_height() / 2, f"{val:.1f}",
                    va="center", ha="right", fontsize=8, color="#1E293B", fontweight="bold")
    ax.legend(loc="lower left", frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=8.5)
    fig.tight_layout()
    p1 = os.path.join(OUT_DIR, "chart_sft_ablation.png")
    fig.savefig(p1, dpi=300)
    plt.close(fig)
    Image.open(p1).save(p1)

    # Chart 2: RoleStyle-Eval Comparison (Zero-shot vs Few-shot vs RLAIF)
    fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=300)
    cats = ["展开程度\n均值", "安全警示\n均值", "表述类型\n均值", "短板：逐项警戒\n(生产运维)", "风格命中率\nSHR", "三项联合命中\nJoint-HR"]
    zero = [57.0, 49.3, 58.5, 33.9, 54.9, 20.0]
    few = [64.0, 56.7, 67.0, 42.1, 62.6, 27.0]
    rlaif = [89.5, 88.3, 92.6, 83.2, 90.2, 76.2]

    x = np.arange(len(cats))
    w = 0.25
    r1 = ax.bar(x - w, zero, w, label="零样本 Prompt (~260 tok)", color="#CBD5E1", edgecolor="#94A3B8", linewidth=0.5)
    r2 = ax.bar(x, few, w, label="少样本 Prompt (~2100 tok)", color=SLATE_BLUE, edgecolor="none")
    r3 = ax.bar(x + w, rlaif, w, label="本文 RLAIF (~12 tok Prefix)", color=NAVY, edgecolor="none")

    style_ax(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=8.8, color="#1E293B")
    ax.set_ylabel("命中率 (%)", fontsize=9.5, color="#1E293B")
    ax.set_ylim(0, 116)
    ax.axvspan(3.55, 5.45, color="#F1F5F9", zorder=0)
    for bar in r3:
        v = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:.1f}",
                ha="center", va="bottom", fontsize=8.2, fontweight="bold", color=NAVY)
    for bar in r2:
        v = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.2, f"{v:.1f}",
                ha="center", va="bottom", fontsize=7.5, color="#475569")
    ax.legend(loc="upper center", ncol=3, frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=8.1)
    fig.tight_layout()
    p2 = os.path.join(OUT_DIR, "chart_rolestyle.png")
    fig.savefig(p2, dpi=300)
    plt.close(fig)

    # Chart 3: Counter Data Trade-off Curve (0% to 30%)
    fig, ax1 = plt.subplots(figsize=(5.6, 3.1), dpi=300)
    ratios = [0, 10, 15, 20, 25, 30]
    asr = [9.1, 10.0, 10.5, 11.1, 12.0, 15.0]
    orr = [14.0, 10.0, 7.0, 5.0, 4.0, 4.0]
    srr = [48.4, 48.0, 47.0, 45.9, 44.5, 40.5]

    style_ax(ax1)
    l1, = ax1.plot(ratios, orr, marker="s", linewidth=2.0, color=TEAL, label="过度拒答率 ORR ↓")
    l2, = ax1.plot(ratios, asr, marker="o", linewidth=2.0, color=BRICK, label="攻击成功率 ASR ↓")
    ax1.axvline(20, color=NAVY, linestyle=":", linewidth=1.3)
    ax1.scatter([20, 20], [5.0, 11.1], s=55, zorder=5, facecolors="none", edgecolors=NAVY, linewidths=1.8)
    ax1.annotate("最优权衡点 20%\n(ORR 5.0%, ASR 11.1%)", xy=(20, 5.0), xytext=(12.5, 1.5),
                 fontsize=8.2, color=NAVY, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.0))

    ax2 = ax1.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color(SLATE_BLUE)
    l3, = ax2.plot(ratios, srr, marker="^", linestyle="--", linewidth=1.8, color=SLATE_BLUE, label="安全恢复率 SRR ↑ (右轴)")

    ax1.set_xlabel("Counter Data 占第二阶段比例 (%)", fontsize=9.2, color="#1E293B")
    ax1.set_ylabel("ORR / ASR (%)", fontsize=9.2, color="#1E293B")
    ax2.set_ylabel("SRR (%)", fontsize=9.2, color=SLATE_BLUE)
    ax1.set_ylim(0, 17.5)
    ax2.set_ylim(36, 52)
    ax1.set_xticks(ratios)

    lines = [l1, l2, l3]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=8.0)
    fig.tight_layout()
    p3 = os.path.join(OUT_DIR, "chart_counter_ratio.png")
    fig.savefig(p3, dpi=300)
    plt.close(fig)

    # Chart 4: External Comparison (Qwen2.5-7B-Instruct vs Qwen-Max vs Ours)
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(8.6, 3.15), dpi=300, gridspec_kw={"width_ratios": [1.35, 1.0]})

    m_left = ["PowerQA\n知识问答↑", "FaultDiag\n首因准确率↑", "RegulationQA\n依据正确性↑", "RoleStyle\n风格命中率↑", "安全恢复率\nSRR↑"]
    q7b_l = [52.6, 30.3, 18.3, 56.3, 6.4]
    qmax_l = [73.5, 54.7, 52.0, 69.0, 12.6]
    ours_l = [81.2, 61.3, 77.0, 89.1, 53.4]

    xl = np.arange(len(m_left))
    wl = 0.25
    ax_l.bar(xl - wl, q7b_l, wl, label="Qwen2.5-7B-Instruct", color="#CBD5E1", edgecolor="#94A3B8", linewidth=0.5)
    b_qm = ax_l.bar(xl, qmax_l, wl, label="Qwen-Max (教师模型)", color=SLATE_BLUE)
    b_ou = ax_l.bar(xl + wl, ours_l, wl, label="本文最终模型 (7B)", color=NAVY)
    style_ax(ax_l)
    ax_l.set_xticks(xl)
    ax_l.set_xticklabels(m_left, fontsize=8.4, color="#1E293B")
    ax_l.set_ylabel("正向指标 (%)", fontsize=9.0, color="#1E293B")
    ax_l.set_ylim(0, 114)
    ax_l.set_title("(a) 领域能力、风格控制与安全恢复对比 (越高越好)", fontsize=9.3, fontweight="bold", color="#1E293B", pad=6)
    for bar in b_ou:
        v = bar.get_height()
        ax_l.text(bar.get_x() + bar.get_width() / 2, v + 1.3, f"{v:.1f}",
                  ha="center", va="bottom", fontsize=7.8, fontweight="bold", color=NAVY)

    m_right = ["不安全回答率\nURR ↓", "攻击成功率\nASR ↓", "过度拒答率\nORR ↓"]
    q7b_r = [24.5, 62.4, 9.7]
    qmax_r = [9.5, 31.4, 4.0]
    ours_r = [1.5, 7.9, 5.0]

    xr = np.arange(len(m_right))
    ax_r.bar(xr - wl, q7b_r, wl, label="Qwen2.5-7B-Instruct", color="#CBD5E1", edgecolor="#94A3B8", linewidth=0.5)
    b_qmr = ax_r.bar(xr, qmax_r, wl, label="Qwen-Max (教师模型)", color="#D97757")
    b_our = ax_r.bar(xr + wl, ours_r, wl, label="本文最终模型 (7B)", color=BRICK)
    style_ax(ax_r)
    ax_r.set_xticks(xr)
    ax_r.set_xticklabels(m_right, fontsize=8.4, color="#1E293B")
    ax_r.set_ylabel("风险与误拒率 (%)", fontsize=9.0, color="#1E293B")
    ax_r.set_ylim(0, 76)
    ax_r.set_title("(b) 安全风险暴露与过度拒答对比 (越低越好)", fontsize=9.3, fontweight="bold", color="#1E293B", pad=6)
    for bar in b_our:
        v = bar.get_height()
        ax_r.text(bar.get_x() + bar.get_width() / 2, v + 1.0, f"{v:.1f}",
                  ha="center", va="bottom", fontsize=8.0, fontweight="bold", color=BRICK)
    for bar in b_qmr:
        v = bar.get_height()
        ax_r.text(bar.get_x() + bar.get_width() / 2, v + 1.0, f"{v:.1f}",
                  ha="center", va="bottom", fontsize=7.5, color="#64748B")

    ax_l.legend(loc="upper center", ncol=3, frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=7.4)
    ax_r.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=7.6)
    fig.tight_layout()
    p4 = os.path.join(OUT_DIR, "chart_external_compare.png")
    fig.savefig(p4, dpi=300)
    plt.close(fig)
    print("  Saved all 4 supplementary charts.")


if __name__ == "__main__":
    prepare_logos()
    prepare_thesis_figures()
    prepare_equations()
    prepare_charts()
    print("ALL ASSETS PREPARED SUCCESSFULLY.")
