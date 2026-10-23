"""示例的「第 3 步：逐页改 deck.json」——模型在 plan.py 草稿上做的修改，写成脚本以便复现。
用法：python3 tools/refine_examples.py（在 plan.py 出草稿之后、build.py 之前运行）
"""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")


def edit(ex, fn):
    p = os.path.join(ROOT, ex, "deck.json")
    d = json.load(open(p, encoding="utf-8"))
    fn({s.get("title"): s for s in d["slides"] if s.get("body")})
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def finance(s):
    s["核心指标全面达成"]["source"] = "示例数据"
    p = s["管理规模连续五个季度增长"]
    p["body"].update(highlight=4, takeaway={"value": "18.6", "unit": "%", "title": "同比增长",
                                            "text": "连续五个季度环比增长，三季度单季净增 67 亿元"})
    p["source"] = "示例数据 · 单位：亿元"
    s["收入结构更均衡"]["source"] = "示例数据"
    s["高净值客户成为增长主力"].update(lead="高净值客户只占 4.5%，户均资产是大众客户的 30 倍", source="示例数据")


def medical(s):
    p = s["血压控制率稳步提升"]
    p["body"]["takeaway"] = {"value": "+17", "unit": "个百分点", "title": "十个月提升", "text": "从 1 月的 51% 提升到 10 月的 68%"}
    p["source"] = "示例数据"
    p = s["一年来的关键数字"]
    p["source"] = "示例数据"
    short = {"覆盖社区卫生": "覆盖社区中心", "纳入管理慢病": "纳入管理患者", "家庭医生随访工时": "随访工时节省"}
    for it in p["body"]["items"]:
        for k, v in short.items():
            if it["title"].startswith(k):
                it["title"] = v


def education(s):
    p = s["一场面试的真实成本"]
    p["source"] = "预测效度：Schmidt & Hunter (1998), Psychological Bulletin 124(2)"
    a, b, c = p["body"]["items"]
    a.update(title="面试官人均每年", text="参加的面试场次（内部数据）")
    b.update(title="非结构化面试", text="预测效度")
    c.update(title="结构化面试", text="预测效度")


def manufacturing(s):
    p = s["OEE 逐月提升"]
    p["body"]["takeaway"] = {"value": "82", "unit": "%", "title": "10 月 OEE", "text": "比年初提升 14 个百分点，熔炼车间最高达 86%"}
    p["source"] = "示例数据"
    s["各车间进度不均衡"].update(lead="涂装车间两项指标都垫底，是明年的改造重点", source="示例数据")
    p = s["一年下来的变化"]
    p["source"] = "示例数据"
    for it in p["body"]["items"]:
        if "OEE" in it["title"]:
            it["title"] = "设备综合效率 OEE"


def tourism(s):
    p = s["游客量持续增长"]
    p["body"].update(highlight=4, takeaway={"value": "2.5", "unit": "倍", "title": "四年增长（420 → 1,050 万人次）"})
    p["source"] = "示例数据 · 单位：万人次"
    s["客源结构"].update(lead="长三角游客占比 27%，是增长最快的客源地", source="示例数据")


def short_tracker(ex, names):
    """进度标签格子很窄：换成短章节名"""
    p = os.path.join(ROOT, ex, "deck.json")
    d = json.load(open(p, encoding="utf-8"))
    for sl in d["slides"]:
        if sl.get("tracker"):
            sl["tracker"]["items"] = names
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def energy(s):
    s["核心指标"]["source"] = "示例数据"
    for it in s["核心指标"]["body"]["items"]:
        if it["value"] == "2,860":
            it.update(unit="亿千瓦时", text="")
    s["季度发电量（亿千瓦时）"]["source"] = "示例数据 · 单位：亿千瓦时"
    s["三个短板"]["body"] = {"type": "cards", "items": [
        {"title": "消纳", "text": "西北地区弃风弃光率仍有 4.1%", "icon": "triangle-alert"},
        {"title": "调节", "text": "储能配置比例偏低，仅为 8%", "icon": "gauge"},
        {"title": "数字化", "text": "场站数据孤岛，平均每站 5 套系统", "icon": "database"}]}
    s["三个短板"]["_why"] = "三个问题各有一句说明 → 卡片（草稿选成了大数字，会丢掉说明）"


def keynote(s):
    p = s["各场景识别准确率（%）"]
    p["body"]["highlight"] = 0
    p["source"] = "示例数据"


def consulting(s):
    src = "资料来源：示例数据；衡策咨询分析"
    for t, sl in s.items():
        if sl["body"]["type"] in ("chart", "stats", "cards", "compare"):
            sl["source"] = src
    s["装机三年增长 6 倍，规模持续扩大"]["body"]["highlight"] = 3


if __name__ == "__main__":
    short_tracker("energy", ["形势分析", "主要成效", "存在问题", "工作计划"])
    for fn in (energy, keynote, consulting):
        edit(fn.__name__, fn)
        print("refined", fn.__name__)
    for fn in (finance, medical, education, manufacturing, tourism):
        edit(fn.__name__, fn)
        print("refined", fn.__name__)
