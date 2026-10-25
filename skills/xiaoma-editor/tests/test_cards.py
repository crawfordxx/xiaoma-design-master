"""字幕与字卡：「内容（备注）」分离、类型判定、序列编号、屏幕区域换算。

 fixture 全是本测试自己编的（作品名《夜班车》，角色周野 / 老陈），不取自任何真实样片。
排版部分要真字体，找不到中文字体时整组 skip（不算失败）。
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 直接跑本文件时也能 import _util

import cards  # noqa: E402
from common import EditorError, find_font  # noqa: E402

try:
    FONT = find_font()
except EditorError:
    FONT = None


class TestLineText(unittest.TestCase):
    def test_strips_speaker_and_quotes(self):
        self.assertEqual(cards.line_text("周野：“这门锁换过了。”"), "这门锁换过了。")

    def test_strips_acting_note_in_parentheses(self):
        self.assertEqual(cards.line_text("老陈（背过身）：“钥匙给我。”"), "钥匙给我。")

    def test_plain_text_passes_through(self):
        self.assertEqual(cards.line_text("他还在车上"), "他还在车上")

    def test_empty_and_none(self):
        self.assertEqual(cards.line_text(None), "")
        self.assertEqual(cards.line_text(""), "")

    def test_long_speaker_prefix_is_not_treated_as_a_speaker(self):
        # 冒号前超过 12 字不是「角色：台词」，整句保留
        raw = "这一整段很长的旁白说明文字：后面才是内容"
        self.assertEqual(cards.line_text(raw), raw)

    def test_inner_parenthetical_is_dropped_but_the_line_survives(self):
        self.assertEqual(cards.line_text("苏晚（压低声音）：“别开灯。”"), "别开灯。")


class TestParseOst(unittest.TestCase):
    def test_production_note_is_split_off_and_never_reaches_the_screen(self):
        got, dropped = cards.parse_ost("周野 · 夜班司机（竖排名牌，画右，后期合成）")
        self.assertEqual([c.text for c in got], ["周野 · 夜班司机"])
        self.assertEqual([c.kind for c in got], ["name"])
        self.assertEqual(dropped, ["备注：竖排名牌，画右，后期合成"])
        self.assertFalse(any("后期" in c.text or "画右" in c.text for c in got))

    def test_name_keyword_makes_a_name_card(self):
        self.assertEqual(cards.parse_ost("老陈 · 车库看门人（人名条）")[0][0].kind, "name")

    def test_screen_keyword_makes_a_screen_card(self):
        got, _ = cards.parse_ost("2024年3月8日 23:40（屏幕合成）")
        self.assertEqual([c.kind for c in got], ["screen"])
        self.assertEqual(got[0].text, "2024年3月8日 23:40")

    def test_title_keyword_makes_a_title_card(self):
        got, _ = cards.parse_ost("夜班车（片名）")
        self.assertEqual([c.kind for c in got], ["title"])

    def test_no_keyword_falls_back_to_caption(self):
        got, _ = cards.parse_ost("他还在车上")
        self.assertEqual([c.kind for c in got], ["caption"])

    def test_short_time_looking_part_becomes_a_time_card(self):
        got, _ = cards.parse_ost("深夜11:40（时间字卡）")
        self.assertEqual(got[0].kind, "time")

    def test_a_long_time_looking_sentence_stays_a_title(self):
        # 时间卡限 16 字：再长就是句子，不是时间卡
        got, _ = cards.parse_ost("2019年那个下着雨的深夜十一点整，一切都变了（片名）")
        self.assertEqual(got[0].kind, "title")

    def test_disclaimer_becomes_a_corner_label_not_a_card(self):
        got, dropped = cards.parse_ost("深夜11:40 ／ 夜班车 ／ 虚构演绎（时间字卡 + 片名 + 片名下小字）")
        self.assertEqual([c.text for c in got], ["深夜11:40", "夜班车"])
        self.assertEqual([c.kind for c in got], ["time", "title"])
        self.assertIn("声明并入角标：虚构演绎", dropped)

    def test_ai_disclaimer_wording_is_also_dropped(self):
        _, dropped = cards.parse_ost("AI 生成（片名）")
        self.assertTrue(any("声明并入角标" in d for d in dropped))

    def test_only_a_disclaimer_leaves_no_card(self):
        got, dropped = cards.parse_ost("本故事纯属虚构（片名下小字）")
        self.assertEqual(got, [])
        self.assertEqual(len(dropped), 2)          # 备注 + 声明各一条

    def test_empty_input(self):
        self.assertEqual(cards.parse_ost(None), ([], []))
        self.assertEqual(cards.parse_ost("   "), ([], []))

    def test_multiple_cards_are_sequenced_not_stacked(self):
        got, _ = cards.parse_ost("11:39 → 11:40（屏幕合成）")
        self.assertEqual([(c.start, c.end) for c in got], [(0.0, 0.5), (0.5, 1.0)])

    def test_three_cards_split_the_shot_into_thirds(self):
        got, _ = cards.parse_ost("一楼 ／ 二楼 ／ 三楼（地点卡）")
        self.assertEqual(len(got), 3)
        for i, c in enumerate(got):
            self.assertAlmostEqual(c.start, i / 3, places=6)
            self.assertAlmostEqual(c.end, (i + 1) / 3, places=6)

    def test_a_single_card_spans_the_whole_shot(self):
        got, _ = cards.parse_ost("11:40（屏幕合成）")
        self.assertEqual([(c.start, c.end) for c in got], [(0.0, 1.0)])

    def test_a_slash_separated_list_of_places_is_not_a_screen(self):
        got, _ = cards.parse_ost("青山路 ／ 十七号（地点卡）")
        self.assertEqual([c.kind for c in got], ["title", "title"])


class TestScreenBox(unittest.TestCase):
    """shot.screen_box 是相对片段原画面的 0–1 比例，输出画面是等比放大 + 居中裁切。"""

    def test_landscape_source_into_portrait_output(self):
        box = cards.map_screen_box([0.4, 0.4, 0.2, 0.2], 1280, 720, 720, 1280)
        self.assertIsNotNone(box)
        x, y, w, h = box
        self.assertEqual((x, y, w, h), (132, 512, 455, 256))

    def test_result_stays_inside_the_frame(self):
        for src, out in [((1280, 720), (720, 1280)), ((720, 1280), (720, 1280)), ((1920, 804), (1280, 720))]:
            box = cards.map_screen_box([0.05, 0.05, 0.9, 0.9], src[0], src[1], out[0], out[1])
            self.assertIsNotNone(box)
            x, y, w, h = box
            self.assertGreaterEqual((x, y), (0, 0))
            self.assertLessEqual(x + w, out[0])
            self.assertLessEqual(y + h, out[1])

    def test_missing_or_malformed_box_returns_none(self):
        self.assertIsNone(cards.map_screen_box(None, 1280, 720, 720, 1280))
        self.assertIsNone(cards.map_screen_box([0.1, 0.1], 1280, 720, 720, 1280))
        self.assertIsNone(cards.map_screen_box([0.1, 0.1, 0.2, 0.2], 0, 0, 720, 1280))

    def test_a_box_too_small_to_hold_text_returns_none(self):
        self.assertIsNone(cards.map_screen_box([0.5, 0.5, 0.001, 0.001], 1280, 720, 720, 1280))


@unittest.skipUnless(FONT, "机器上没有中文字体，跳过排版测试")
class TestTypesetter(unittest.TestCase):
    W, H = 720, 1280

    def setUp(self):
        self.ts = cards.Typesetter(FONT, self.W, self.H)

    def test_subtitle_sits_in_the_lower_safe_area(self):
        im, x, y = self.ts.subtitle("这门锁换过了。")
        self.assertGreater(y, self.H * 0.5)
        self.assertLessEqual(y + im.height, self.H)
        self.assertGreaterEqual(x, 0)
        self.assertLessEqual(x + im.width, self.W)

    def test_corner_label_is_top_right_and_small(self):
        im, x, y = self.ts.label("AI 生成 · 纯属虚构")
        self.assertEqual((x, y), (self.W - im.width - 12, 12))

    def test_every_card_kind_lands_inside_the_frame(self):
        for kind, text in [("name", "周野 · 夜班司机"), ("screen", "11:40"), ("title", "夜班车"),
                           ("time", "深夜11:40"), ("caption", "他还在车上")]:
            for im, x, y in self.ts.place(cards.Card(kind, text), None):
                self.assertGreaterEqual((x, y), (0, 0), kind)
                self.assertLessEqual(x + im.width, self.W, kind)
                self.assertLessEqual(y + im.height, self.H, kind)
                self.assertEqual(im.mode, "RGBA", kind)

    def test_screen_card_without_a_box_goes_to_the_middle_info_panel(self):
        im, x, y = self.ts.place(cards.Card("screen", "11:39"), None)[0]
        cy = y + im.height / 2
        self.assertGreater(cy, self.H * 0.3)
        self.assertLess(cy, self.H * 0.6)

    def test_screen_card_with_a_box_fills_exactly_that_box(self):
        box = (100, 200, 300, 160)
        im, x, y = self.ts.place(cards.Card("screen", "11:39 → 11:40"), box)[0]
        self.assertEqual((x, y, im.width, im.height), box)

    def test_text_is_actually_drawn(self):
        import numpy as np
        im = self.ts.text_png("夜班车", 46, self.W * 0.8, box=False)
        self.assertGreater(np.asarray(im)[:, :, 3].max(), 200)

    def test_long_text_wraps_instead_of_overflowing(self):
        im = self.ts.text_png("这一句很长很长很长很长的字卡内容需要折行", 30, self.W * 0.6, box=True)
        self.assertLessEqual(im.width, self.W * 0.6 + 60)

    def test_sizes_scale_with_the_canvas(self):
        small = cards.Typesetter(FONT, 360, 640)
        self.assertAlmostEqual(small.font(30).size, 15, delta=1)
        self.assertEqual(self.ts.font(30).size, 30)


if __name__ == "__main__":
    unittest.main()
