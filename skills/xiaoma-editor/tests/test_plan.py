"""选入出点纯函数：对白镜整句说完才出点，无台词镜严格按分镜时长。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 直接跑本文件时也能 import _util

from _util import SEG, stereo, tone  # noqa: E402

from plan import HEAD_SKIP, POST, PRE, energy_span, plan_window  # noqa: E402


class TestDialogueWindow(unittest.TestCase):
    """对白镜：绝不切半句。"""

    def test_out_point_waits_for_the_whole_line(self):
        p = plan_window(total=8.0, planned=2.0, has_line=True, speech=(3.0, 5.0),
                        segs=[SEG(0.0, 8.0, False)], events=[])
        self.assertAlmostEqual(p["start"], 3.0 - PRE, places=3)
        self.assertAlmostEqual(p["dur"], (5.0 + POST) - (3.0 - PRE), places=3)
        self.assertLessEqual(p["start"], 3.0)
        self.assertGreaterEqual(p["start"] + p["dur"], 5.0)

    def test_shot_is_stretched_beyond_the_plan_rather_than_cut(self):
        p = plan_window(8.0, 2.0, True, (3.0, 5.0), [SEG(0.0, 8.0, False)], [])
        self.assertGreater(p["dur"], 2.0)          # 计划 2s 装不下 2.6s 的台词 → 拉长

    def test_line_never_runs_past_the_clip(self):
        p = plan_window(5.2, 2.0, True, (3.0, 5.1), [SEG(0.0, 5.2, False)], [])
        self.assertLessEqual(p["start"] + p["dur"], 5.2 + 1e-6)

    def test_takes_the_segment_that_contains_the_line_not_the_longest(self):
        segs = [SEG(0.0, 1.5, False), SEG(1.5, 8.0, False)]
        p = plan_window(8.0, 4.0, True, (0.3, 1.2), segs, [])
        self.assertEqual(p["segment"], [0.0, 1.5])
        self.assertTrue(any("内部有切点" in f for f in p["flags"]))

    def test_line_straddling_an_internal_cut_is_protected_and_flagged(self):
        segs = [SEG(0.0, 2.0, False), SEG(2.0, 8.0, False)]
        p = plan_window(8.0, 4.0, True, (1.0, 3.0), segs, [])
        self.assertTrue(any("跨片段内部切点" in f for f in p["flags"]))
        self.assertLessEqual(p["start"], 1.0)
        self.assertGreaterEqual(p["start"] + p["dur"], 3.0)

    def test_dialogue_shot_without_detected_voice_falls_back_and_warns(self):
        p = plan_window(8.0, 2.5, True, None, [SEG(0.0, 8.0, False)], [])
        self.assertAlmostEqual(p["dur"], 2.5, places=3)
        self.assertTrue(any("没定位到人声" in f for f in p["flags"]))


class TestSilentWindow(unittest.TestCase):
    """无台词镜：严格按分镜时长。"""

    def test_exact_planned_duration(self):
        p = plan_window(8.0, 2.0, False, None, [SEG(0.0, 8.0, False)], [])
        self.assertAlmostEqual(p["dur"], 2.0, places=3)

    def test_skips_the_generated_still_head(self):
        p = plan_window(8.0, 2.0, False, None, [SEG(0.0, 8.0, False)], [])
        self.assertAlmostEqual(p["start"], HEAD_SKIP, places=3)

    def test_no_head_skip_when_the_segment_does_not_start_at_zero(self):
        p = plan_window(8.0, 2.0, False, None, [SEG(0.0, 1.0, False), SEG(1.0, 8.0, False)], [])
        self.assertAlmostEqual(p["start"], 1.0, places=3)
        self.assertAlmostEqual(p["dur"], 2.0, places=3)
        self.assertEqual(p["segment"], [1.0, 8.0])

    def test_segment_shorter_than_the_plan_is_used_up_and_flagged(self):
        p = plan_window(1.5, 3.0, False, None, [SEG(0.0, 1.5, False)], [])
        self.assertAlmostEqual(p["dur"], 1.5, places=3)
        self.assertTrue(any("短于分镜" in f for f in p["flags"]))

    def test_missing_segments_are_treated_as_one_long_take(self):
        p = plan_window(6.0, 2.0, False, None, [], [])
        self.assertEqual(p["segment"], [0.0, 6.0])
        self.assertAlmostEqual(p["dur"], 2.0, places=3)

    def test_window_never_goes_negative_or_past_the_end(self):
        p = plan_window(1.0, 2.0, False, None, [SEG(0.0, 1.0, False)], [])
        self.assertGreaterEqual(p["start"], 0.0)
        self.assertLessEqual(p["start"] + p["dur"], 1.0 + 1e-6)


class TestSliverAvoidance(unittest.TestCase):
    def test_in_point_moves_off_a_bright_flash(self):
        p = plan_window(8.0, 2.0, False, None, [SEG(0.0, 8.0, False)], [2.35])
        self.assertTrue(any("闪帧" in f for f in p["flags"]))
        self.assertAlmostEqual(p["start"], 0.35, places=3)
        self.assertAlmostEqual(p["dur"], 2.0, places=3)

    def test_event_far_from_the_window_changes_nothing(self):
        p = plan_window(8.0, 2.0, False, None, [SEG(0.0, 8.0, False)], [7.0])
        self.assertEqual(p["flags"], [])
        self.assertAlmostEqual(p["start"], HEAD_SKIP, places=3)

    def test_events_outside_the_chosen_segment_are_ignored(self):
        p = plan_window(8.0, 2.0, False, None, [SEG(0.0, 1.0, False), SEG(1.0, 8.0, False)], [0.5])
        self.assertFalse(any("闪帧" in f for f in p["flags"]))


class TestEnergySpan(unittest.TestCase):
    """转写没认出台词时的兜底：人声频带能量。"""

    def test_finds_the_loud_band(self):
        x = np.concatenate([stereo(1.0), tone(1.0, 1000.0, 0.3), stereo(1.0)])
        x += np.random.default_rng(0).normal(0, 1e-4, x.shape).astype(np.float32)
        span = energy_span(x)
        self.assertIsNotNone(span)
        self.assertAlmostEqual(span[0], 1.0, delta=0.15)
        self.assertAlmostEqual(span[1], 2.0, delta=0.15)

    def test_silence_returns_none(self):
        self.assertIsNone(energy_span(stereo(2.0)))

    def test_empty_audio_returns_none(self):
        self.assertIsNone(energy_span(np.zeros((0, 2), np.float32)))

    def test_too_short_to_judge_returns_none(self):
        self.assertIsNone(energy_span(tone(0.05)))

    def test_low_frequency_rumble_is_not_voice(self):
        x = np.concatenate([stereo(1.0), tone(1.0, 60.0, 0.6), stereo(1.0)])
        x += np.random.default_rng(1).normal(0, 1e-4, x.shape).astype(np.float32)
        self.assertIsNone(energy_span(x))


if __name__ == "__main__":
    unittest.main()
