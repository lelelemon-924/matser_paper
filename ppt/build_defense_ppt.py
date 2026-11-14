# -*- coding: utf-8 -*-
"""
Master entry script to build ultra-clean, large-font `ppt/硕士答辩.pptx` (34 slides, ~25 min defense)
and export synchronized speaker script `ppt/答辩讲稿.md`.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation
from pptx.util import Inches
from ppt_helpers import SLIDE_W, SLIDE_H
from slides_sec1_2 import build_slides_1_to_11
from slides_sec3_4 import build_slides_12_to_23
from slides_sec5_6 import build_slides_24_to_34

SLIDE_META = [
    (1, "封面"),
    (2, "汇报提纲"),
    (3, "第一部分：研究背景与总体技术路线"),
    (4, "1.1 电力领域大语言模型面临的挑战"),
    (5, "1.2 总体技术路线：四阶段递进训练框架"),
    (6, "1.3 主要研究工作与创新点"),
    (7, "第二部分：电力领域数据体系构建与持续预训练"),
    (8, "2.1 电力数据体系、三级去重与评测隔离"),
    (9, "2.2 基于种子模型困惑度（PPL）的数据筛选"),
    (10, "2.3 CPT 领域—通用混合配比实验"),
    (11, "2.4 CPT 训练收敛与通用能力保持验证"),
    (12, "第三部分：场景原生指令合成与动态微调"),
    (13, "3.1 六模块场景原生指令合成管线"),
    (14, "3.2 图谱逆频采样与自动化指令演化"),
    (15, "3.3 一票否决质量筛选与两阶段微调配比"),
    (16, "3.4 动态微调（DFT）与 CPT 先验协同机理"),
    (17, "3.5 SFT 实验验证：2×2 对比与管线消融"),
    (18, "3.6 故障诊断真实工单案例对比"),
    (19, "第四部分：面向用户角色的回答风格强化学习对齐"),
    (20, "4.1 提问角色与语料解耦：风格组合与 Prefix"),
    (21, "4.2 风格判别模型 StyleRM-7B"),
    (22, "4.3 开根号奖励与 GRPO + Clip-Higher 训练"),
    (23, "4.4 风格评测结果与跨角色输出对比"),
    (24, "第五部分：面向电力安全合规的深层 DPO 对齐"),
    (25, "5.1 电力安全风险体系与中途偏好反转"),
    (26, "5.2 同状态偏好数据：Recovery 与 Counter Data"),
    (27, "5.3 预填充前缀截断机理：Token 边界 vs. 字符边界"),
    (28, "5.4 困难状态加权（HS-Weighting）与两阶段训练"),
    (29, "5.5 安全对齐实验结果与预填充恢复对比"),
    (30, "5.6 四阶段跨阶段能力保持评测"),
    (31, "5.7 与通用指令模型及教师模型的综合对比"),
    (32, "6.1 全文总结"),
    (33, "6.2 研究局限与未来展望"),
    (34, "致谢"),
]


def main():
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)

    build_slides_1_to_11(prs)
    build_slides_12_to_23(prs)
    build_slides_24_to_34(prs)

    assert len(prs.slides) == 34, f"Expected 34 slides, got {len(prs.slides)}"

    out_pptx = os.path.join("ppt", "硕士答辩.pptx")
    prs.save(out_pptx)
    print(f"[OK] Saved {out_pptx} ({len(prs.slides)} slides)")

    out_md = os.path.join("ppt", "答辩讲稿.md")
    lines = [
        "# 硕士学位论文答辩讲稿（25 分钟极简大字版）",
        "",
        "- **论文题目**：面向数字电网知识服务的大语言模型训练与对齐方法研究",
        "- **答辩人**：赵乐森（指导教师：许鋆 教授）",
        "- **总页数**：34 页（含封面、目录、致谢及 5 页章节分隔页；正文内容共 26 页，每页仅聚焦一个核心图表或结论，全程约 25 分钟）",
        "",
        "---",
        "",
    ]
    for idx, slide in enumerate(prs.slides):
        pno, ptitle = SLIDE_META[idx]
        note_txt = slide.notes_slide.notes_text_frame.text.strip()
        lines.append(f"## P{pno:02d}  {ptitle}")
        lines.append("")
        lines.append(note_txt)
        lines.append("")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Saved {out_md}")


if __name__ == "__main__":
    main()
