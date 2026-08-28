from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path("output/pdf/counting-zero-empirical-return-algorithm.pdf")
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT_NAME = "ArialUnicode"

pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

PAGE_W, PAGE_H = A4
MARGIN_X = 20 * mm
MARGIN_TOP = 18 * mm
MARGIN_BOTTOM = 18 * mm


class NumberedDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(
            MARGIN_X,
            MARGIN_BOTTOM,
            PAGE_W - 2 * MARGIN_X,
            PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN_X, 13 * mm, PAGE_W - MARGIN_X, 13 * mm)
        canvas.setFont(FONT_NAME, 8.5)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(MARGIN_X, 8.5 * mm, "Counting Zero 实验设计说明")
        canvas.drawRightString(PAGE_W - MARGIN_X, 8.5 * mm, f"第 {doc.page} 页")
        canvas.restoreState()


styles = getSampleStyleSheet()
title = ParagraphStyle(
    "TitleCN",
    parent=styles["Title"],
    fontName=FONT_NAME,
    fontSize=21,
    leading=29,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#0F172A"),
    spaceAfter=8 * mm,
)
subtitle = ParagraphStyle(
    "SubtitleCN",
    parent=styles["Normal"],
    fontName=FONT_NAME,
    fontSize=10.5,
    leading=17,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#475569"),
    spaceAfter=9 * mm,
)
h1 = ParagraphStyle(
    "H1CN",
    parent=styles["Heading1"],
    fontName=FONT_NAME,
    fontSize=15,
    leading=21,
    textColor=colors.HexColor("#0F4C81"),
    spaceBefore=5 * mm,
    spaceAfter=3 * mm,
    keepWithNext=True,
)
h2 = ParagraphStyle(
    "H2CN",
    parent=styles["Heading2"],
    fontName=FONT_NAME,
    fontSize=12,
    leading=18,
    textColor=colors.HexColor("#1E3A5F"),
    spaceBefore=3 * mm,
    spaceAfter=2 * mm,
    keepWithNext=True,
)
body = ParagraphStyle(
    "BodyCN",
    parent=styles["BodyText"],
    fontName=FONT_NAME,
    fontSize=10.3,
    leading=17,
    textColor=colors.HexColor("#1E293B"),
    alignment=TA_LEFT,
    spaceAfter=2.4 * mm,
)
formula = ParagraphStyle(
    "FormulaCN",
    parent=body,
    fontSize=11.5,
    leading=18,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#0F4C81"),
    backColor=colors.HexColor("#EFF6FF"),
    borderPadding=(7, 9, 7, 9),
    spaceBefore=2 * mm,
    spaceAfter=4 * mm,
)
note = ParagraphStyle(
    "NoteCN",
    parent=body,
    fontSize=9.6,
    leading=15.5,
    textColor=colors.HexColor("#334155"),
    backColor=colors.HexColor("#F8FAFC"),
    borderColor=colors.HexColor("#CBD5E1"),
    borderWidth=0.5,
    borderPadding=8,
    spaceBefore=2 * mm,
    spaceAfter=3 * mm,
)
code = ParagraphStyle(
    "CodeCN",
    parent=body,
    fontName=FONT_NAME,
    fontSize=9.2,
    leading=15,
    textColor=colors.HexColor("#E2E8F0"),
    backColor=colors.HexColor("#172033"),
    borderPadding=10,
    leftIndent=0,
    rightIndent=0,
    spaceBefore=2 * mm,
    spaceAfter=4 * mm,
)


def P(text, style=body):
    return Paragraph(text, style)


