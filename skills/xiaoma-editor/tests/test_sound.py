"""声音三层 + 混音：各层长度必须严格等于成片长度，电平关系和避让要对。

不碰 ffmpeg：素材目录一律指向不存在的路径（走合成兜底），
需要读音频的地方用 monkeypatch 把 `sound.read_audio` 换成 numpy 假数据。
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 直接跑本文件时也能 import _util

from _util import missing_dir, shot, timeline, timing, tone  # noqa: E402

import sound  # noqa: E402
from common import SR, db, rms, undb  # noqa: E402

N = 3 * SR                      # 3 秒成片
NO_ASSETS = missing_dir(Path(__file__).resolve().parent)
REFS = [{"id": "loc_rain", "type": "location", "name": "雨夜路口", "description": "雨"},
        {"id": "loc_room", "type": "location", "name": "楼梯间", "description": "水泥墙"},
        {"id": "loc_street", "type": "location", "name": "街口", "description": "外立面"},
        {"id": "hero", "type": "character", "name": "主角", "description": "男"}]


class TestLayerLengths(unittest.TestCase):
    """核心验收：每一层的样本数都等于成片样本数，差一个样本成片就会音画错位。"""

    def setUp(self):
        self.tl = timeline([1.0, 1.0, 1.0],
                           {1: {"scene": "loc_rain", "music": "无"},
                            2: {"scene": "loc_room", "music": "极低的低频长音进"},
                            3: {"scene": "loc_room", "music": ""}})

    def test_bed_layer_is_exactly_n_samples(self):
        bed, used = sound.render_beds(self.tl, REFS, NO_ASSETS, N)
        self.assertEqual(len(bed), N)
        self.assertTrue(used)

    def test_music_layer_is_exactly_n_samples(self):
        music, used = sound.render_music(sound.plan_music(self.tl), NO_ASSETS, N)
        self.assertEqual(len(music), N)
        self.assertTrue(used)

    def test_sfx_layer_is_exactly_n_samples(self):
        cues = [{"t": 0.2, "type": "hit", "gain": 0.8}, {"t": 2.9, "type": "riser", "gain": 0.5}]
        fx, used = sound.render_sfx(cues, NO_ASSETS, N)
        self.assertEqual(len(fx), N)
        self.assertEqual(len(used), 2)

    def test_a_cue_near_the_end_does_not_make_the_layer_longer(self):
        fx, _ = sound.render_sfx([{"t": 2.99, "type": "hit", "gain": 0.9}], NO_ASSETS, N)
        self.assertEqual(len(fx), N)

    def test_mixed_output_is_n_frames_of_stereo(self):
        bed, _ = sound.render_beds(self.tl, REFS, NO_ASSETS, N)
        music, _ = sound.render_music(sound.plan_music(self.tl), NO_ASSETS, N)
        fx, _ = sound.render_sfx([{"t": 1.0, "type": "tick", "gain": 0.6}], NO_ASSETS, N)
        out, levels = sound.mix(tone(3.0), bed, music, fx, [(0.5, 2.5)], N)
        self.assertEqual(out.shape, (N, 2))
        self.assertTrue(np.isfinite(out).all())
        self.assertEqual(set(levels), {"ref_db", "bed_db", "bgm_db", "duck_db"})

    def test_every_layer_is_n_even_when_the_timeline_is_shorter(self):
        short = timeline([0.5, 0.5])                    # 1s 时间线，3s 成片（片尾黑场）
        bed, used = sound.render_beds(short, REFS, NO_ASSETS, N)
        self.assertEqual(len(bed), N)
        self.assertAlmostEqual(used[-1]["to"], N / SR, places=3)   # 最后一段铺到成片结尾

    def test_fit_pads_and_truncates_to_n(self):
        self.assertEqual(len(sound.fit(np.ones(10, np.float32), N)), N)
        self.assertEqual(len(sound.fit(np.ones(N + 500, np.float32), N)), N)
        self.assertEqual(sound.fit(np.ones((10, 2), np.float32), N).shape, (N, 2))

    def test_mix_pads_a_short_dialogue_track(self):
        out, _ = sound.mix(tone(1.0), np.zeros(N, np.float32), np.zeros(N, np.float32),
                           np.zeros(N, np.float32), [(0.0, 0.5)], N)
        self.assertEqual(out.shape, (N, 2))
        self.assertEqual(np.abs(out[int(1.5 * SR):]).max(), 0.0)   # 后面是补的零


class TestLevelsAndDucking(unittest.TestCase):
    def setUp(self):
        self.dialog = tone(3.0, 1000.0, 0.2)
        self.ref = db(rms(self.dialog[:, 0]))
        self.speech = [(0.5, 2.5)]

    def test_bed_sits_20db_below_the_dialogue(self):
        bed = np.ones(N, np.float32)
        out, levels = sound.mix(self.dialog, bed, np.zeros(N, np.float32),
                                np.zeros(N, np.float32), self.speech, N)
        self.assertAlmostEqual(db(rms(out[:, 0] - self.dialog[:, 0])), self.ref + sound.BED_REL_DB, delta=0.6)
        self.assertAlmostEqual(levels["bed_db"], self.ref + sound.BED_REL_DB, delta=0.1)

    def test_music_is_ducked_inside_the_dialogue(self):
        music = np.ones(N, np.float32)
        g = sound.duck_envelope(N, self.speech)
        out, _ = sound.mix(self.dialog, np.zeros(N, np.float32), music,
                           np.zeros(N, np.float32), self.speech, N)
        inside = out[:, 0][int(1.0 * SR):int(2.0 * SR)] - self.dialog[:, 0][int(1.0 * SR):int(2.0 * SR)]
        outside = out[:, 0][:int(0.2 * SR)] - self.dialog[:, 0][:int(0.2 * SR)]
        drop = db(rms(outside)) - db(rms(inside))
        self.assertAlmostEqual(drop, -sound.DUCK_DB, delta=1.0)     # 对白段低约 12 dB
        self.assertAlmostEqual(float(g[int(1.5 * SR)]), undb(sound.DUCK_DB), places=6)

    def test_duck_envelope_is_flat_without_dialogue(self):
        self.assertTrue((sound.duck_envelope(1000, []) == 1.0).all())

    def test_duck_envelope_ramps_in_and_out(self):
        g = sound.duck_envelope(N, [(1.0, 2.0)], ramp=0.2)
        self.assertEqual(g[0], 1.0)
        self.assertEqual(g[int(0.7 * SR)], 1.0)                     # 还没到坡道
        self.assertLess(g[int(0.9 * SR)], 1.0)                      # 提前 0.2s 开始降
        self.assertLess(g[int(2.1 * SR)], 1.0)                      # 之后 0.2s 才回来
        self.assertEqual(g[-1], 1.0)

    def test_reference_uses_only_the_dialogue_spans(self):
        loud = np.concatenate([np.zeros((SR, 2), np.float32), tone(1.0, 440.0, 0.5)])
        self.assertAlmostEqual(sound.reference_db(loud, [(1.0, 2.0)]), db(0.5 / np.sqrt(2)), delta=0.2)

    def test_silence_falls_back_to_a_fixed_reference(self):
        self.assertEqual(sound.reference_db(np.zeros((SR, 2), np.float32), []), sound.FALLBACK_REF_DB)


class TestBeds(unittest.TestCase):
    def test_scene_comes_from_the_shot_then_the_location_ref_then_the_previous_shot(self):
        shots = [shot(1, 2.0, scene="loc_rain"), shot(2, 2.0, refs=["loc_room"]),
                 shot(3, 2.0), shot(4, 2.0, refs=["hero"])]
        self.assertEqual(sound.assign_scenes(shots, REFS),
                         ["loc_rain", "loc_room", "loc_room", "loc_room"])

    def test_a_leading_shot_without_a_scene_inherits_the_first_known_one(self):
        shots = [shot(1, 2.0), shot(2, 2.0, scene="loc_room")]
        self.assertEqual(sound.assign_scenes(shots, REFS), ["loc_room", "loc_room"])

    def test_bed_preset_picks_rain_outdoor_or_room(self):
        self.assertEqual(sound.bed_preset({"description": "雨夜"}), "rain")
        self.assertEqual(sound.bed_preset({"description": "街口外立面"}), "outdoor")
        self.assertEqual(sound.bed_preset({"description": "水泥楼梯间"}), "room")
        self.assertEqual(sound.bed_preset(None), "room")

    def test_every_span_reports_where_its_audio_came_from(self):
        tl = timeline([1.5, 1.5], {1: {"scene": "loc_rain"}, 2: {"scene": "loc_room"}})
        _, used = sound.render_beds(tl, REFS, NO_ASSETS, N)
        self.assertEqual([u["scene"] for u in used], ["loc_rain", "loc_room"])
        self.assertTrue(all("合成兜底" in u["source"] for u in used))
        self.assertEqual(used[0]["from"], 0.0)
        self.assertAlmostEqual(used[1]["to"], 3.0, places=2)

    def test_a_real_asset_file_is_preferred_over_synthesis(self):
        """把 find_asset / read_audio 换成假的：有素材就用素材，没素材才合成。"""
        orig_find, orig_read = sound.find_asset, sound.read_audio
        sound.find_asset = lambda folder, name: Path("bed.wav") if name == "loc_rain" else None
        sound.read_audio = lambda *a, **k: tone(2.0, 200.0, 0.4)
        try:
            tl = timeline([1.5, 1.5], {1: {"scene": "loc_rain"}, 2: {"scene": "loc_room"}})
            bed, used = sound.render_beds(tl, REFS, NO_ASSETS, N)
        finally:
            sound.find_asset, sound.read_audio = orig_find, orig_read
        self.assertEqual([u["source"] for u in used], ["素材 bed.wav", "合成兜底（room）"])
        self.assertEqual(len(bed), N)

    def test_synthesised_beds_are_audible_and_finite(self):
        for preset in ("rain", "outdoor", "room"):
            x = sound.synth_bed(preset, SR)
            self.assertEqual(len(x), SR)
            self.assertTrue(np.isfinite(x).all())
            self.assertGreater(rms(x), 1e-4, preset)

    def test_an_empty_bed_request_gives_silence(self):
        self.assertEqual(len(sound.synth_bed("room", 0)), 0)


class TestLoadLoop(unittest.TestCase):
    """交叉淡化循环铺满：靠注入假 read_audio，不需要 ffmpeg。"""

    def setUp(self):
        self._orig = sound.read_audio

    def tearDown(self):
        sound.read_audio = self._orig

    def _patch(self, seconds, freq=200.0, amp=0.5):
        sound.read_audio = lambda *a, **k: tone(seconds, freq, amp)

    def test_a_short_asset_is_looped_up_to_n(self):
        self._patch(0.5)
        x = sound.load_loop(Path("x.wav"), N)
        self.assertEqual(len(x), N)
        self.assertGreater(rms(x), 1e-4)                    # 循环之后不是静音

    def test_a_long_asset_is_truncated_to_n(self):
        self._patch(10.0)
        self.assertEqual(len(sound.load_loop(Path("x.wav"), N)), N)

    def test_a_silent_asset_gives_silence_not_nan(self):
        sound.read_audio = lambda *a, **k: np.zeros((0, 2), np.float32)
        x = sound.load_loop(Path("x.wav"), N)
        self.assertEqual(len(x), N)
        self.assertEqual(np.abs(x).max(), 0.0)


class TestSfxCues(unittest.TestCase):
    def test_knock_count_is_read_from_the_text(self):
        cues = sound.parse_sfx("敲门三下", 3.0, [])
        self.assertEqual([c["type"] for c in cues], ["thud"] * 3)
        self.assertAlmostEqual(cues[1]["t"] - cues[0]["t"], 0.32, places=3)

    def test_knock_without_a_count_defaults_to_three(self):
        self.assertEqual(len(sound.parse_sfx("敲门", 3.0, [])), 3)

    def test_the_first_clause_lands_on_a_picture_event(self):
        cues = sound.parse_sfx("接单提示音一声", 1.6, [0.5])
        self.assertEqual(cues[0]["type"], "pop")
        self.assertAlmostEqual(cues[0]["t"], 0.5, places=3)

    def test_a_sound_that_stops_is_not_played(self):
        self.assertEqual(sound.parse_sfx("电流声消失", 2.0, []), [])

    def test_end_anchored_sound_lands_on_the_last_frame(self):
        cues = sound.parse_sfx("钥匙一响与黑场同落", 4.0, [])
        self.assertEqual(cues[0]["type"], "chime")
        self.assertAlmostEqual(cues[0]["t"], 3.95, places=3)

    def test_clauses_are_spread_across_the_shot(self):
        cues = sound.parse_sfx("咔哒一声；数字滚动", 3.0, [])
        self.assertEqual([c["type"] for c in cues][0], "tick")
        self.assertLess(cues[0]["t"], cues[-1]["t"])

    def test_no_text_no_cues(self):
        self.assertEqual(sound.parse_sfx(None, 2.0, []), [])
        self.assertEqual(sound.parse_sfx("", 2.0, []), [])
        self.assertEqual(sound.parse_sfx("雨声", 2.0, []), [])     # 雨声是底噪的活，不是音效

    def test_the_same_type_always_uses_the_same_sound(self):
        fx, used = sound.render_sfx([{"t": 0.1, "type": "tick", "gain": 0.6},
                                     {"t": 1.0, "type": "tick", "gain": 0.6}], NO_ASSETS, N)
        self.assertEqual(len(fx), N)
        self.assertEqual({u["source"] for u in used}, {"合成"})
        a = fx[int(0.1 * SR):int(0.1 * SR) + 100]
        b = fx[int(1.0 * SR):int(1.0 * SR) + 100]
        self.assertTrue(np.allclose(a, b))                        # 同一条素材 → 母题一致

    def test_key_beats_get_a_riser_then_a_hit(self):
        tl = [timing(7, 10.0, 2.0, shot(7, 2.0, beat="反转"), events=[0.8])]
        cues = sound.beat_cues([{"name": "反转", "purpose": "揭开真相"}], tl)
        self.assertEqual([c["type"] for c in cues], ["riser", "hit"])
        self.assertAlmostEqual(cues[1]["t"], 10.8, places=3)
        self.assertAlmostEqual(cues[0]["t"], 8.8, places=3)

    def test_a_riser_never_starts_before_the_film(self):
        tl = [timing(1, 0.0, 2.0, shot(1, 2.0, beat="钩子反转"))]
        cues = sound.beat_cues([{"name": "钩子反转", "purpose": ""}], tl)
        self.assertEqual(cues[0]["t"], 0.0)

    def test_ordinary_beats_get_no_cue(self):
        tl = [timing(1, 0.0, 2.0, shot(1, 2.0, beat="铺垫"))]
        self.assertEqual(sound.beat_cues([{"name": "铺垫", "purpose": "交代"}], tl), [])


class TestMusicPlan(unittest.TestCase):
    def test_mood_keywords(self):
        self.assertEqual(sound.music_mood("上行的弦乐"), "rise")
        self.assertEqual(sound.music_mood("极低频长音，压抑"), "drone")
        self.assertEqual(sound.music_mood("随便来点"), "pad")

    def test_no_music_means_no_segment(self):
        self.assertEqual(sound.plan_music(timeline([1.0, 1.0], {1: {"music": "无"}, 2: {"music": "无"}})), [])

    def test_a_missing_field_inherits_the_previous_mood(self):
        tl = timeline([1.0, 1.0, 1.0], {1: {"music": "低频长音"}, 2: {"music": ""}, 3: {"music": ""}})
        segs = sound.plan_music(tl)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0]["mood"], "drone")
        self.assertAlmostEqual(segs[0]["t1"], 3.0, places=3)

    def test_a_hard_stop_cuts_in_30ms(self):
        tl = timeline([1.0, 1.0], {1: {"music": "低频长音"}, 2: {"music": "低频长音同时抽掉"}})
        segs = sound.plan_music(tl)
        self.assertEqual(len(segs), 1)
        self.assertAlmostEqual(segs[0]["fade_out"], 0.03, places=3)
        self.assertAlmostEqual(segs[0]["t1"], 1.0, places=3)

    def test_a_soft_stop_fades_out(self):
        tl = timeline([1.0, 1.0], {1: {"music": "弦乐长音"}, 2: {"music": "弦乐长音停"}})
        segs = sound.plan_music(tl)
        self.assertAlmostEqual(segs[0]["fade_out"], 0.4, places=3)

    def test_a_mood_change_starts_a_new_segment(self):
        tl = timeline([1.0, 1.0], {1: {"music": "低频长音"}, 2: {"music": "上行弦乐"}})
        segs = sound.plan_music(tl)
        self.assertEqual([s["mood"] for s in segs], ["drone", "rise"])
        self.assertAlmostEqual(segs[0]["t1"], segs[1]["t0"], places=3)

    def test_rendered_segments_cover_their_planned_span(self):
        tl = timeline([1.0, 1.0], {1: {"music": "低频长音"}, 2: {"music": ""}})
        music, used = sound.render_music(sound.plan_music(tl), NO_ASSETS, N)
        self.assertEqual(len(music), N)
        self.assertEqual(used[0]["source"], "合成 pad")
        self.assertGreater(rms(music[:int(1.5 * SR)]), 1e-4)
        self.assertEqual(rms(music[int(2.2 * SR):]), 0.0)      # 计划外不出声

    def test_synthesised_music_is_finite(self):
        for mood in ("drone", "rise", "pad"):
            x = sound.synth_music(mood, SR)
            self.assertEqual(len(x), SR)
            self.assertTrue(np.isfinite(x).all(), mood)


class TestAssetLookup(unittest.TestCase):
    def test_missing_folder_gives_none(self):
        self.assertIsNone(sound.find_asset(NO_ASSETS, "room"))

    def test_supported_extensions(self):
        self.assertIn(".wav", sound.AUDIO_EXT)
        self.assertIn(".flac", sound.AUDIO_EXT)


if __name__ == "__main__":
    unittest.main()
