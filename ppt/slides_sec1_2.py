# -*- coding: utf-8 -*-
"""
Ultra-Clean, Large-Font Academic Slides (Part 1: Slides 1 - 11)
- Body bullets: 18.5 - 20 pt, single-line concise phrases (no paragraph walls)
- Tables: 15.5 - 16.5 pt, clean Booktabs 3-line style
- One visual focus per slide, generous whitespace, zero AI-template feel
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


def build_slides_1_to_11(prs):
    # =========================================================================
    # P01: Cover Slide (Spacious, Large Typography)
    # =========================================================================
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    s1.background.fill.solid()
    s1.background.fill.fore_color.rgb = WHITE

    add_picture_fit(s1, asset("hitsz_logo_blue.png"), MARGIN_X, 0.58, 3.65, 0.68)
    _, tf_tag = add_textbox(s1, SLIDE_W - MARGIN_X - 3.5, 0.65, 3.5, 0.50, valign=MSO_ANCHOR.MIDDLE)
    add_para(tf_tag, [("硕士学位论文答辩", 17.0, False, SUB_INK)], align=PP_ALIGN.RIGHT, space_after=0, first=True)

    add_line(s1, MARGIN_X, 1.45, CONTENT_W, color=NAVY, pt=1.6)

    _, tf_title = add_textbox(s1, MARGIN_X, 2.15, CONTENT_W, 2.10)
    add_para(tf_title, [("面向数字电网知识服务的\n大语言模型训练与对齐方法研究", 34.0, True, NAVY)],
             line_spacing=1.32, space_after=0, first=True)

    _, tf_info = add_textbox(s1, MARGIN_X, 4.75, 10.5, 2.05)
    add_para(tf_info, [("答 辩 人：赵乐森", 19.0, False, INK),
                       ("            指导教师：许  鋆  教授", 19.0, False, INK)], space_after=14, first=True)
    add_para(tf_info, [("学科专业：控制科学与工程", 19.0, False, INK),
                       ("    所属学院：智能科学与工程学院", 19.0, False, INK)], space_after=14)
    add_para(tf_info, [("2027 年 1 月", 17.0, False, MUTED)], space_after=0)

    s1.notes_slide.notes_text_frame.text = (
        "各位评审老师好！我是控制科学与工程专业的硕士生赵乐森，指导教师是许鋆老师。"
        "今天汇报的论文题目是《面向数字电网知识服务的大语言模型训练与对齐方法研究》。"
        "本研究依托中国南方电网数字电网大模型项目开展，汇报时间约25分钟。"
    )

    # =========================================================================
    # P02: Outline (Pure Section Titles, 22pt, Zero Jargon Clutter)
    # =========================================================================
    s2 = new_slide(
        prs, "汇报提纲", "", 2, TOTAL,
        notes=(
            "汇报共分六个部分：首先介绍研究背景与四阶段总体路线；随后依次汇报电力语料构建与持续预训练、"
            "场景原生指令合成与动态微调、面向用户群体的风格强化学习对齐、深层安全DPO对齐与综合评测；最后总结全文并展望后续工作。"
        )
    )
    toc_titles = [
        "1.   研究背景与总体技术路线",
        "2.   电力领域数据体系构建与持续预训练",
        "3.   面向七类业务场景的指令合成与动态微调",
        "4.   基于 Prompt Prefix 的回答风格强化学习对齐",
        "5.   面向电力安全合规的深层 DPO 对齐",
        "6.   总结与展望",
    ]
    _, tf_toc = add_textbox(s2, 1.50, 1.25, 10.2, 5.45, valign=MSO_ANCHOR.MIDDLE)
    for i, t in enumerate(toc_titles):
        add_para(tf_toc, [(t, 22.0, False, INK)],
                 space_before=(0 if i == 0 else 20), space_after=4, first=(i == 0))

    # =========================================================================
    # P03: Section 1 Divider
    # =========================================================================
    new_section_slide(
        prs, "第一部分", "研究背景与总体技术路线",
        ["1.1 电力场景的四类特殊挑战", "1.2 四阶段训练框架", "1.3 主要创新点"],
        3, TOTAL, notes="首先汇报第一部分：研究背景、切入点与总体技术路线。"
    )

    # =========================================================================
    # P04: Background & 4 Challenges (Clean 2x2 / 4-Row Short Phrases, 19pt)
    # =========================================================================
    s4 = new_slide(
        prs, "1.1 电力领域大语言模型面临的挑战", "1 研究背景与总体路线", 4, TOTAL,
        notes=(
            "通用大模型应用于数字电网知识服务面临四个层面的挑战："
            "第一是知识层面，电力规程、工单与仿真文档多源异构，通用基座缺乏设备机理与内部规程先验，而纯领域预训练又容易遗忘通用能力；"
            "第二是任务层面，故障诊断要求结论先行和按序排查，制度问答要求精确引用条款，套用统一模板会丢失各类资料的原生推理结构；"
            "第三是表达层面，同一问题由研发、运维或管理人员提出时，所需的详略与警示方式截然不同，传统微调风格随语料固定、无法按角色切换；"
            "第四是安全层面，违章诱导常表现为‘语言合规但工程危险’，没有表面敏感词，浅层安全对齐易在中途状态被突破，加严又易导致过度拒答。"
        )
    )
    ch_hdr = ["维度", "业务特征", "通用模型局限"]
    ch_row = [
        ["领域知识", "发输变配调多源异构，设备机理与规程强耦合", "缺乏内部规程先验；纯领域训练易遗忘通用能力"],
        ["专业任务", "故障需按序排查，制度需条款溯源，方案需权衡", "自由生成易编造条款；统一模板丢失原生推理结构"],
        ["用户表达", "研发重机理、运维重操作指令、管理重依据裁定", "回答风格随语料固定，无法按提问角色切换"],
        ["安全合规", "违章诱导多为“语言合规但工程危险”，无敏感词", "浅层对齐易被中途突破；加严拒答易误伤正常咨询"],
    ]
    add_three_line_table(
        s4, MARGIN_X, 1.45, CONTENT_W, 4.95, ch_hdr, ch_row,
        col_widths=[1.8, 4.9, 5.2], col_aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        font_size=16.8, header_size=17.2, sub_rules={0, 1, 2}, bold_cells={(0, 0), (1, 0), (2, 0), (3, 0)},
        red_cells={(3, 0)}
    )

    # =========================================================================
    # P05: Overall Technical Roadmap (Full-Width Fig 1-1 Only)
    # =========================================================================
    s5 = new_slide(
        prs, "1.2 总体技术路线：四阶段递进训练框架", "1 研究背景与总体路线", 5, TOTAL,
        notes=(
            "针对上述挑战，本文以 Qwen2.5-7B 预训练模型为基座，提出 CPT—SFT—RLAIF—DPO 四阶段框架。"
            "每阶段以前一阶段模型初始化：CPT注入电力知识；SFT保留七类资料原生风格培养任务能力；RLAIF按三类用户角色显式控制风格；DPO建立深层安全边界。"
        )
    )
    add_picture_fit(s5, asset("fig1_1_roadmap.png"), MARGIN_X + 0.1, 1.12, CONTENT_W - 0.2, 5.65)

    # =========================================================================
    # P06: Main Contributions (Short, Crisp 19pt Lines)
    # =========================================================================
    s6 = new_slide(
        prs, "1.3 主要研究工作与创新点", "1 研究背景与总体路线", 6, TOTAL,
        notes=(
            "本文的主要创新点有四项：一是结合专家种子设计逻辑与知识图谱约束的六模块场景原生指令合成管线，构建6.8万条指令；"
            "二是CPT领域先验与动态微调DFT协同策略，故障诊断首因准确率较标准交叉熵提升4.7个百分点；"
            "三是面向三类用户群体的12-token风格Prefix强化学习对齐，风格命中率达90.2%；"
            "四是基于Token边界截断同状态恢复与困难状态加权的深层DPO对齐，攻击成功率降至7.9%，相关工作已被EACL 2027 Findings录用。"
        )
    )
    add_bullets(s6, MARGIN_X, 1.25, CONTENT_W, 4.70, [
        ("1. 场景原生指令数据合成：", "融合专家设计逻辑与 4.2 万条知识图谱三元组，构建 6.8 万条保留原生风格的指令数据。"),
        ("2. CPT 先验与 DFT 协同微调：", "先以持续预训练注入电力先验，再用动态微调抑制表面词过拟合，故障诊断首因准确率提高 4.7 pp。"),
        ("3. 面向用户群体的风格对齐：", "引入 12-token 风格 Prefix 与判别模型 StyleRM-7B，风格命中率达 90.2%（较少样本提示高 27.6 pp）。"),
        ("4. 电力深层安全 DPO 对齐：", "构建原生 Token 截断同状态恢复数据与困难状态加权，攻击成功率降至 7.9%，过度拒答率控制在 5.0%。"),
    ], main_size=18.5, gap=22.0, valign=MSO_ANCHOR.MIDDLE)

    add_line(s6, MARGIN_X, 6.15, CONTENT_W, color=RULE_GRAY, pt=0.8)
    _, tf_pub = add_textbox(s6, MARGIN_X, 6.28, CONTENT_W, 0.55)
    add_para(tf_pub, [
        ("代表论文：", 15.0, True, NAVY),
        ("Zhao L, et al. Refusal Is Not Recovery: Same-State Preference Optimization from Unsafe Generation States. ", 14.5, False, INK, FONT_EN),
        ("Findings of EACL 2027.", 14.5, True, ACCENT_RED, FONT_EN)
    ], space_after=0, first=True)

    # =========================================================================
    # P07: Section 2 Divider
    # =========================================================================
    new_section_slide(
        prs, "第二部分", "电力领域数据体系构建与持续预训练",
        ["2.1 数据体系、三级去重与评测隔离", "2.2 基于种子模型困惑度的双阈值筛选", "2.3 领域—通用混合配比实验"],
        7, TOTAL, notes="下面汇报第二部分：电力数据体系、评测隔离协议与持续预训练。"
    )

    # =========================================================================
    # P08: Data System, 3-Stage Dedup & Evaluation Isolation (Clean Split)
    # =========================================================================
    s8 = new_slide(
        prs, "2.1 电力数据体系、三级去重与评测隔离", "2 电力数据体系与持续预训练", 8, TOTAL,
        notes=(
            "我们整合南方电网脱敏工单、检修报告、规程与公开标准，划分为基础科学、工程建设、新型电力系统、运行控制、运维检修、安全市场、制度文件七类语料，面向知识问答、故障诊断、制度问答、方案分析四类核心任务。"
            "预处理中按4096 token完整句分箱，通过下表三级去重累计剔除33.8%重复内容。"
            "同时确立严格的评测隔离协议：整篇抽取5%源文档作为评测保留集D_eval（仅参与无监督CPT注入知识，严禁进入后续图谱、SFT、RLAIF和DPO训练），并采用GPT-5与Claude Sonnet 4.5独立双裁判评分，排除教师模型Qwen-Max自评偏好。"
        )
    )
    add_bullets(s8, MARGIN_X, 1.25, CONTENT_W, 2.05, [
        ("双源七类语料：", "南网内部脱敏工单/规程 + 公开标准教材，覆盖发输变配调检七类场景与四类核心任务。"),
        ("文档级评测隔离：", "整篇划出 5% 文档作评测集 D_eval（仅参与 CPT，严格隔离于后续各阶段），GPT-5 + Claude 双裁判评分。"),
    ], main_size=17.5, gap=12.0)

    dd_hdr = ["去重级别", "核心算法与阈值", "目标重复类型", "本级去除", "累积保留"]
    dd_row = [
        ["第一级", "64 位 SimHash + 条款号正则", "完全同文及重编号引用", "18.6%", "81.4%"],
        ["第二级", "3-gram MinHash + LSH (0.85)", "局部改写与摘录", "12.3%", "71.4%"],
        ["第三级", "BGE-M3 向量 + FAISS (0.92)", "异文同义（留高实体密度条）", "7.2%", "66.2%"],
        ["三级合计", "句面 → 字符集 → 语义递进", "相对原始候选语料", "33.8%", "66.2%"],
    ]
    add_three_line_table(
        s8, MARGIN_X, 3.55, CONTENT_W, 3.15, dd_hdr, dd_row,
        col_widths=[1.5, 3.6, 3.6, 1.6, 1.6],
        col_aligns=[PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.CENTER],
        font_size=15.0, header_size=15.5, highlight_rows={3}
    )

    # =========================================================================
    # P09: PPL Dual-Threshold Filtering (Large Chart + 3 Crisp Bullets)
    # =========================================================================
    s9 = new_slide(
        prs, "2.2 基于种子模型困惑度（PPL）的数据筛选", "2 电力数据体系与持续预训练", 9, TOTAL,
        notes=(
            "去重后语料两端仍存在低熵公文套话与高熵OCR残余噪声。我们用5%精选语料训练种子CPT模型为全量切片打分，"
            "按每5%分位数抽样5000条标注。如左图所示，P10以下冗余占74%，P80以上噪声陡增至64%~89%；"
            "通过零训练计算有效召回率与纯度的调和平均F，锁定[P10, P80]最优区间（F=88.6），保留中间70%约2.1B token高质量语料。"
        )
    )
    add_picture_fit(s9, asset("fig2_3_ppl_thresh.png"), MARGIN_X, 1.15, 7.35, 5.55)

    add_bullets(s9, MARGIN_X + 7.60, 1.25, 4.33, 5.35, [
        ("种子模型打分：", "5% 精选切片训练种子模型计算 PPL。"),
        ("双端拐点分布：", "P10 以下 74% 冗余；P80 以上 64%–89% 噪声。"),
        ("零训练定界：", "取 [P10, P80]（F = 88.6），留存 2.1B token。"),
    ], main_size=18.5, gap=26.0, valign=MSO_ANCHOR.MIDDLE)

    # =========================================================================
    # P10: CPT Domain-General Ratio (Clean Large Table + Key Result Only)
    # =========================================================================
    s10 = new_slide(
        prs, "2.3 CPT 领域—通用混合配比实验", "2 电力数据体系与持续预训练", 10, TOTAL,
        notes=(
            "纯领域训练（1:0）虽能使PowerQA升至72.4%，但通用能力GS暴跌10.5个百分点出现灾难性遗忘。"
            "实验表明1:1均衡混合（λ=0.5，总计4.2B token训练1个epoch）取得最高的调和平均均衡得分65.0%：PowerQA大幅提升24.7 pp至68.2%，通用得分仅降3.7 pp；且PPL筛选在同配比下带来6.7 pp的显著增益。"
        )
    )
    cpt_hdr = ["电力 : 通用配比", "PowerQA 领域 ↑", "通用基准 GS ↑", "调和均衡分 S(λ) ↑"]
    cpt_row = [
        ["基座模型（无 CPT）", "43.5%", "65.8%", "52.4%"],
        ["1 : 2 (λ = 0.33)", "57.8%", "64.3%", "60.9%"],
        ["1 : 1 (λ = 0.50)", "68.2%", "62.1%", "65.0%"],
        ["1 : 0 (λ = 1.00)", "72.4%", "55.3%", "62.7%"],
        ["1 : 1（无 PPL 筛选）", "61.5%", "60.4%", "60.9%"],
    ]
    add_three_line_table(
        s10, MARGIN_X, 1.35, CONTENT_W, 4.15, cpt_hdr, cpt_row,
        col_widths=[3.9, 2.7, 2.7, 2.6],
        col_aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.CENTER],
        font_size=16.8, header_size=17.2, highlight_rows={2}, sub_rules={0, 3}, red_cells={(2, 3), (3, 2)}
    )

    add_bullets(s10, MARGIN_X, 5.75, CONTENT_W, 1.00, [
        ("配置：", "2.1B 电力 + 2.1B 通用 = 4.2B token（seq_len 4096，1 epoch）；PPL 筛选同配比提升 PowerQA 6.7 pp。"),
    ], main_size=17.5, gap=8.0)

    # =========================================================================
    # P11: CPT Training Convergence Curves (Clean Visual Evidence)
    # =========================================================================
    s11 = new_slide(
        prs, "2.4 CPT 训练收敛与通用能力保持验证", "2 电力数据体系与持续预训练", 11, TOTAL,
        notes=(
            "观察4000步训练过程中的困惑度变化：左图显示不同配比下调和得分在λ=0.5处取峰值；"
            "右图显示1:1混训下电力验证集PPL从18.7持续降至8.2，而通用验证集PPL稳定在9.8（仅较初始9.5微升0.3，远低于纯领域训练的3.1升幅），验证了知识注入与通用保持的平衡。"
        )
    )
    add_picture_fit(s11, asset("fig2_4_data_ratio.png"), MARGIN_X, 1.35, 5.75, 4.95,
                    caption="不同配比 λ 下的性能权衡曲线")
    add_picture_fit(s11, asset("fig2_6_cpt_ppl.png"), MARGIN_X + 6.15, 1.35, 5.78, 4.95,
                    caption="1:1 混合训练中领域 PPL (18.7→8.2) 与通用 PPL (9.5→9.8)")
