"""生成 3 个复杂模板示例的原始内容（故意用三种格式：Word / Markdown / GBK 编码的 txt）。
用法：python3 tools/make_complex_content.py   数据均为虚构。
"""
import os

import docx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def energy():
    d = docx.Document()
    d.add_paragraph("岳川能源 2026 年度工作汇报", style="Title")
    d.add_paragraph("集团办公室　|　2026 年 12 月")
    d.add_heading("一、2026 年形势分析", 1)
    d.add_heading("外部环境", 2)
    for t in ("用电需求：全社会用电量同比增长 6.8%", "新能源：风光装机首次超过煤电",
              "电价：市场化交易电量占比升至 61%"):
        d.add_paragraph(t, style="List Bullet")
    d.add_heading("我们面临的考验", 2)
    d.add_paragraph("新能源占比快速提高，系统调节能力跟不上；电价市场化以后，发电收益的波动明显变大。")
    d.add_paragraph().add_run("规模不再是唯一目标，效益和安全同样重要。").bold = True
    d.add_heading("二、主要成效", 1)
    d.add_heading("核心指标", 2)
    for t in ("全年发电量 2,860 亿千瓦时", "新能源装机 4,150 万千瓦", "安全生产连续 3,650 天", "供电可靠率 99.97%"):
        d.add_paragraph(t, style="List Bullet")
    d.add_heading("季度发电量（亿千瓦时）", 2)
    rows = [["季度", "2025 年", "2026 年"], ["一季度", "640", "672"], ["二季度", "620", "668"],
            ["三季度", "760", "812"], ["四季度", "650", "708"]]
    tb = d.add_table(rows=len(rows), cols=3)
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            tb.cell(i, j).text = v
    d.add_heading("新能源重点项目", 2)
    for t in ("3 月：青海 200 万千瓦光伏基地开工", "6 月：江苏海上风电二期并网", "9 月：内蒙古储能电站投运",
              "12 月：张北柔直工程全线贯通"):
        d.add_paragraph(t, style="List Bullet")
    d.add_heading("三、存在问题", 1)
    d.add_heading("从「建得快」到「用得好」", 2)
    d.add_paragraph("过去")
    for t in ("比装机规模", "项目各自建设", "靠经验调度"):
        d.add_paragraph(t, style="List Bullet")
    d.add_paragraph("现在")
    for t in ("比发电效益", "场站统一集控", "靠数据调度"):
        d.add_paragraph(t, style="List Bullet")
    d.add_heading("三个短板", 2)
    for t in ("消纳：西北地区弃风弃光率仍有 4.1%", "调节：储能配置比例偏低，仅为 8%",
              "数字化：场站数据孤岛，平均每站 5 套系统"):
        d.add_paragraph(t, style="List Bullet")
    d.add_heading("四、2027 年工作计划", 1)
    d.add_heading("四步推进", 2)
    for t in ("稳存量：完成 30 台煤电机组灵活性改造", "扩增量：新增新能源装机 800 万千瓦",
              "补短板：新建储能 150 万千瓦", "强数字：建成集团统一的新能源集控平台"):
        d.add_paragraph(t, style="List Number")
    d.add_paragraph("“把每一度电都发得清洁、送得稳定、用得高效。”", style="Quote")
    path = os.path.join(ROOT, "examples", "energy", "content.docx")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    d.save(path)


KEYNOTE = """# 星曜 X1 智能眼镜发布会 —— 看见，即理解

2027 年 3 月 18 日 · 深圳

## 产品理念

### 为什么是眼镜

手机让我们低头，电脑让我们坐下。眼镜是唯一一个一直在你视线里、又不需要你伸手的设备。

**最好的界面，是没有界面。**

### 三个设计原则

- **轻**：整机 38 克，和普通眼镜一样
- **静**：不打扰，只在需要时出现
- **准**：看见什么，就理解什么

## 核心能力

### 关键参数

- 整机重量 **38 克**
- 续航 **12 小时**
- 端侧算力 **45 TOPS**
- 识别延迟 **120 毫秒**

### 和上一代相比

**上一代**

- 续航 6 小时
- 重量 52 克
- 需要连接手机

**星曜 X1**

- 续航 12 小时
- 重量 38 克
- 独立运行

## 体验场景

### 一天的使用

- 08:00 通勤路上，实时翻译路牌
- 10:30 会议中，自动生成纪要
- 15:00 维修现场，叠加操作指引
- 20:00 回家路上，提醒购物清单

### 各场景识别准确率（%）

| 场景 | 准确率 |
|---|---|
| 中文翻译 | 96 |
| 会议纪要 | 93 |
| 物体识别 | 91 |
| 操作指引 | 89 |

## 价格与上市

### 三个版本

- **标准版**：3,999 元，日常佩戴
- **专业版**：5,999 元，支持行业应用
- **开发者版**：6,999 元，开放全部接口

### 上市节奏

1. 3 月 18 日：开启预约
2. 4 月 1 日：首批发货
3. 5 月：进入 30 个城市的线下门店

> 我们想做的，是一副你忘了自己戴着的眼镜。—— 星曜科技创始人 林知远
"""

CONSULTING = """中国工商业储能市场研究与进入策略
为华铸智造准备的讨论文件
2026 年 10 月

一、市场概览
（一）装机三年增长 6 倍，规模持续扩大
年份\t新增装机（GWh）
2023\t4.2
2024\t9.8
2025\t17.5
2026\t26.0

（二）三个因素推动需求快速释放
峰谷价差：23 个省份价差超过 0.7 元/千瓦时
电芯降价：储能电芯价格两年下降 58%
政策支持：17 个省份出台工商业储能补贴

二、竞争格局
（一）前五名企业合计占据 52% 份额
企业\t市场份额（%）
企业 A\t16
企业 B\t13
企业 C\t9
企业 D\t8
企业 E\t6
其他\t48

（二）竞争正在从拼价格转向拼运营
过去的做法：
• 比设备单价
• 一次性卖设备
现在的做法：
• 比全周期收益
• 设备加运营服务

三、能力评估
（一）华铸的优势集中在制造和客户
制造：自有电池包产线，成本低于行业 8%
客户：已服务 1,200 家制造业客户
短板：缺少电力交易和运维团队

四、实施建议
（一）分三步进入，18 个月盈亏平衡
1. 0–6 个月：在长三角 3 个园区做示范项目
2. 6–12 个月：组建电力交易和运维团队
3. 12–18 个月：复制到 50 家存量客户
“先把自己工厂的储能做好，就是最好的样板间。”
"""


def main():
    energy()
    for name, text, enc in (("keynote/content.md", KEYNOTE, "utf-8"), ("consulting/content.txt", CONSULTING, "gb18030")):
        path = os.path.join(ROOT, "examples", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(text.encode(enc))
    print("ok")


if __name__ == "__main__":
    main()
