"""镜头切分、内部切点选段、剪点重复帧、闪帧、黑场尾巴。

全部用 _util 造的假帧（numpy），不解码任何视频，不需要 ffmpeg。
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 直接跑本文件时也能 import _util

from _util import FPS, SEG, black, brighten, concat, pattern, ramp  # noqa: E402

import scenecut as sc  # noqa: E402


class TestDetectCuts(unittest.TestCase):
    def test_hard_cut_between_two_structures_is_found(self):
        frames = concat(pattern(1, 30), pattern(2, 60))
        cuts = sc.detect_cuts(frames, FPS)
        self.assertEqual(cuts, [1.0])          # 第 30 帧起是第二段 → 1.0s

    def test_identical_frames_have_no_cut(self):
        self.assertEqual(sc.detect_cuts(pattern(3, 45), FPS), [])

    def test_gradual_exposure_change_is_not_a_cut(self):
        self.assertEqual(sc.detect_cuts(ramp(pattern(4, 45)), FPS), [])

    def test_light_turning_on_is_not_a_cut(self):
        frames = concat(pattern(5, 20), brighten(pattern(5, 20), 1.9))
        self.assertEqual(sc.detect_cuts(frames, FPS), [])

    def test_black_boundary_counts_as_a_cut(self):
        frames = concat(pattern(6, 20), black(20), pattern(7, 20))
        self.assertEqual(sc.detect_cuts(frames, FPS), [round(20 / FPS, 3), round(40 / FPS, 3)])

    def test_segments_split_on_every_cut(self):
        frames = concat(pattern(1, 30), pattern(2, 3), pattern(3, 30))
        segs = sc.segments(frames, FPS)
        self.assertEqual([(s.start, s.end) for s in segs], [(0.0, 1.0), (1.0, 1.1), (1.1, 2.1)])
        self.assertFalse(any(s.black for s in segs))

    def test_whole_black_span_is_marked(self):
        frames = concat(pattern(1, 30), black(30))
        segs = sc.segments(frames, FPS)
        self.assertEqual([s.black for s in segs], [False, True])

    def test_black_between_two_frames_is_not_a_change(self):
        sim = sc.adjacent_similarity(black(5))
        self.assertTrue((sim == 1.0).all())


class TestChooseSegment(unittest.TestCase):
    """片段内部自带切镜时，只取一段。"""

    def setUp(self):
        # 3 帧一段：短段在前（0–1s），长段在后（1–3s）
        self.frames = concat(pattern(11, 30), pattern(12, 60))
        self.segs = sc.segments(self.frames, FPS)
        self.assertEqual(len(self.segs), 2)

    def test_picks_the_segment_containing_speech_even_if_shorter(self):
        got = sc.choose_segment(self.segs, (0.2, 0.8))
        self.assertEqual((got.start, got.end), (0.0, 1.0))

    def test_picks_the_longest_non_black_segment_without_speech(self):
        got = sc.choose_segment(self.segs, None)
        self.assertEqual((got.start, got.end), (1.0, 3.0))

    def test_speech_outside_every_segment_falls_back_to_longest(self):
        got = sc.choose_segment(self.segs, (9.0, 9.5))
        self.assertEqual((got.start, got.end), (1.0, 3.0))

    def test_black_segment_is_never_chosen(self):
        segs = [SEG(0.0, 4.0, True), SEG(4.0, 5.0, False)]
        self.assertEqual(sc.choose_segment(segs, None).start, 4.0)

    def test_all_black_falls_back_to_longest_overall(self):
        segs = [SEG(0.0, 1.0, True), SEG(1.0, 3.0, True)]
        self.assertEqual(sc.choose_segment(segs, None).start, 1.0)

    def test_overlap_is_clamped_to_zero(self):
        self.assertEqual(sc.overlap((0.0, 1.0), (2.0, 3.0)), 0.0)
        self.assertAlmostEqual(sc.overlap((0.0, 2.0), (1.0, 3.0)), 1.0)


class TestAvoidSlivers(unittest.TestCase):
    seg = SEG(0.0, 8.0, False)

    def test_in_point_too_close_to_an_event_is_pushed_back(self):
        start, moved = sc.avoid_slivers(2.95, 2.0, [3.0], self.seg)
        self.assertTrue(moved)
        self.assertAlmostEqual(start, 2.7, places=3)      # 突变前至少留 0.3s

    def test_event_near_the_out_point_moves_the_window(self):
        start, moved = sc.avoid_slivers(1.0, 1.95, [2.9], self.seg)
        self.assertTrue(moved)
        self.assertAlmostEqual(start, 0.95, places=3)     # 出点从突变前 0.05s 挪到突变上
        gap = abs((start + 1.95) - 2.9)
        self.assertFalse(0 < gap < 0.3)                   # 出点不再贴着突变

    def test_no_event_near_the_window_leaves_it_alone(self):
        start, moved = sc.avoid_slivers(1.0, 2.0, [6.0], self.seg)
        self.assertFalse(moved)
        self.assertEqual(start, 1.0)

    def test_a_sliver_is_allowed_rather_than_cutting_the_line(self):
        # 台词占满了整个窗口：挪开突变就会切掉半句 → 宁可不挪
        start, moved = sc.avoid_slivers(1.0, 2.0, [2.95], self.seg, keep=(1.0, 3.0))
        self.assertEqual((start, moved), (1.0, False))

    def test_the_window_it_moves_to_still_covers_the_line(self):
        start, moved = sc.avoid_slivers(1.0, 2.5, [3.4], self.seg, keep=(1.2, 2.8))
        self.assertTrue(moved)
        self.assertLessEqual(start, 1.2 + 1e-6)
        self.assertGreaterEqual(start + 2.5, 2.8 - 1e-6)

    def test_window_is_never_pushed_out_of_its_segment(self):
        seg = SEG(2.0, 4.0, False)
        start, moved = sc.avoid_slivers(2.0, 2.0, [2.1], seg)   # 窗口已经占满整段
        self.assertFalse(moved)                            # 段里没地方可挪 → 保持原样
        self.assertEqual(start, 2.0)


class TestFilmChecks(unittest.TestCase):
    def test_flash_shorter_than_300ms_is_reported(self):
        frames = concat(pattern(21, 30), pattern(22, 3), pattern(23, 30))
        shots = sc.film_shots(frames, FPS)
        fl = sc.flashes(shots)
        self.assertEqual(len(fl), 1)
        self.assertAlmostEqual(fl[0]["start"], 1.0, places=3)
        self.assertLess(fl[0]["dur"], 0.3)

    def test_a_long_enough_shot_is_not_a_flash(self):
        frames = concat(pattern(24, 30), pattern(25, 30))
        self.assertEqual(sc.flashes(sc.film_shots(frames, FPS)), [])

    def test_tail_black_is_not_a_flash(self):
        frames = concat(pattern(26, 30), black(6))
        self.assertEqual(sc.flashes(sc.film_shots(frames, FPS)), [])

    def test_duplicate_picture_at_a_cut(self):
        # 第 0–39 帧同一结构（=剪点两侧画面重复），第 40 帧起才换
        frames = concat(pattern(31, 20), pattern(31, 20), pattern(32, 20))
        dup = sc.duplicate_at_cuts(frames, FPS, [20 / FPS])
        self.assertEqual(len(dup), 1)
        self.assertGreaterEqual(dup[0]["sim"], 0.8)

    def test_clean_cut_has_no_duplicate(self):
        frames = concat(pattern(31, 20), pattern(31, 20), pattern(32, 20))
        self.assertEqual(sc.duplicate_at_cuts(frames, FPS, [40 / FPS]), [])

    def test_black_frames_are_ignored_when_looking_for_duplicates(self):
        frames = concat(pattern(33, 20), black(20), pattern(33, 20))
        self.assertEqual(sc.duplicate_at_cuts(frames, FPS, [20 / FPS]), [])

    def test_black_tail_length(self):
        frames = concat(pattern(34, 30), black(15))
        self.assertAlmostEqual(sc.black_tail(frames, FPS), 0.5, places=3)

    def test_no_black_tail(self):
        self.assertAlmostEqual(sc.black_tail(pattern(35, 30), FPS), 0.0, places=3)


if __name__ == "__main__":
    unittest.main()
