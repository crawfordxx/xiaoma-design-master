import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

BASE = {
    'project': {'title': '测试片', 'genre': 'tvc', 'duration_s': 10, 'aspect': '16:9',
                'extra_columns': ['卖点']},
    'strategy': {'logline': '一句话', 'beats': [
        {'name': '钩子', 'duration_s': 2, 'purpose': '抓人'},
        {'name': '展示', 'duration_s': 8, 'purpose': '讲卖点'}]},
    'style': {'frame_style': 'realistic-cinema', 'prompt_prefix': '电影感写实'},
    'refs': [{'id': 'hero', 'type': 'product', 'name': '咖啡瓶', 'description': '玻璃瓶',
              'prompt': '一个玻璃咖啡瓶'}],
    'shots': [
        {'no': 1, 'duration_s': 2, 'shot_size': '特写', 'angle': '平视', 'movement': '固定',
         'visual': '冰块落进杯子', 'dialogue': '', 'vo': '', 'transition': '硬切',
         'purpose': '钩子', 'frame_prompt': '冰块落进玻璃杯', 'extra': {'卖点': '冰爽'}, 'refs': []},
        {'no': 2, 'duration_s': 3, 'shot_size': '中景', 'angle': '平视', 'movement': '缓推',
         'visual': '女孩拿起咖啡瓶', 'dialogue': '', 'vo': '早上好', 'transition': '叠化',
         'purpose': '引出产品', 'frame_prompt': '女孩拿起咖啡瓶', 'extra': {'卖点': '便携'},
         'refs': ['hero']},
        {'no': 3, 'duration_s': 5, 'shot_size': '近景', 'angle': '俯拍', 'movement': '环绕',
         'visual': '咖啡瓶立在桌上', 'dialogue': '', 'vo': '', 'transition': '黑场',
         'purpose': '定格产品', 'frame_prompt': '咖啡瓶立在木桌上', 'extra': {'卖点': '颜值'},
         'refs': ['hero']},
    ],
}


@pytest.fixture
def sb():
    return copy.deepcopy(BASE)