def metric_table(rows, widths=(54 * mm, 46 * mm, 58 * mm)):
    table = Table(rows, colWidths=list(widths), repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("LEADING", (0, 0), (-1, -1), 14),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#1E293B")),
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


story = []
story += [
    P("基于股票 30 日经验收益率的<br/>Counting Zero 矩阵生成算法", title),
    P(
        "设计目标：让数零任务与股价预测任务的正确答案具有可比较的相对波动，同时保持 15×15 矩阵中 0 和 1 的长期平均比例约为 50:50。",
        subtitle,
    ),
    P("1. 设计问题", h1),
    P(
        "现有程序对 225 个格子分别、独立地以 50% 概率生成 0 或 1。因此，0 的数量 X 服从 Binomial(225, 0.5)，均值为 112.5，标准差仅为 7.5。正确答案高度集中在 112 和 113 附近，参与者可以通过猜测中心值获得不应有的优势。"
    ),
    P("X ~ Binomial(225, 0.5),　E[X] = 112.5,　SD[X] = 7.5", formula),
    P(
        "简单改为 0 到 225 的离散均匀分布虽然能消除中心集中，但会频繁生成几乎全 0 或几乎全 1 的矩阵，任务难度不稳定，也无法与股价预测任务建立数据基础上的对应关系。"
    ),
    P("2. 股票任务的经验基准", h1),
    P(
        "项目中包含 200 只股票。每只股票向参与者展示 252 个历史交易日，并要求预测随后第 30 个交易日的归一化价格。与预测难度直接相关的收益率，应以最后一个可见历史价格为基准："
    ),
    P("Ri = Pi,30 / Pi,0 - 1", formula),
    metric_table(
        [
            ["统计量", "30 日 return", "对应含义"],
            ["最小值", "-49.91%", "最极端下跌"],
            ["5% 分位数", "-15.12%", "中央 90% 下界"],
            ["中位数", "+0.99%", "典型观测"],
            ["均值", "+1.36%", "样本平均漂移"],
            ["标准差", "12.20%", "相对波动尺度"],
            ["95% 分位数", "+19.16%", "中央 90% 上界"],
            ["最大值", "+48.65%", "最极端上涨"],
        ]
    ),
    Spacer(1, 3 * mm),
    P(
        "说明：不能使用“正确价格相对于序列第一天 100 的 return”作为映射基准，因为它混合了已展示的 252 日历史变化和真正需要预测的未来 30 日变化。采用最后可见价格到正确答案之间的 30 日 return，才能反映参与者实际面对的不确定性。",
        note,
    ),
]

story += [
    P("3. 推荐的中心化经验映射", h1),
    P(
        "每次生成矩阵时，从 200 个真实股票 30 日 return 中等概率抽取一个 Ri。为了消除股票样本平均上涨造成的 0/1 比例偏移，先减去经验均值 Rmean，再将相对变化映射到以 112.5 为中心的 0 数量："
    ),
    P("X = round{112.5 × [1 + (Ri - Rmean)]},　Rmean = 1.3569%", formula),
    P(
        "映射完成后，建立 X 个 0 和 225-X 个 1，并使用均匀随机洗牌决定位置。条件于 X，所有包含 X 个 0 的矩阵具有相同生成概率。"
    ),
    P("4. 映射后分布的实际性质", h1),
    metric_table(
        [
            ["统计量", "0 的数量 X", "解释"],
            ["最小值", "55", "对应最极端负 return"],
            ["5% 分位数", "94", "中央 90% 下界"],
            ["25% 分位数", "106", "下四分位数"],
            ["中位数", "112", "分布中心"],
            ["均值", "112.475", "约等于 112.5"],
            ["标准差", "13.77", "相对标准差约 12.24%"],
            ["75% 分位数", "118", "上四分位数"],
            ["95% 分位数", "133", "中央 90% 上界"],
            ["最大值", "166", "对应最极端正 return"],
        ]
    ),
    Spacer(1, 3 * mm),
    P(
        "该映射使 (X-112.5)/112.5 与 Ri-Rmean 近似相等。因此，两个任务的正确答案具有近似相同的相对离散程度。映射后 E[X]≈112.5，所以任一随机位置长期为 0 的边际概率仍约为 50%。",
        note,
    ),
    P("5. 完整生成步骤", h1),
    P("① 预先计算所有股票的 30 日 return 列表，并计算其经验均值。"),
    P("② 每道题从 return 列表中等概率、有放回抽取一个 return。"),
    P("③ 使用中心化映射公式计算 0 的数量，并四舍五入为整数。"),
    P("④ 将结果限制在 0 到 225 之间，作为防御性检查。"),
    P("⑤ 建立指定数量的 0 和剩余数量的 1。"),
    P("⑥ 使用 Fisher-Yates 等均匀洗牌方法随机排列全部 225 个格子。"),
    P("⑦ 每 15 个元素切分为一行，形成 15×15 矩阵。"),
]

story += [
    P("6. Python 参考实现", h1),
    P(
        "<font color='#93C5FD'>def</font> make_matrix():<br/>"
        "　total_cells = C.MATRIX_SIZE ** 2<br/>"
        "　sampled_return = random.choice(STOCK_30_DAY_RETURNS)<br/>"
        "　centered_return = sampled_return - MEAN_STOCK_RETURN<br/><br/>"
        "　zero_count = round(total_cells / 2 * (1 + centered_return))<br/>"
        "　zero_count = max(0, min(total_cells, zero_count))<br/><br/>"
        "　cells = [0] * zero_count + [1] * (total_cells - zero_count)<br/>"
        "　random.shuffle(cells)<br/><br/>"
        "　matrix = [cells[i:i + C.MATRIX_SIZE]<br/>"
        "　　　　　　for i in range(0, total_cells, C.MATRIX_SIZE)]<br/>"
        "　return matrix, zero_count",
        code,
    ),
    P("7. 实施建议", h1),
    P("经验抽样方式", h2),
    P(
        "建议有放回抽样。每道题都从同一套 200 个 return 中独立抽取，使每道题的边际分布一致，也避免参与者完成较多题目后改变剩余题目的分布。"
    ),
    P("中心化处理", h2),
    P(
        "建议保留中心化。若直接映射原始 return，0 的平均数量约为 114.02，单个格子为 0 的长期概率约为 50.68%。中心化后平均值约为 112.475，更接近严格的 50:50。"
    ),
    P("可复现性", h2),
    P(
        "正式实验应保存每道题抽中的 return、zero_count、矩阵以及随机种子或可追踪的题目标识。这样可以复核正确答案，并验证不同处理组面对的题目分布是否平衡。"
    ),
    P("极端值", h2),
    P(
        "当前经验 return 映射后的范围为 55 到 166，仍远离 0 和 225，不会生成全 0 或全 1 的退化矩阵，因此无需删去极端观测。若未来替换股票库，应重新检查映射范围，并在必要时预先规定截尾规则。"
    ),
    P("8. 结论", h1),
    P(
        "推荐采用“中心化股票 30 日经验 return 重抽样”算法。它比二项伯努利生成方式提供更充分的答案变化，又比人为均匀分布更具实验依据；最重要的是，它使 Counting Zero 与 Stock Forecast 两个任务在正确答案的相对波动上建立了清晰、可复核的对应关系。",
        note,
    ),
]


doc = NumberedDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    title="基于股票30日经验收益率的Counting Zero矩阵生成算法",
    author="AI_Gender Project",
    subject="Counting Zero experimental design",
)
doc.build(story)
print(OUTPUT.resolve())
