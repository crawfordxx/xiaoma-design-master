# gen-cover 案例：《为什么你收藏了 500 篇教程，还是什么都没学会》

同一篇文章三个创意方向，公众号 2.35:1，主体都在中心 1:1 安全区内，标题上图后交付。

| 方向 | 成品 | 出字方式 |
|---|---|---|
| A 直接冲击 | [cover-A-direct.jpg](cover-A-direct.jpg) | 底图 [base-A.jpg](base-A.jpg) + [cover-A.html](cover-A.html) 排版叠字截图（模型直出两次，标题都伸进了中心安全区） |
| B 氛围 | [cover-B-atmos.jpg](cover-B-atmos.jpg) | 模型直出，逐字校对通过 |
| C 信息可视化 | [cover-C-infoviz.jpg](cover-C-infoviz.jpg) | 底图 [base-C.jpg](base-C.jpg) + [cover-C.html](cover-C.html) 排版叠字截图 |

## 底图提示词 A

```
扁平设计风格的公众号封面，2.35:1 超宽横幅。画面正中的正方形区域内（只占画面中间约 40% 宽度）：一部竖立的智能手机轮廓，屏幕里塞满层层叠叠的书签图标，越堆越高、开始倾斜，顶上三枚书签正在掉出屏幕，下落轨迹用虚线表示。米白纸张底色，深炭黑图形，只有掉落的书签用橘红色。画面左侧 30% 完全留白，只有干净的纸张底色。右侧留白带保持干净。no text, no letters, no words, no numbers, 几何极简，大量留白，2.35:1 aspect ratio
```

## 底图提示词 C

```
信息可视化风格的公众号封面，2.35:1 超宽横幅。画面正中的正方形区域内（只占画面中间约 40% 宽度）：一个简洁的几何漏斗，上方大量密集的深灰小书签图标倒进漏斗，漏斗底部只滴出一颗发光的橘红色小圆点。米白底色，深灰线条，橘红色只用在那颗圆点上。画面左侧 30% 完全留白，只有干净的纸张底色。no text, no letters, no words, no numbers, flat geometric, clean infographic style, 2.35:1 aspect ratio
```

## 提示词 B（模型直出）

```
电影感氛围摄影风格的公众号封面，2.35:1 超宽横幅。画面正中的正方形区域内（只占画面中间约 40% 宽度）：深夜书桌前一个人的侧背影，笔记本电脑屏幕的冷光照亮侧脸，桌上一杯凉掉的咖啡，背后书架虚化成暗色块。蓝调冷色温，屏幕光为唯一主光源，柔和景深，安静略带失落。左侧是幽暗干净的暗部留白带，里面两行白色细字重无衬线标题，左对齐："收藏500篇，" 第二行 "为何没学会"。右侧暗部保持干净。render all text exactly as written, no other text, cinematic lighting, shallow depth of field, 2.35:1 aspect ratio
```
