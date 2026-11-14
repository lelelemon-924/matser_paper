# -*- coding: utf-8 -*-
"""
Ultra-Clean, Large-Font Academic Slides (Part 2: Slides 12 - 23)
- Body bullets: 18 - 19 pt, crisp one-line statements
- Tables: 15.5 - 16 pt
- Case studies trimmed to scannable core phrases
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


def build_slides_12_to_23(prs):
    # =========================================================================
    # P12: Section 3 Divider
    # =========================================================================
    new_section_slide(
        prs, "第三部分", "场景原生指令合成与动态微调",
        ["3.1 六模块场景原生指令合成管线", "3.2 动态微调（DFT）与 CPT 先验协同", "3.3 实验验证与工单案例"],
        12, TOTAL, notes="进入第三部分，汇报场景原生指令合成与动态微调方法。"
    )

    # =========================================================================
    # P13: 6-Module SFT Pipeline Overview
    # =========================================================================
    s13 = new_slide(
        prs, "3.1 六模块场景原生指令合成管线", "3 场景原生指令合成与动态微调", 13, TOTAL,
        notes=(
            "为了不压平仿真、运维、制度等七类资料的原生推理结构，同时防止大模型自由生成产生条款幻觉，我们设计了左图的六模块合成管线："
            "以600条专家种子和4.2万条知识图谱三元组为基础，经设计逻辑提取、图遍历生成、指令演化和一票否决筛选，从9.3万候选中构建6.8万条高质量指令。"
        )
    )
    add_picture_fit(s13, asset("fig3_1_sft_pipeline.png"), MARGIN_X, 1.12, 6.20, 5.65)

    add_bullets(s13, MARGIN_X + 6.50, 1.25, 5.43, 5.40, [
        ("保留原生风格：", "在七类语料各自场景内生成，不套用统一模板。"),
        ("图谱锚定事实：", "600 专家种子提取逻辑，4.2 万条三元组约束知识边界。"),
        ("演化与筛选：", "五类算子扩展推理复杂度，9.3 万候选筛留 6.8 万条。"),
    ], main_size=18.5, gap=28.0, valign=MSO_ANCHOR.MIDDLE)

    # =========================================================================
    # P14: Design Logic, KG Traversal & Automated Evolution
    # =========================================================================
    s14 = new_slide(
        prs, "3.2 图谱逆频采样与自动化指令演化", "3 场景原生指令合成与动态微调", 14, TOTAL,
        notes=(
            "设计逻辑模板规定‘怎么问、怎么答’，双向增广知识图谱提供‘问什么、答什么’，并按实体历史使用频次倒数 1/(1+χ) 抽样起点以覆盖长尾设备。"
            "右图展示了自动化演化闭环：施加约束增加、条件组合、风险嵌入等五类算子重写完整答案，经三项自检与Optimizer LLM失败反馈自动修订提示词。"
        )
    )
    add_picture_fit(s14, asset("fig3_2_evol.png"), MARGIN_X, 1.12, 6.45, 5.65)

    add_bullets(s14, MARGIN_X + 6.72, 1.25, 5.21, 5.40, [
        ("逻辑模板 ℓ = (a, Ξ, σ, φ)：", "分离知识需求链 Ξ 与回答组织结构 σ。"),
        ("逆频起点采样：", "按 1 / (1 + χ(e)) 抽样实体，长尾覆盖提高 31%。"),
        ("自优化演化闭环：", "五类算子重写问答，Optimizer LLM 自动迭代提示词。"),
    ], main_size=18.5, gap=28.0, valign=MSO_ANCHOR.MIDDLE)

    # =========================================================================
    # P15: Quality Filtering & Two-Stage SFT Ratio
    # =========================================================================
    s15 = new_slide(
        prs, "3.3 一票否决质量筛选与两阶段微调配比", "3 场景原生指令合成与动态微调", 15, TOTAL,
        notes=(
            "末端筛选基于1000条双专家盲评样本拟合四维权重（事实支持率q3占0.36），任何与图谱冲突的样本一票否决，独立测试集准入精确率达94.2%。"
            "微调先在6万通用指令上建立对话格式，再按通用:电力 = 1:2 混训，取得最高的均衡得分74.6%。"
        )
    )
    add_picture_fit(s15, asset("eq_sft_quality_clean.png"), MARGIN_X + 0.25, 1.22, CONTENT_W - 0.50, 0.72)

    _, tf_m15 = add_textbox(s15, MARGIN_X, 2.08, CONTENT_W, 0.55)
    add_para(tf_m15, [
        ("双专家盲评拟合权重（κ = 0.79）：", 17.0, True, NAVY),
        ("事实冲突一票否决，准入精确率 94.2%。", 17.0, False, INK)
    ], space_after=0, first=True)

    sft_r_hdr = ["Stage 2 通用 : 电力", "PowerQA ↑", "FaultDiag ↑", "RegulationQA ↑", "通用指令遵循 ↑", "均衡分 ↑"]
    sft_r_row = [
        ["0 : 1 (γ = 1.00)", "83.6%", "65.3%", "80.7%", "58.4%", "66.2%"],
        ["1 : 4 (γ = 0.80)", "83.0%", "64.3%", "79.3%", "71.2%", "73.3%"],
        ["1 : 2 (γ = 0.67)", "82.3%", "63.0%", "78.0%", "74.8%", "74.6%"],
        ["1 : 1 (γ = 0.50)", "80.6%", "61.0%", "76.7%", "76.3%", "74.5%"],
    ]
    add_three_line_table(
        s15, MARGIN_X, 2.85, CONTENT_W, 3.80, sft_r_hdr, sft_r_row,
        col_widths=[2.6, 1.8, 1.8, 1.9, 2.1, 1.7], col_aligns=[PP_ALIGN.CENTER] * 6,
        font_size=16.2, header_size=16.5, highlight_rows={2}, red_cells={(0, 4), (2, 5)}
    )

    # =========================================================================
    # P16: Dynamic Fine-Tuning (DFT) & CPT Prior Synergy
    # =========================================================================
    s16 = new_slide(
        prs, "3.4 动态微调（DFT）与 CPT 先验协同机理", "3 场景原生指令合成与动态微调", 16, TOTAL,
        notes=(
            "标准交叉熵的logit梯度为1-p，低概率表面连接词（p=0.1）梯度是专业词（p=0.9）的9倍，易拟合教师模型的套话；"
            "DFT乘以停止梯度概率sg(p_t)，将梯度变为p(1-p)，压低表面词权重。"
            "但无CPT时生僻电力事实p≈0.05，DFT梯度仅0.048导致事实吸收受阻；前置CPT将事实概率推至0.30后，DFT梯度放大4.4倍至0.21，实现协同增益。"
        )
    )
    add_picture_fit(s16, asset("fig3_3_dft_grad.png"), MARGIN_X, 1.22, 6.25, 5.45)

    add_box(s16, MARGIN_X + 6.50, 1.32, 5.43, 1.55, fill=SOFT_BG, border=RULE_GRAY)
    add_picture_fit(s16, asset("eq_dft_clean.png"), MARGIN_X + 6.65, 1.42, 5.13, 1.35)

    add_bullets(s16, MARGIN_X + 6.50, 3.25, 5.43, 3.35, [
        ("抑制表面词过拟合：", "消除 CE 对低概率过渡词的 9 倍偏置。"),
        ("CPT 跨越低概率区：", "p 由 0.05 推升至 0.30，DFT 梯度放大 4.4 倍。"),
    ], main_size=18.0, gap=24.0)

    # =========================================================================
    # P17: SFT 2x2 Comparison & Pipeline Ablation
    # =========================================================================
    s17 = new_slide(
        prs, "3.5 SFT 实验验证：2×2 对比与管线消融", "3 场景原生指令合成与动态微调", 17, TOTAL,
        notes=(
            "左表2×2正交实验印证了梯度分析：无CPT时DFT在事实与制度任务上弱于CE；有CPT先验后DFT全面占优，FaultDiag首因准确率提升4.7个百分点达63.0%。"
            "右图消融实验表明：去掉专家种子、知识图谱、指令演化分别使制度问答下降11.0 pp、多跳推理下降7.0 pp、复杂故障诊断下降8.7 pp。"
        )
    )
    syn_hdr = ["模型配置", "PowerQA", "FaultDiag", "RegulationQA"]
    syn_row = [
        ["Base + CE", "73.5%", "51.0%", "64.3%"],
        ["Base + DFT", "71.8%", "53.3%", "61.0%"],
        ["CPT + CE", "80.6%", "58.3%", "76.0%"],
        ["CPT + DFT", "82.3%", "63.0%", "78.0%"],
    ]
    add_three_line_table(
        s17, MARGIN_X, 1.65, 5.55, 3.85, syn_hdr, syn_row,
        col_widths=[1.95, 1.20, 1.20, 1.20],
        col_aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.CENTER],
        font_size=16.0, header_size=16.2, highlight_rows={3}, sub_rules={1}, red_cells={(3, 2)}
    )

    add_picture_fit(s17, asset("chart_sft_ablation_clean.png"), MARGIN_X + 5.82, 1.25, 6.11, 5.35)

    # =========================================================================
    # P18: SFT Case Study (Concise Key-Point Table, 16pt)
    # =========================================================================
    s18 = new_slide(
        prs, "3.6 故障诊断真实工单案例对比", "3 场景原生指令合成与动态微调", 18, TOTAL,
        notes=(
            "案例问题：110kV主变正常负荷发轻瓦斯告警，油温油位正常，一周前刚完成冷却器检修。"
            "Base直接建议停电吊罩；CPT罗列常见原因但无排序与步骤；CPT+SFT准确锁定‘检修残留空气进入继电器’首因，给出五步由浅入深排查及严禁退出重瓦斯跳闸的安全提示。"
        )
    )
    _, tf_q18 = add_textbox(s18, MARGIN_X, 1.20, CONTENT_W, 0.55)
    add_para(tf_q18, [
        ("工单问题：", 17.5, True, NAVY),
        ("110kV 主变正常负荷发轻瓦斯告警，油温油位正常，一周前刚完成冷却器检修。", 17.5, False, INK)
    ], space_after=0, first=True)

    c18_hdr = ["模型", "首因判定", "回答结构与关键结论"]
    c18_row = [
        ["Base", "未命中", "忽略检修线索，直接建议停电吊罩检查（处置代价过高）"],
        ["CPT", "未命中", "罗列四类常见原因，无主次排序、无排查步骤与安全警示"],
        ["CPT + SFT", "命中", "首因：冷却器检修残留空气 → 核对排气 → 取气辨色 → 油色谱 → 严禁退重瓦斯跳闸"],
    ]
    add_three_line_table(
        s18, MARGIN_X, 2.05, CONTENT_W, 4.25, c18_hdr, c18_row,
        col_widths=[1.8, 1.6, 8.5], col_aligns=[PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.LEFT],
        font_size=16.0, header_size=16.5, highlight_rows={2}, sub_rules={0, 1}, red_cells={(0, 1), (1, 1)}
    )

    # =========================================================================
    # P19: Section 4 Divider
    # =========================================================================
    new_section_slide(
        prs, "第四部分", "面向用户角色的回答风格强化学习对齐",
        ["4.1 提问角色与语料解耦：三维风格与条件化 Prefix", "4.2 风格判别模型 StyleRM-7B", "4.3 GRPO + Clip-Higher 训练与评测"],
        19, TOTAL, notes="进入第四部分，汇报面向不同用户群体的回答风格强化学习对齐方法。"
    )

    # =========================================================================
    # P20: Role-Style Mapping & 12-Token Prefix
    # =========================================================================
    s20 = new_slide(
        prs, "4.1 提问角色与语料解耦：风格组合与 Prefix", "4 面向用户角色的风格强化学习对齐", 20, TOTAL,
        notes=(
            "回答风格取决于提问者是谁，而非问题来自哪类语料。我们将风格拆分为展开程度、安全警示、表述类型三个类目，为研发、运维、管理三类用户规定固定组合，编码为仅约12 token的Prefix拼接在问题前，仅调整表述形式而不改变技术结论。"
        )
    )
    ug_hdr = ["目标用户群体", "展开程度", "安全警示", "表述类型"]
    ug_row = [
        ["技术研究人员", "详尽（机理与推导）", "基础提醒（文末概括）", "研讨型"],
        ["生产运维人员", "精简（结论先行）", "逐项警戒（每步前置条件）", "指令型"],
        ["管理人员", "适中（因果链条）", "前置提醒（开头单列风险）", "裁定型"],
    ]
    add_three_line_table(
        s20, MARGIN_X, 1.38, CONTENT_W, 3.15, ug_hdr, ug_row,
        col_widths=[2.8, 2.8, 3.6, 2.7], col_aligns=[PP_ALIGN.CENTER] * 4,
        font_size=15.8, header_size=16.2, highlight_rows={1}
    )

    add_bullets(s20, MARGIN_X, 4.90, CONTENT_W, 1.85, [
        ("轻量控制接口：", "输入前缀仅约 12 token（如 [展开:精简][安全:逐项警戒][表述:指令]），远短于少样本提示（~2100 token）。"),
        ("内容与风格解耦：", "仅改变表述形式，不改变技术判断；判别模型打分时剥离 Prefix，只评问答文本。"),
    ], main_size=17.5, gap=14.0)

    # =========================================================================
    # P21: StyleRM-7B Discriminator
    # =========================================================================
    s21 = new_slide(
        prs, "4.2 风格判别模型 StyleRM-7B", "4 面向用户角色的风格强化学习对齐", 21, TOTAL,
        notes=(
            "构建1.38万条经双模型校准的风格标注样本（与RL Prompt集严格不重叠，含36%跨角色同题多风格样本）。"
            "左图展示了StyleRM-7B架构：通过类目专属查询向量对全序列隐藏状态做注意力池化，三类目平均判别准确率达83.3%，较零样本提示提高20.5 pp。"
        )
    )
    add_picture_fit(s21, asset("fig4_1_rl_rm.png"), MARGIN_X, 1.15, 6.75, 5.55)

    rm_hdr = ["判别方法", "展开", "安全", "表述", "均值 ↑"]
    rm_row = [
        ["7B 零样本", "59.4%", "55.6%", "73.5%", "62.8%"],
        ["StyleRM-3B", "74.6%", "71.2%", "87.0%", "77.6%"],
        ["StyleRM-7B", "81.3%", "78.0%", "90.6%", "83.3%"],
    ]
    add_three_line_table(
        s21, MARGIN_X + 7.00, 1.55, 4.93, 2.75, rm_hdr, rm_row,
        col_widths=[1.55, 0.82, 0.82, 0.82, 0.92],
        col_aligns=[PP_ALIGN.LEFT] + [PP_ALIGN.CENTER] * 4,
        font_size=14.5, header_size=14.8, highlight_rows={2}, red_cells={(2, 4)}
    )
    add_bullets(s21, MARGIN_X + 7.00, 4.65, 4.93, 2.00, [
        ("防泄漏切分：", "1.2w 改写集与 6k RL 集零重叠。"),
        ("注意力分类头：", "平均准确率提升 +20.5 pp。"),
    ], main_size=17.0, gap=14.0)

    # =========================================================================
    # P22: GRPO + Clip-Higher Anti-Collapse Training
    # =========================================================================
    s22 = new_slide(
        prs, "4.3 开根号奖励与 GRPO + Clip-Higher 训练", "4 面向用户角色的风格强化学习对齐", 22, TOTAL,
        notes=(
            "将各类目概率开根号均值作为奖励（r = 1/3 ∑√P_j），放大低概率短板类目的梯度灵敏度。"
            "标准GRPO在3000步内出现策略熵坍缩（右图蓝线），组内采样趋同导致奖励停滞；引入非对称上界裁剪Clip-Higher（ε_high=0.28）维持了组内多样性，无需Critic即取得最高的90.2%测试集风格命中率。"
        )
    )
    rl_hdr = ["RL 算法（8500 步同预算）", "Critic", "测试 SHR ↑"]
    rl_row = [
        ["标准 PPO", "需要", "76.8%"],
        ["Dual-Clip PPO", "需要", "85.1%"],
        ["RLOO (M = 8)", "不需要", "81.9%"],
        ["标准 GRPO (G = 8)", "不需要", "83.7%"],
        ["GRPO + Clip-Higher", "不需要", "90.2%"],
    ]
    add_three_line_table(
        s22, MARGIN_X, 1.38, 5.45, 3.75, rl_hdr, rl_row,
        col_widths=[2.65, 1.25, 1.55],
        col_aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.CENTER],
        font_size=15.0, header_size=15.2, highlight_rows={4}, sub_rules={1}, red_cells={(4, 2)}
    )
    add_bullets(s22, MARGIN_X, 5.38, 5.45, 1.35, [
        ("开根号奖励 √P_j：", "优先驱动低分短板类目（+2.4 pp）。"),
        ("Clip-Higher (0.28)：", "抑制熵坍缩，突破后期奖励平台。"),
    ], main_size=16.5, gap=10.0)

    add_picture_fit(s22, asset("fig4_5_entropy.png"), MARGIN_X + 5.75, 1.28, 6.18, 5.35,
                    caption="标准 GRPO 熵坍缩至 0.2 vs. Clip-Higher 维持组内多样性 (~0.85)")

    # =========================================================================
    # P23: RoleStyle-Eval Results & Concise Cross-Role Case
    # =========================================================================
    s23 = new_slide(
        prs, "4.4 风格评测结果与跨角色输出对比", "4 面向用户角色的风格强化学习对齐", 23, TOTAL,
        notes=(
            "左图显示，RLAIF模型风格命中率SHR达90.2%（较少样本提示+27.6 pp），三项联合命中率Joint-HR达76.2%（+49.2 pp），在最难改变的‘逐项警戒’上提升41.1 pp，且领域任务回落小于1 pp。"
            "右侧展示了同一道‘220kV线路TV断线告警’在运维与研发两种角色下的结构差异。"
        )
    )
    add_picture_fit(s23, asset("chart_rolestyle_clean.png"), MARGIN_X, 1.22, 6.15, 5.45)

    _, tf_c23 = add_textbox(s23, MARGIN_X + 6.45, 1.35, 5.48, 5.25)
    add_para(tf_c23, [("同题对比：220kV 线路“TV 断线”告警处置", 17.5, True, NAVY)], space_after=16, first=True)

    add_para(tf_c23, [("• 生产运维（精简 + 逐项警戒 + 指令）", 16.5, True, INK)], space_after=6)
    add_para(tf_c23, [(
        "开头【安全警告】防二次短路 → ①确认保护闭锁 → ②（须用绝缘工具）查空开端子 → ③（未经许可禁投退）按调度令退保护。",
        15.5, False, SUB_INK
    )], line_spacing=1.38, space_after=22)

    add_para(tf_c23, [("• 技术研究（详尽 + 基础提醒 + 研讨）", 16.5, True, INK)], space_after=6)
    add_para(tf_c23, [(
        "阐述自产零序电压断线判别逻辑与元件闭锁机理 → 研讨空开、切换接点、熔断器三类成因与录波判据 → 文末附一句防短路提醒。",
        15.5, False, SUB_INK
    )], line_spacing=1.38, space_after=18)

    add_para(tf_c23, [("注：跨角色题 Joint-HR 达 73.8%，三项电力任务回落均 < 1 pp。", 15.0, True, NAVY)], space_after=0)
