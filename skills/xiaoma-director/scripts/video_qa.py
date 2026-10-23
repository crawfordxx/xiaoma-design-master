"""出片后质检：按七个维度给每镜打分（0-100），按阈值判决并给修复建议。

七维（来自一线 AI 视频产线的质检口径）：
  画面质量 / 主体一致性 / 构图 / 运镜 / 时长 / 合规 / 提示词忠实

判决（默认阈值 75，修复带 ±15）：
  pass   ≥ 阈值
  repair ≥ 阈值-15：优先「局部修改」——拿原片加指令改问题点，省额度也保住其余画面
  fail   再低：整镜重出

用法：
  python3 video_qa.py <dir>/storyboard.json --scores '{"3": {"画面质量": 70, ...}}'
评分写回 shot.video.qa = {scores, total, verdict, advice}。
"""
import json
import sys

DIMENSIONS = ('画面质量', '主体一致性', '构图', '运镜', '时长', '合规', '提示词忠实')
THRESHOLD = 75
REPAIR_BAND = 15


def score(scores, threshold=THRESHOLD):
    """七维齐全且 0-100 才收；返回 {scores, total, verdict}。"""
    for dim in DIMENSIONS:
        v = scores.get(dim)
        if v is None:
            raise ValueError(f'缺维度「{dim}」，七维都要打分')
        if not isinstance(v, (int, float)) or not 0 <= v <= 100:
            raise ValueError(f'维度「{dim}」分数非法：{v}（0-100）')
    total = round(sum(scores[d] for d in DIMENSIONS) / len(DIMENSIONS), 1)
    if total >= threshold:
        verdict = 'pass'
    elif total >= threshold - REPAIR_BAND:
        verdict = 'repair'
    else:
        verdict = 'fail'
    return {'scores': dict(scores), 'total': total, 'verdict': verdict}


def repair_advice(shot, verdict, reasons):
    """按判决给修复建议：repair 走局部修改，fail 整镜重出，pass 不用。"""
    if verdict == 'pass':
        return None
    why = '、'.join(reasons) if reasons else '综合评分不足'
    if verdict == 'repair':
        return f"镜头 {shot['no']} 局部修改：{why}（拿原片加指令改，其余画面不动）"
    return f"镜头 {shot['no']} 整镜重出：{why}"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    import sbcommon
    sb = sbcommon.load_storyboard(argv[0])
    scores_in = json.loads(argv[argv.index('--scores') + 1]) if '--scores' in argv else {}
    threshold = float(argv[argv.index('--threshold') + 1]) if '--threshold' in argv else THRESHOLD
    changed = 0
    for shot in sb['shots']:
        video = shot.get('video') or {}
        if not video.get('url') or str(shot['no']) not in scores_in:
            continue
        try:
            r = score({**scores_in[str(shot['no'])]}, threshold=threshold)
        except ValueError as e:
            print(f'✗ 镜头 {shot['no']}:{e}')
            return 1
        low = [d for d in DIMENSIONS if r['scores'][d] < threshold]
        r['advice'] = repair_advice(shot, r['verdict'], low)
        video['qa'] = r
        shot['video'] = video
        changed += 1
        print(f"镜头 {shot['no']}: {r['total']} → {r['verdict']}" + (f" | {r['advice']}" if r['advice'] else ''))
    sbcommon.write_json(argv[0], sb)
    print(f'✓ 已写回 {changed} 镜的质检结果 → {argv[0]}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
