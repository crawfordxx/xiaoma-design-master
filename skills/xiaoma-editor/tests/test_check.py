"""check.py 里不碰 ffmpeg 的纯函数：台词窗口核对、节奏统计、字卡审计。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 直接跑本文件时也能 import _util

from _util import shot, storyboard  # noqa: E402

import check  # noqa: E402


def plan(no, start, dur, planned=None, has_line=False, speech_clip=None, flags=None, cards_=None):
    return {"no": no, "start": start, "dur": dur, "planned": planned if planned is not None else dur,
            "has_line": has_line, "speech_clip": speech_clip, "flags": flags or [],
            "at": start, "in": start, "cards": cards_ or []}


class TestLineWindow(unittest.TestCase):
    """不靠转写判断台词有没有被剪断：剪辑窗口必须盖住素材里量到的人声。"""

    def test_a_window_covering_the_line_passes(self):
        p = plan(3, 1.17, 2.87, has_line=True, speech_clip=(1.2, 3.9))
        self.assertEqual(check.line_window_check([p]), [])

    def test_out_point_before_the_line_ends_is_reported(self):
        p = plan(8, 0.0, 2.0, has_line=True, speech_clip=(0.1, 3.4))
        got = check.line_window_check([p])
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["no"], 8)
        self.assertAlmostEqual(got[0]["clipped_tail_s"], 1.4, places=2)
        self.assertEqual(got[0]["clipped_head_s"], 0.0)

    def test_in_point_after_the_line_starts_is_reported(self):
        p = plan(9, 2.0, 2.0, has_line=True, speech_clip=(1.0, 3.0))
        got = check.line_window_check([p])
        self.assertAlmostEqual(got[0]["clipped_head_s"], 1.0, places=2)

    def test_tiny_slack_is_not_a_cut(self):
        p = plan(1, 0.0, 2.0, has_line=True, speech_clip=(0.02, 1.98))
        self.assertEqual(check.line_window_check([p]), [])

    def test_silent_shots_are_not_checked(self):
        self.assertEqual(check.line_window_check([plan(1, 0.0, 2.0, speech_clip=(0.0, 5.0))]), [])

    def test_a_dialogue_shot_without_voice_detection_is_not_checked(self):
        self.assertEqual(check.line_window_check([plan(1, 0.0, 2.0, has_line=True)]), [])


class TestPacing(unittest.TestCase):
    def setUp(self):
        self.sb = storyboard([shot(1, 2.0), shot(2, 6.0)], asl=[2.2, 3.8])

    def test_asl_and_totals(self):
        plans = [plan(1, 0.0, 2.0, planned=2.0), plan(2, 2.0, 6.0, planned=3.0)]
        got = check.pacing(plans, self.sb)
        self.assertEqual(got["asl"], 4.0)
        self.assertEqual(got["planned_total"], 5.0)
        self.assertEqual(got["actual_total"], 8.0)
        self.assertEqual(got["asl_target"], [2.2, 3.8])

    def test_over_and_under_plan_use_a_two_frame_tolerance(self):
        plans = [plan(1, 0.0, 2.2, planned=2.0), plan(2, 2.2, 1.8, planned=2.0), plan(3, 4.0, 2.02, planned=2.0)]
        got = check.pacing(plans, self.sb)
        self.assertEqual([r["no"] for r in got["over_plan"]], [1])
        self.assertEqual([r["no"] for r in got["under_plan"]], [2])

    def test_shots_longer_than_five_seconds_are_listed(self):
        plans = [plan(1, 0.0, 5.03, planned=3.2)]
        self.assertEqual([r["no"] for r in check.pacing(plans, self.sb)["over_5s"]], [1])

    def test_rows_carry_the_planning_flags_through(self):
        plans = [plan(1, 0.0, 2.0, planned=2.0, flags=["片段内部有切点，取 1.00–3.00s 这一段"])]
        self.assertTrue(check.pacing(plans, self.sb)["rows"][0]["flags"][0].startswith("片段内部有切点"))


class TestTextAudit(unittest.TestCase):
    def test_a_production_note_on_screen_is_flagged(self):
        plans = [plan(1, 0.0, 2.0, cards_=[{"kind": "title", "text": "竖排名牌，画右"}])]
        got = check.text_audit(plans, [])
        self.assertEqual(got["leaked_notes"], [{"no": 1, "text": "竖排名牌，画右"}])

    def test_clean_cards_are_not_flagged(self):
        plans = [plan(1, 0.0, 2.0, cards_=[{"kind": "name", "text": "周野 · 夜班司机"},
                                           {"kind": "time", "text": "深夜11:40"}])]
        self.assertEqual(check.text_audit(plans, [])["leaked_notes"], [])

    def test_dropped_text_is_passed_through_for_the_report(self):
        dropped = [{"no": 4, "text": "声明并入角标：虚构演绎"}]
        self.assertEqual(check.text_audit([], dropped)["dropped"], dropped)


class TestLoudnessParsing(unittest.TestCase):
    """ebur128 的 Summary 段解析（不跑 ffmpeg，直接喂文本）。"""

    LOG = """[Parsed_ebur128_0 @ 0x1] Summary:
  Integrated loudness:
    I:         -16.4 LUFS
    Threshold: -26.5 LUFS
  Loudness range:
    LRA:         6.2 LU
    Threshold: -36.5 LUFS
  True peak:
    Peak:       -1.8 dBFS
"""

    def test_fields_are_read(self):
        import re

        def get(key, tail):
            return (re.search(key + r":\s*(-?[\d.]+)", tail) or [None, None])[1]
        tail = self.LOG[self.LOG.rfind("Summary:"):]
        self.assertEqual(check._f(get("I", tail)), -16.4)
        self.assertEqual(check._f(get("LRA", tail)), 6.2)
        self.assertEqual(check._f(get("Peak", tail)), -1.8)

    def test_missing_field_is_none(self):
        self.assertIsNone(check._f(None))
        self.assertIsNone(check._f(""))


if __name__ == "__main__":
    unittest.main()
