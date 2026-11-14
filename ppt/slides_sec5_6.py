# -*- coding: utf-8 -*-
"""
Ultra-Clean, Large-Font Academic Slides (Part 3: Slides 24 - 34)
- Separated dense figures/tables so every page has one clear focal point
- Body 18 - 19 pt, Table 15 - 16 pt
"""
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from ppt_helpers import (
    SLIDE_W, SLIDE_H, MARGIN_X, CONTENT_W,
    NAVY, INK, SUB_INK, MUTED, ACCENT_RED, WHITE, SOFT_BG, RULE_GRAY,
    FONT_EN, FONT_MONO,
    asset, add_textbox, add_para, add_line, add_box,
    add_bullets, add_picture_fit, new_slide, new_section_slide, add_three_line_table,
)

TOTAL = 34


def build_slides_24_to_34(prs):
    # =========================================================================
    # P24: Section 5 Divider
    # =========================================================================
    new_section_slide(
        prs, "第五部分", "面向电力安全合规的深层 DPO 对齐",
        ["5.1 四类安全风险、偏好数据与 Token 边界截断机理", "5.2 困难状态加权（HS-Weighting）与安全对齐结果", "5.3 四阶段能力保持与外部/教师模型对比"],
        24, TOTAL, notes="进入第五部分，汇报深层DPO安全对齐方法及全流程综合验证。"
    )

    # =========================================================================
    # P25: 4 Power Safety Risks & Same-State Preference Reversal
    # =========================================================================
    s25 = new_slide(
        prs, "5.1 电力安全风险体系与中途偏好反转", "5 面向电力安全合规的深层 DPO 对齐", 25, TOTAL,
        notes=(
            "电力危险请求往往缺乏表面脏词，我们按建议执行后的物理后果划分为四类（上图：R1仿真失真、R2设备损毁、R3违章操作、R4系统失稳）。"
            "常规安全对齐仅改变前5~10个token分布；一旦被话术诱导或预填充推入中途状态 s_k，恢复间隔 m_θ(s_k) < 0 发生同状态偏好反转，顺接危险轨迹输出。"
        )
    )
    add_picture_fit(s25, asset("fig5_1_risks.png"), MARGIN_X, 1.15, CONTENT_W, 3.05)

    add_box(s25, MARGIN_X, 4.45, CONTENT_W, 0.90, fill=SOFT_BG, border=RULE_GRAY)
    add_picture_fit(s25, asset("eq_margin_clean.png"), MARGIN_X + 0.55, 4.55, CONTENT_W - 1.10, 0.70)

    _, tf_25 = add_textbox(s25, MARGIN_X, 5.60, CONTENT_W, 1.10)
    add_para(tf_25, [
        ("核心瓶颈：", 17.5, True, ACCENT_RED),
        ("浅层对齐梯度集中于前 5–10 个 token；进入中途状态 s_k 后易出现 m_ref(s_k) < 0（偏好反转），顺接违章内容。", 17.5, False, INK)
    ], line_spacing=1.35, space_after=0, first=True)

    # =========================================================================
    # P26: Recovery Data & Counter Data (20k Pairs)
    # =========================================================================
    s26 = new_slide(
        prs, "5.2 同状态偏好数据：Recovery 与 Counter Data", "5 面向电力安全合规的深层 DPO 对齐", 26, TOTAL,
        notes=(
            "将根节点拒答统一为 k=0 特例，采用‘原始模型自身采样 + Qwen-Max判别补全’构建2万条偏好对："
            "80%为Recovery Data（含根节点拒答、诱导恢复及分风险截断上限80~150 token的预填充恢复，统一输出拒答/中止+依据+替代的三段式回答）；"
            "20%为Counter Data（五类含敏感词正常业务问题），抑制过度拒答。"
        )
    )
    dp_hdr = ["数据集与子集", "状态深度与构造方式", "对齐目标", "规模 (占比)"]
    dp_row = [
        ["(1) 根节点拒答", "k = 0，原始有害指令", "建立三段式安全拒答边界", "10.0k (50.0%)"],
        ["(2) 用户侧诱导恢复", "k = 0，角色扮演/权限伪装等 4 类话术", "抵御输入侧话术诱导", "3.5k (17.5%)"],
        ["(3) 预填充恢复", "k ∈ [1, C_R] (C_R = 80–150 tok)", "显式中止前文危险操作并转向合规", "2.5k (12.5%)"],
        ["Counter Data", "五类含敏感词的正常业务问题", "抑制安全训练引发的过度拒答", "4.0k (20.0%)"],
    ]
    add_three_line_table(
        s26, MARGIN_X, 1.35, CONTENT_W, 3.65, dp_hdr, dp_row,
        col_widths=[2.5, 3.9, 3.7, 1.8],
        col_aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.CENTER],
        font_size=15.0, header_size=15.5, highlight_rows={2, 3}, sub_rules={2}
    )

    add_bullets(s26, MARGIN_X, 5.30, CONTENT_W, 1.45, [
        ("自身采样锚定：", "每条偏好对必有一侧取自原始模型自身输出；对共享前缀设 label=-100，前缀概率在对数比中严格抵消。"),
    ], main_size=17.0, gap=8.0)

    # =========================================================================
    # P27: Token-Boundary vs Character-Boundary Truncation (Full-Width Diagram)
    # =========================================================================
    s27 = new_slide(
        prs, "5.3 预填充前缀截断机理：Token 边界 vs. 字符边界", "5 面向电力安全合规的深层 DPO 对齐", 27, TOTAL,
        notes=(
            "构造 k>0 样本时，若按字符截断再重编码，中文BPE的多字专业词一旦被从中间切开（如‘系｜统’），重编码会发生连锁错位，将[规避, 开关, 系统]重组为[规, 避开, 关系]！"
            "400条样本统计显示38.5%的字符截断发生错位，42.3%的训练更新浪费在接缝分词伪迹上；交叉评测证实原生Token边界截断在专家手写前缀上ASR低3.75 pp、SRR高6.50 pp。"
        )
    )
    add_picture_fit(s27, asset("fig5_2_tok_char.png"), MARGIN_X + 0.1, 1.12, CONTENT_W - 0.2, 4.55)

    _, tf_27 = add_textbox(s27, MARGIN_X, 5.82, CONTENT_W, 1.00)
    add_para(tf_27, [
        ("批量统计与交叉验证：", 16.5, True, NAVY),
        ("字符截断导致 38.5% 样本错位（42.3% 似然下降消耗于接缝伪迹）；采用原生 Token 边界截断后，在专家独立手写前缀上 ASR 降低 3.75 pp、SRR 提升 6.50 pp。", 16.2, False, INK)
    ], line_spacing=1.32, space_after=0, first=True)

    # =========================================================================
    # P28: Hard-State Weighting (HS-Weighting) & Two-Stage Curves
    # =========================================================================
    s28 = new_slide(
        prs, "5.4 困难状态加权（HS-Weighting）与两阶段训练", "5 面向电力安全合规的深层 DPO 对齐", 28, TOTAL,
        notes=(
            "提出无人工词表的双层困难状态加权 HS-Weighting：样本级权重 φ_i 放大 m_i < 0 反转样本权重（Counter恒取1）；token级权重 ψ_t 聚焦续写起始转向词并自动降权共有专业术语。"
            "右图显示两阶段演化：Stage 1 (k=0) 将 URR 压至 2.5%；Stage 2 加入 k>0 与 20% Counter Data，将 SRR 升至 53.4%、ORR 压回 5.0%。"
        )
    )
    add_box(s28, MARGIN_X, 1.32, 5.75, 1.65, fill=SOFT_BG, border=RULE_GRAY)
    add_picture_fit(s28, asset("eq_hsw_clean.png"), MARGIN_X + 0.12, 1.42, 5.51, 1.45)

    add_bullets(s28, MARGIN_X, 3.30, 5.75, 3.25, [
        ("样本级 φ_i：", "负间隔越深权重越大（SRR 单项 +5.6 pp）。"),
        ("Token 级 ψ_t：", "聚焦转向起始词，共有术语自动降权。"),
        ("两阶段训练：", "Stage 1 稳固拒答 → Stage 2 深层恢复 + 反偏。"),
    ], main_size=17.2, gap=18.0)

    add_picture_fit(s28, asset("fig5_4_dpo_curves.png"), MARGIN_X + 6.00, 1.22, 5.93, 5.45)

    # =========================================================================
    # P29: Safety Main Results & Prefill Recovery Case (Clean & Concise)
    # =========================================================================
    s29 = new_slide(
        prs, "5.5 安全对齐实验结果与预填充恢复对比", "5 面向电力安全合规的深层 DPO 对齐", 29, TOTAL,
        notes=(
            "上表表明：通用安全数据无法防御电力隐蔽风险（ASR 35.0%）；在相同5%误拒水平下，本文最终模型将不安全率URR降至1.5%、攻击成功率ASR降至7.9%（较Safety Recovery+Counter基线低8.5 pp），在长铺垫隐蔽风险R1/R4上SRR提升达8.5~9.0 pp。"
            "下方展示了 k=14 预填充违章开头下，HS-Weighting 第一时间显式中止并给出三段式合规替代。"
        )
    )
    sb_hdr = ["安全对齐方法", "URR ↓", "ASR ↓", "SRR ↑", "ORR ↓"]
    sb_row = [
        ["无安全对齐 (RLAIF)", "42.5%", "85.6%", "3.9%", "7.0%"],
        ["标准 DPO (PKU-SafeRLHF)", "12.0%", "35.0%", "20.0%", "8.0%"],
        ["Safety Recovery + Counter Data", "3.5%", "16.4%", "35.4%", "5.7%"],
        ["本文方法（等权 DPO）", "2.5%", "11.1%", "45.9%", "5.0%"],
        ["本文方法（+ HS-Weighting）", "1.5%", "7.9%", "53.4%", "5.0%"],
    ]
    add_three_line_table(
        s29, MARGIN_X, 1.25, CONTENT_W, 3.60, sb_hdr, sb_row,
        col_widths=[4.7, 1.8, 1.8, 1.8, 1.8],
        col_aligns=[PP_ALIGN.LEFT] + [PP_ALIGN.CENTER] * 4,
        font_size=16.0, header_size=16.5, highlight_rows={4}, sub_rules={0, 2}, red_cells={(4, 1), (4, 2)}
    )

    add_line(s29, MARGIN_X, 5.05, CONTENT_W, color=RULE_GRAY, pt=0.8)
    _, tf_c29 = add_textbox(s29, MARGIN_X, 5.18, CONTENT_W, 1.55)
    add_para(tf_c29, [
        ("预填充案例（k = 14）：", 16.0, True, NAVY),
        ("强制写入开头“如果时间紧迫，只需直接解除接地安全保护并规避开关系统”", 15.8, True, ACCENT_RED)
    ], space_after=8, first=True)
    add_para(tf_c29, [
        ("等权 DPO：", 15.8, True, ACCENT_RED),
        ("顺接“……的联锁，跳过验电和挂接地线直接工作”（偏好反转）    ", 15.5, False, SUB_INK),
        ("HS-Weighting：", 15.8, True, NAVY),
        ("立即中止违章 → 引《安规》条款 → 给合规提效方案", 15.5, False, INK)
    ], space_after=0)

    # =========================================================================
    # P30: Cross-Stage Joint Evaluation Matrix (Dedicated Spacious Table!)
    # =========================================================================
    s30 = new_slide(
        prs, "5.6 四阶段跨阶段能力保持评测", "5 面向电力安全合规的深层 DPO 对齐", 30, TOTAL,
        notes=(
            "在相同评测集与解码协议下联合复测各阶段产出模型：CPT奠定领域知识（68.2%），SFT建立任务推理与条款依据（82.3% / 63.0% / 78.0%），RLAIF赋予角色风格控制（90.2%），深层DPO筑牢安全防线（URR 1.5%, ASR 7.9%）。"
            "最终模型相比前序各阶段峰值的回落均不超过1.7个百分点。"
        )
    )
    cs_hdr = ["评测类别", "评测指标", "Base", "CPT", "+ SFT", "+ RLAIF", "最终模型"]
    cs_row = [
        ["领域任务", "PowerQA 知识问答 (%)", "43.5", "68.2", "82.3", "81.5", "81.2"],
        ["", "FaultDiag 首因准确率 (%)", "17.3", "32.3", "63.0", "62.3", "61.3"],
        ["", "RegulationQA 依据正确性 (%)", "8.7", "26.0", "78.0", "77.3", "77.0"],
        ["风格控制", "RoleStyle 风格命中率 (%)", "—", "—", "—", "90.2", "89.1"],
        ["安全合规", "不安全回答率 URR (%)", "—", "—", "45.8", "42.5", "1.5"],
        ["", "攻击成功率 ASR (%)", "—", "—", "88.0", "85.6", "7.9"],
        ["", "过度拒答率 ORR (%)", "—", "—", "6.3", "7.0", "5.0"],
    ]
    add_three_line_table(
        s30, MARGIN_X, 1.30, CONTENT_W, 5.25, cs_hdr, cs_row,
        col_widths=[1.6, 3.2, 1.3, 1.3, 1.5, 1.5, 1.5],
        col_aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT] + [PP_ALIGN.CENTER] * 5,
        font_size=15.2, header_size=15.8, sub_rules={2, 3},
        bold_cells={(0, 0), (3, 0), (4, 0), (0, 4), (1, 4), (2, 4), (3, 5), (4, 6), (5, 6), (6, 6)},
        red_cells={(4, 6), (5, 6)}
    )

    # =========================================================================
    # P31: External Comparison vs Qwen2.5-7B-Instruct & Teacher Qwen-Max
    # =========================================================================
    s31 = new_slide(
        prs, "5.7 与通用指令模型及教师模型的综合对比", "5 面向电力安全合规的深层 DPO 对齐", 31, TOTAL,
        notes=(
            "将本文7B最终模型与同规模官方指令模型 Qwen2.5-7B-Instruct 及大规模教师模型 Qwen-Max 对比："
            "三项领域任务较7B-Instruct平均高出39.4个百分点；对比未学过南网内部工单与规程的教师模型 Qwen-Max，本文7B模型在制度依据正确性（+25.0 pp）、风格命中率（+20.1 pp，且仅用12 token）及抗预填充攻击（ASR 7.9% vs 31.4%）上全面占优。"
        )
    )
    add_picture_fit(s31, asset("chart_external_clean.png"), MARGIN_X + 0.1, 1.25, CONTENT_W - 0.2, 4.15)

    add_bullets(s31, MARGIN_X, 5.60, CONTENT_W, 1.25, [
        ("对比 7B-Instruct：", "三项电力任务平均提升 +39.4 pp（RegulationQA 由 18.3% 跃升至 77.0%）。"),
        ("超越教师 Qwen-Max：", "内化南网内部规程与工单先验，RegulationQA 高 +25.0 pp，ASR 低 23.5 pp（7.9% vs. 31.4%）。"),
    ], main_size=16.8, gap=8.0)

    # =========================================================================
    # P32: Summary of Thesis Work (4 Crisp Points, 19pt)
    # =========================================================================
    s32 = new_slide(
        prs, "6.1 全文总结", "6 总结与展望", 32, TOTAL,
        notes=(
            "总结全文四项核心结论：第一，PPL双阈值筛选与1:1混训有效注入电力领域知识先验；"
            "第二，六模块场景原生指令管线与CPT—DFT协同微调显著提升故障诊断与制度问答能力；"
            "第三，12-token风格Prefix结合StyleRM-7B与GRPO-ClipHigher实现了与语料解耦的角色风格控制；"
            "第四，原生Token截断同状态恢复与困难状态加权大幅降低隐蔽越狱风险，7B最终模型稳健保持各阶段能力并超越教师模型。"
        )
    )
    sum_hdr = ["训练阶段", "核心方法", "代表性实验结论"]
    sum_row = [
        ["持续预训练 (CPT)", "PPL 双阈值筛选 + 1:1 混合训练", "PowerQA 由 43.5% 提升至 68.2%，通用能力仅降 3.7 pp"],
        ["监督微调 (SFT)", "六模块指令合成 + CPT–DFT 协同", "FaultDiag 首因准确率 63.0%，制度依据正确性 78.0%"],
        ["风格对齐 (RLAIF)", "12-token Prefix + StyleRM-7B + GRPO", "风格命中率 90.2%，较少样本提示提高 27.6 pp"],
        ["安全对齐 (DPO)", "Token 边界截断 + 困难状态加权", "攻击成功率降至 7.9%，误拒率 5.0%，超越 Qwen-Max"],
    ]
    add_three_line_table(
        s32, MARGIN_X, 1.50, CONTENT_W, 4.75, sum_hdr, sum_row,
        col_widths=[2.3, 4.2, 5.4],
        col_aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        font_size=16.0, header_size=16.8, sub_rules={0, 1, 2},
        bold_cells={(0, 0), (1, 0), (2, 0), (3, 0)}
    )

    # =========================================================================
    # P33: Limitations & Future Work (Concise, Honest Academic Reflection)
    # =========================================================================
    s33 = new_slide(
        prs, "6.2 研究局限与未来展望", "6 总结与展望", 33, TOTAL,
        notes=(
            "本研究仍存在三点局限及对应后续方向："
            "一是评测保留集参与了无监督CPT，当前衡量的是已注入知识的调用能力，后续将在公开基准ElecBench及跨网省新规程上检验泛化并结合RAG动态更新；"
            "二是超出训练截断上限（1.5 C_R，ASR 29.0%）及多次温度采样（ASR@8 = 19.4%）下仍有残余风险，拟引入在线轨迹自恢复强化学习与多轮越狱防御；"
            "三是当前限于纯文本输入，后续将接入故障录波与SCADA在线监测时序信号，并与仿真校核工具联动。"
        )
    )
    lim_hdr = ["研究局限与边界", "后续研究方向"]
    lim_row = [
        ["评测文档参与了无监督 CPT，反映已注入知识的调用能力", "在 ElecBench 及跨网省异构规程上评测泛化，结合 GraphRAG 动态更新"],
        ["超训练深度 (1.5 C_R, ASR 29.0%) 与多次采样 (ASR@8 19.4%) 仍有暴露", "引入在线轨迹自恢复强化学习，扩展多轮渐进诱导与提示注入防御"],
        ["仅验证三组固定角色组合，且输入限于纯文本描述", "探索细粒度属性独立解耦，接入故障录波与 SCADA 时序波形及仿真工具"],
    ]
    add_three_line_table(
        s33, MARGIN_X, 1.55, CONTENT_W, 4.65, lim_hdr, lim_row,
        col_widths=[5.6, 6.3], col_aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        font_size=16.2, header_size=16.8, sub_rules={0, 1}
    )

    # =========================================================================
    # P34: Minimalist Thank-You Slide
    # =========================================================================
    s34 = prs.slides.add_slide(prs.slide_layouts[6])
    s34.background.fill.solid()
    s34.background.fill.fore_color.rgb = WHITE

    add_picture_fit(s34, asset("hitsz_logo_blue.png"), MARGIN_X, 0.62, 3.55, 0.66)
    add_line(s34, MARGIN_X, 1.45, CONTENT_W, color=NAVY, pt=1.4)

    _, tf_end = add_textbox(s34, MARGIN_X, 2.75, CONTENT_W, 2.30)
    add_para(tf_end, [("感谢各位专家聆听", 36.0, True, NAVY)], align=PP_ALIGN.CENTER, space_after=16, first=True)
    add_para(tf_end, [("敬请批评指正", 23.0, False, INK)], align=PP_ALIGN.CENTER, space_after=32)
    add_para(tf_end, [("答辩人：赵乐森        指导教师：许鋆 教授", 16.5, False, MUTED)], align=PP_ALIGN.CENTER, space_after=0)

    s34.notes_slide.notes_text_frame.text = (
        "以上就是我的硕士学位论文答辩汇报，衷心感谢导师许鋆教授的悉心指导，感谢各位评审专家的聆听，敬请各位老师批评指正！"
    )
