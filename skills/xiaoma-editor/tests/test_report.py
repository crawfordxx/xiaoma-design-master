"""剪辑报告渲染：判定档位、门槛、缺字段时不崩。纯函数，不需要素材。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 直接跑本文件时也能 import _util

import report  # noqa: E402


def base_rep(**over):
    """一份「全过」的报告，测试里逐项改坏。"""
    rep = {
        "video": "ep01.mp4", "duration_s": 79.4, "lufs_target": -16, "asr_used_for_cut": True,
        "loudness": {"integrated_lufs": -16.2, "lra": 6.1, "true_peak_dbfs": -1.8},
        "cuts": {"fps": 30.0, "detected_shots": 33, "flashes": [], "extra_cuts": [],
                 "missing_cuts": [], "duplicates": [], "black_tail_s": 1.0},
        "pacing": {"rows": [{"no": 1, "planned": 2.0, "actual": 2.0, "delta": 0.0,
                             "dialogue": False, "in": 0.4, "flags": []}],
                   "asl": 2.6, "asl_target": [2.2, 3.8], "planned_total": 75.0,
                   "actual_total": 78.4, "over_plan": [], "under_plan": [], "over_5s": []},
        "line_window": [],
        "text": {"dropped": [{"no": 4, "text": "声明并入角标：虚构演绎"}], "leaked_notes": []},
        "sound": {"levels": {"ref_db": -24.6, "bed_db": -44.6, "bgm_db": -38.6, "duck_db": -12.0},
                  "pre_loudnorm_lufs": -24.4, "speech_intervals": [(1.0, 3.0)],
                  "beds": [{"scene": "loc_rain", "from": 0.0, "to": 5.9, "source": "合成兜底（rain）"}],
                  "sfx": [{"t": 0.85, "type": "chime", "gain": 0.6, "no": 1, "source": "合成"}],
                  "music": [{"mood": "drone", "t0": 14.5, "t1": 37.6, "fade_in": 0.8,
                             "fade_out": 0.03, "source": "合成 pad"}],
                  "stray_voice_muted": []},
        "dialogue": {"lines": [{"no": 3, "expected": "这门锁换过了", "heard": "这门锁换过了", "coverage": 1.0}],
                     "low_coverage": [], "unverifiable": [], "straddle": []},
        "sheet": "sheet.jpg",
    }
    rep.update(over)
    return rep


def item(rep, name):
    return next((lvl, msg) for lvl, key, msg in report.verdict(rep) if key == name)


class TestVerdict(unittest.TestCase):
    def test_a_clean_film_passes_everything(self):
        self.assertEqual([lvl for lvl, _, _ in report.verdict(base_rep())],
                         [report.PASS] * len(report.verdict(base_rep())))

    def test_loudness_within_one_lu_is_a_pass(self):
        rep = base_rep(loudness={"integrated_lufs": -16.9})
        self.assertEqual(item(rep, "响度")[0], report.PASS)

    def test_loudness_off_by_three_lu_is_a_fail(self):
        rep = base_rep(loudness={"integrated_lufs": -13.0})
        self.assertEqual(item(rep, "响度")[0], report.FAIL)

    def test_missing_loudness_is_a_warning_not_a_crash(self):
        rep = base_rep(loudness={"integrated_lufs": None})
        self.assertEqual(item(rep, "响度")[0], report.WARN)

    def test_tail_black_over_three_seconds_is_a_fail(self):
        rep = base_rep()
        rep["cuts"]["black_tail_s"] = 4.2
        self.assertEqual(item(rep, "片尾黑场")[0], report.FAIL)

    def test_tail_black_at_the_limit_passes(self):
        rep = base_rep()
        rep["cuts"]["black_tail_s"] = 3.0
        self.assertEqual(item(rep, "片尾黑场")[0], report.PASS)

    def test_flashes_are_a_warning(self):
        rep = base_rep()
        rep["cuts"]["flashes"] = [{"start": 12.0, "end": 12.1, "dur": 0.1, "black": False}]
        self.assertEqual(item(rep, "闪帧")[0], report.WARN)

    def test_duplicate_picture_at_a_cut_is_a_warning(self):
        rep = base_rep()
        rep["cuts"]["duplicates"] = [{"at": 12.0, "sim": 0.93}]
        self.assertEqual(item(rep, "剪点重复画面")[0], report.WARN)

    def test_unplanned_cuts_are_a_warning(self):
        rep = base_rep()
        rep["cuts"]["extra_cuts"] = [5.2]
        self.assertEqual(item(rep, "计划外的切点")[0], report.WARN)

    def test_a_cut_line_is_a_fail(self):
        rep = base_rep(line_window=[{"no": 8, "clipped_head_s": 0.0, "clipped_tail_s": 1.4,
                                     "speech_in_clip": [0.1, 3.4], "window": [0.0, 2.0]}])
        self.assertEqual(item(rep, "台词被剪断")[0], report.FAIL)

    def test_low_character_coverage_is_a_warning_because_homophones(self):
        rep = base_rep()
        rep["dialogue"]["low_coverage"] = [{"no": 10, "coverage": 0.5}]
        self.assertEqual(item(rep, "台词转写覆盖率")[0], report.WARN)

    def test_a_straddling_sentence_without_a_window_check_is_a_fail(self):
        rep = base_rep(line_window=None)
        rep["dialogue"]["straddle"] = [{"at": 20.0, "text": "车里有人", "start": 19.0, "end": 21.0}]
        self.assertEqual(item(rep, "台词跨剪点")[0], report.FAIL)

    def test_a_straddle_the_window_check_explains_away_is_not_a_fail(self):
        """剪辑窗口已证明盖住了人声 → 转写把上一镜尾音和本镜起音合成了一段，不当不合格。"""
        rep = base_rep()
        rep["dialogue"]["straddle"] = [{"at": 57.5, "text": "锁换过了", "start": 57.0, "end": 58.4}]
        level, msg = item(rep, "台词跨剪点")
        self.assertEqual(level, report.PASS)
        self.assertIn("57.50s", msg)

    def test_asl_outside_the_genre_band_is_a_warning(self):
        rep = base_rep()
        rep["pacing"]["asl"] = 4.9
        self.assertEqual(item(rep, "平均镜长")[0], report.WARN)

    def test_asl_slightly_outside_the_band_still_passes(self):
        rep = base_rep()
        rep["pacing"]["asl"] = 4.0
        self.assertEqual(item(rep, "平均镜长")[0], report.PASS)

    def test_total_drift_over_a_quarter_is_a_warning(self):
        rep = base_rep()
        rep["pacing"]["actual_total"] = 120.0
        self.assertEqual(item(rep, "总时长漂移")[0], report.WARN)

    def test_stray_voice_in_a_silent_shot_is_a_warning(self):
        rep = base_rep()
        rep["sound"]["stray_voice_muted"] = [{"no": 18, "from": 41.3, "to": 43.1}]
        self.assertEqual(item(rep, "无台词镜里的人声")[0], report.WARN)

    def test_cutting_without_voice_detection_is_a_warning(self):
        self.assertEqual(item(base_rep(asr_used_for_cut=False), "剪辑没用人声定位")[0], report.WARN)

    def test_no_asr_library_is_reported_as_skipped(self):
        rep = base_rep(dialogue={"skipped": "没装本地转写库"})
        self.assertEqual(item(rep, "台词转写自检")[0], report.WARN)

    def test_notes_leaked_onto_the_screen_are_a_warning(self):
        rep = base_rep(text={"dropped": [], "leaked_notes": [{"no": 2, "text": "竖排画右"}]})
        self.assertEqual(item(rep, "制作备注上屏")[0], report.WARN)

    def test_true_peak_above_minus_one_dbtp_is_a_warning(self):
        rep = base_rep(loudness={"integrated_lufs": -16.0, "true_peak_dbfs": -0.4})
        self.assertEqual(item(rep, "真峰值")[0], report.WARN)


class TestAslRange(unittest.TestCase):
    def test_list_form(self):
        self.assertEqual(report._asl_range([2.2, 3.8]), (2.2, 3.8))

    def test_dash_string_forms(self):
        self.assertEqual(report._asl_range("2.2–3.8"), (2.2, 3.8))
        self.assertEqual(report._asl_range("2.2-3.8"), (2.2, 3.8))
        self.assertEqual(report._asl_range("2.2~3.8"), (2.2, 3.8))

    def test_a_single_number_gets_a_band(self):
        self.assertEqual(report._asl_range("3.0"), (2.4, 3.6))

    def test_junk_and_missing(self):
        self.assertIsNone(report._asl_range(None))
        self.assertIsNone(report._asl_range("快一点"))


class TestRenderMarkdown(unittest.TestCase):
    def test_all_sections_are_present(self):
        md = report.render_markdown(base_rep())
        for head in ("# 剪辑报告", "## 一、总判定", "## 二、节奏", "## 三、剪点",
                     "## 四、声音层", "## 五、台词", "## 六、字卡", "## 七、不合格怎么修"):
            self.assertIn(head, md)

    def test_a_clean_film_says_zero_failures(self):
        self.assertIn("**0 项不合格 / 0 项待人工确认**", report.render_markdown(base_rep()))

    def test_failures_are_counted(self):
        rep = base_rep(loudness={"integrated_lufs": -9.0})
        rep["cuts"]["black_tail_s"] = 5.0
        self.assertIn("**2 项不合格", report.render_markdown(rep))

    def test_marks_are_rendered(self):
        rep = base_rep()
        rep["cuts"]["flashes"] = [{"start": 1.0, "end": 1.1, "dur": 0.1, "black": False}]
        md = report.render_markdown(rep)
        self.assertIn(report.MARK[report.WARN], md)
        self.assertIn(report.MARK[report.PASS], md)

    def test_machine_check_only_report_still_renders(self):
        """没有 edl / storyboard 时只有机检那几节，不能崩。"""
        md = report.render_markdown({"video": "x.mp4", "duration_s": 10.0,
                                     "loudness": {"integrated_lufs": -16.0},
                                     "cuts": {"fps": 30.0, "detected_shots": 4, "flashes": [],
                                              "extra_cuts": [], "missing_cuts": [],
                                              "duplicates": [], "black_tail_s": 1.0}})
        self.assertIn("## 三、剪点", md)
        self.assertNotIn("## 二、节奏", md)

    def test_an_almost_empty_dict_still_renders(self):
        self.assertIn("# 剪辑报告", report.render_markdown({}))

    def test_long_lists_are_truncated_not_dumped(self):
        rep = base_rep()
        rep["sound"]["sfx"] = [{"t": i * 0.1, "type": "tick", "gain": 0.5, "no": i, "source": "合成"}
                               for i in range(200)]
        md = report.render_markdown(rep)
        self.assertIn("…另有", md)
        self.assertLess(len(md), 20000)

    def test_every_pacing_row_reaches_the_table(self):
        rep = base_rep()
        rep["pacing"]["rows"] = [{"no": i, "planned": 2.0, "actual": 2.0, "delta": 0.0,
                                  "dialogue": i % 2 == 0, "in": 0.4, "flags": []} for i in range(1, 33)]
        md = report.render_markdown(rep)
        self.assertIn("| 32 |", md)

    def test_sound_sources_are_named_so_fallbacks_are_visible(self):
        md = report.render_markdown(base_rep())
        self.assertIn("合成兜底（rain）", md)
        self.assertIn("合成 pad", md)

    def test_no_absolute_machine_paths_leak_into_the_report(self):
        md = report.render_markdown(base_rep())
        self.assertNotIn("/Users/", md)
        self.assertNotIn("C:\\", md)


if __name__ == "__main__":
    unittest.main()
