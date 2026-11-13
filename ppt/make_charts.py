"""生成答辩 PPT 中新增的数据图（数据均取自论文初稿.tex）。"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

for f in ("NotoSansCJKsc-Regular.otf", "NotoSansCJKsc-Bold.otf", "NotoSansCJKsc-Medium.otf"):
    p = os.path.expanduser(f"~/Library/Fonts/{f}")
    if os.path.exists(p):
        font_manager.fontManager.addfont(p)
plt.rcParams["font.family"] = "Noto Sans CJK SC"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 13

GRAY, LBLUE, BLUE = "#D8DDE3", "#BACADB", "#7391B5"
C_CPT, C_SFT, C_RL, C_DPO = "#5A7BA2", "#8FA7C4", "#7391B5", "#9A9FA6"
C_LINE3 = "#BCCADB"
C_LABEL = "#4A6A91"


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", ls="--", alpha=0.35)
    ax.set_axisbelow(True)


def bar_labels(ax, bars, fmt="{:.1f}", size=11, color="#333"):
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 1.0, fmt.format(h),
                ha="center", va="bottom", fontsize=size, color=color)


# 1. SFT 主结果：Base / CPT / CPT+SFT
def chart_sft():
    metrics = ["PowerQA 得分", "FaultDiag\n首因准确率", "RegulationQA\n依据正确性"]
    data = {"Base": [43.5, 17.3, 8.7], "CPT": [68.2, 32.3, 26.0], "CPT+SFT（DFT）": [82.3, 63.0, 78.0]}
    colors = [GRAY, LBLUE, BLUE]
    fig, ax = plt.subplots(figsize=(6.6, 3.6), dpi=220)
    w = 0.26
    for i, (k, v) in enumerate(data.items()):
        bars = ax.bar([x + (i - 1) * w for x in range(3)], v, w, label=k, color=colors[i])
        bar_labels(ax, bars, size=10.5)
    ax.set_xticks(range(3), metrics)
    ax.set_ylim(0, 95)
    ax.set_ylabel("%")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.13), fontsize=11.5)
    style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "chart_sft_main.png"), transparent=False, facecolor="white")
    plt.close(fig)


# 2. 风格评测：九个目标取值的命中率 + SHR / Joint-HR
def chart_style():
    vals = ["精简", "适中", "详尽", "基础\n提醒", "前置\n提醒", "逐项\n警戒", "研讨型", "指令型", "裁定型"]
    zero = [41.4, 66.1, 63.6, 58.2, 55.7, 33.9, 45.0, 78.2, 52.1]
    few = [52.5, 70.4, 69.3, 64.6, 63.2, 42.1, 55.4, 83.9, 61.8]
    rl = [92.5, 90.4, 85.7, 90.7, 91.1, 83.2, 89.3, 96.4, 92.1]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.2, 3.5), dpi=220,
                                 gridspec_kw={"width_ratios": [3.3, 1.2]})
    w = 0.27
    xs = range(len(vals))
    a1.bar([x - w for x in xs], zero, w, color=GRAY, label="零样本 Prompt")
    a1.bar(list(xs), few, w, color=LBLUE, label="少样本 Prompt")
    b = a1.bar([x + w for x in xs], rl, w, color=C_RL, label="RLAIF（本文）")
    for bb in b:
        a1.text(bb.get_x() + bb.get_width() / 2, bb.get_height() + 1, f"{bb.get_height():.1f}",
                ha="center", va="bottom", fontsize=9.5, color=C_RL)
    a1.set_xticks(list(xs), vals, fontsize=11.5)
    for x0, name in [(1, "展开程度"), (4, "安全警示"), (7, "表述类型")]:
        a1.text(x0, -27, name, ha="center", fontsize=12, color="#555", fontweight="bold")
    for xl in (2.5, 5.5):
        a1.axvline(xl, color="#999", lw=0.8, ls=":")
    a1.set_ylim(0, 108)
    a1.set_ylabel("命中率（%）")
    a1.set_title("(a) 各风格目标取值的命中率", fontsize=13, loc="left")
    a1.legend(frameon=False, ncol=3, loc="lower right", fontsize=11, bbox_to_anchor=(1.0, 1.0))
    style(a1)

    names = ["SHR", "Joint-HR"]
    z, f, r = [54.9, 20.0], [62.6, 27.0], [90.2, 76.2]
    w2 = 0.26
    for i, (vv, c) in enumerate([(z, GRAY), (f, LBLUE), (r, C_RL)]):
        bars = a2.bar([x + (i - 1) * w2 for x in range(2)], vv, w2, color=c)
        bar_labels(a2, bars, size=10)
    a2.set_xticks(range(2), names, fontsize=12)
    a2.set_ylim(0, 108)
    a2.set_title("(b) 总体指标", fontsize=13)
    style(a2)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.2)
    fig.savefig(os.path.join(OUT, "chart_style.png"), facecolor="white")
    plt.close(fig)


# 3. 跨阶段能力演化
def chart_stage():
    stages = ["Base", "CPT", "+SFT", "+RLAIF", "+DPO\n(HS-W)"]
    pq = [43.5, 68.2, 82.3, 81.5, 81.2]
    fd = [17.3, 32.3, 63.0, 62.3, 61.3]
    rq = [8.7, 26.0, 78.0, 77.3, 77.0]
    asr = [None, None, 88.0, 85.6, 7.9]
    fig, ax = plt.subplots(figsize=(6.4, 3.9), dpi=220)
    ax.plot(stages, pq, "-o", color=C_CPT, lw=2.2, label="PowerQA")
    ax.plot(stages, fd, "-s", color=C_LINE3, lw=2.2, mec=C_SFT, label="FaultDiag")
    ax.plot(stages, rq, "-^", color=C_SFT, lw=2.2, label="RegulationQA")
    ax.plot(stages[2:], asr[2:], "--D", color=C_DPO, lw=2.2, label="攻击成功率 ASR")
    for x, y, dy in zip(stages[2:], asr[2:], (5, 5, 4)):
        ax.text(x, y + dy, f"{y}", color=C_DPO, ha="center", fontsize=10.5)
    ax.text(4, 84.5, "81.2", color=C_CPT, ha="center", fontsize=10.5)
    ax.text(4, 66.0, "61.3", color=C_SFT, ha="center", fontsize=10.5)
    ax.text(4.25, 73.0, "77.0", color=C_SFT, ha="center", fontsize=10.5)
    ax.set_ylim(0, 102)
    ax.set_ylabel("%")
    style(ax)
    fig.legend(*ax.get_legend_handles_labels(), frameon=False, fontsize=10.5, ncol=4,
               loc="upper center", bbox_to_anchor=(0.5, 1.0), handlelength=1.6, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(OUT, "chart_stage.png"), facecolor="white")
    plt.close(fig)


# 4. 与外部模型对比
def chart_external():
    m_up = ["PowerQA", "FaultDiag", "RegulationQA", "风格 SHR"]
    q7 = [52.6, 30.3, 18.3, 56.3]
    qm = [73.5, 54.7, 52.0, 69.0]
    me = [81.2, 61.3, 77.0, 89.1]
    m_dn = ["URR", "ASR"]
    q7d, qmd, med = [24.5, 62.4], [9.5, 31.4], [1.5, 7.9]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 3.9), dpi=220,
                                 gridspec_kw={"width_ratios": [2.3, 1.1]})
    w = 0.26
    for i, (vv, c, lab) in enumerate([(q7, GRAY, "Qwen2.5-7B-Instruct"), (qm, LBLUE, "Qwen-Max（教师）"),
                                      (me, BLUE, "本文最终模型")]):
        bars = a1.bar([x + (i - 1) * w for x in range(4)], vv, w, color=c, label=lab)
        if i == 2:
            bar_labels(a1, bars, size=9.5, color=BLUE)
        b2 = a2.bar([x + (i - 1) * w for x in range(2)], [q7d, qmd, med][i], w, color=c)
        bar_labels(a2, b2, size=9.5, color="#333" if i < 2 else BLUE)
    a1.set_xticks(range(4), m_up, fontsize=10)
    a1.set_ylim(0, 100)
    a1.set_title("领域任务与风格（越高越好）", fontsize=11.5)
    a2.set_xticks(range(2), m_dn, fontsize=10.5)
    a2.set_ylim(0, 75)
    a2.set_title("安全（越低越好）", fontsize=11.5)
    for a in (a1, a2):
        style(a)
    fig.legend(*a1.get_legend_handles_labels(), frameon=False, ncol=3, loc="upper center",
               fontsize=9.8, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(OUT, "chart_external.png"), facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    chart_sft()
    chart_style()
    chart_stage()
    chart_external()
    print("charts done")
