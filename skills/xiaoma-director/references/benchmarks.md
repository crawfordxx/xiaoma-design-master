# 顶尖范本实测与来源

片种卡里的结构、节奏和「顶尖范本」都来自这里的调研：向国内外公认的导演和作品学分镜编排，一部分范本下载到本机切镜实测，量完即删，只留数字。写分镜时只读片种卡就够了；想知道某条规则、某个参数从哪来，查这里。

## 怎么测的

- **范本**：每个片种 4–7 部，国内外大致各半；「顶尖」的依据是大奖（戛纳、One Show、D&AD、奥斯卡、金马等）、行业公认的导演和工作室、平台头部播放量、被反复拉片教学。
- **来源**：B站、抖音、小红书、知乎、YouTube、TikTok、Reddit、Instagram、X 上的拉片、分镜拆解和幕后视频（读字幕），以及 StudioBinder、No Film School、Art of the Title、案例页、导演访谈等文章。
- **切镜**：PySceneDetect AdaptiveDetector（阈值 3.0，最小镜长 0.25 秒）。叠化、淡化、同机位跳切会漏检，快闪和滚动水印会多检，每部都抽帧人工复核，修正值写在备注里。MG、录屏、一镜到底这类靠形变和推拉转场的，切镜数字没有意义，改用抽帧看「画面状态」。
- **语速**：B站字幕时间轴，或下载音轨用本机 Whisper 转写。「净」= 字数 ÷ 说话时长，「毛」= 字数 ÷ 首句到末句的跨度（含停顿）。
- **节奏审核参数**：取值原则是让顶尖范本被机检误判的镜头不超过一成；平均镜长区间要包住范本实测值。台词旁白的偏紧误判有一部分来自测量口径（一句话跨过切点被拆进两镜），写分镜时整句落在一镜里，所以 `cps` 没有为压误判率而调高；而且每镜不超过 5 字/秒是校验红线。

## 节奏审核参数：调研前 → 调研后

| 片种 | asl | cps | slack | hold | hook |
|---|---|---|---|---|---|
| TVC 广告（`tvc`） | 1.5-3 → **1.2-3** | 3.5 | 1 | 3.5 → **4** | 3 |
| 品牌形象宣传片（`brand-film`） | 2-5 → **1.5-3** | 3.5 | 1.5 | 6 | 0 |
| 竖屏短剧（`short-drama`） | 2-3.5 → **2-4** | 4.5 | 1 → **4** | 4 → **5.5** | 5 |
| 教程 / 操作演示（`tutorial`） | 3-10 → **2.5-10** | 4 → **4.5** | 1.5 | 8 | 0 |
| 产品宣传片（`product-promo`） | 1.5-3.5 → **1.3-3** | 3.5 | 1 | 4 | 3 → **10** |
| 文旅 / 城市宣传片（`city-tourism`） | 1.5-6 → **1.2-3** | 3 | 2 | 8 | 0 |
| 微电影 / 剧情短片（`micro-film`） | 3-6 → **3-8** | 4 | 2 → **5** | 8 → **12** | 0 |
| 动画短片（`animation`） | 3-5 → **3-7** | 4 | 1.5 → **4.5** | 6 → **10** | 0 |
| 知识科普 / 解说（`explainer`） | 3-8 → **2.5-6** | 4 → **4.5** | 1.5 | 6 | 0 → **15** |
| MG 动画 / 数据可视化（`motion-graphics`） | 3-6 | 4 | 1 | 5 | 5 |
| 达人口播 / 带货种草（`creator-ad`） | 1.5-4 → **1.3-3** | 4.5 → **5** | 0.8 | 3 | 3 |
| 纪录片 / 人物纪实（`documentary`） | 5-12 → **2.5-9** | 4 → **3.5** | 4 | 15 | 0 |
| MV / 音乐短片（`mv`） | 0.5-6 → **0.8-4** | 4 | 2 | 8 → **10** | 0 |
| Vlog（`vlog`） | 2-8 → **2-6** | 4.5 | 3 → **2** | 12 → **8** | 0 → **15** |
| 预告片 / 游戏 PV（`trailer-pv`） | 1.5-3 → **1.2-3** | 3.5 | 1 | 6 | 6 |
| 片头 / 活动开场片（`opening-title`） | 1-3 | 3 | 0.8 | 4 | 3 → **5** |
| 发布会 / 活动纪实（`event-recap`） | 1-4 | 4 | 1.5 | 8 | 6 → **4** |

## TVC 广告（`tvc`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 士力架《林黛玉篇》15s（BBDO 平台中国版） | 全片 0–15.2s | 11 | 1.39 | 1.36 | 0.32–2.66 | 3 | 落版 3.4s（22%）；产品 7.8s 入画 |
| 士力架《林黛玉篇》30s | 全片 0–29s | 19 | 1.53 | 1.24 | 0.80–3.24 | 2 | 揭示镜 4.48s 最长；落版 4.7s（16%） |
| 《1984》（Ridley Scott，1984 戛纳 GP） | 0–60s | 35（机检 36） | 1.71（机检 1.67） | 0.92 | 0.39–3.37 | 0 | 叠化漏检、跟拍多检已抽帧修正；落版约 10s（字卡 + logo） |
| 《Write the Future》（Iñárritu，2011 戛纳 Film GP） | 全片 0–183.2s | 167 | 1.10 | 0.72 | 0.35–2.35 | 2 | 0.2s 快闪是真剪辑；落版 4.8s |
| 999 感冒灵《有人偷偷爱着你》 | 0.8–264.9s | 89（机检 96） | 2.97（机检 2.75） | 1.70 | 0.23–5.68 | 0 | 灯光闪烁多检约 11 刀；logo 只在最后约 3s |

语速：无可靠实测（士力架对白混环境声转写失败，999 靠字幕不靠旁白）。

被误判估算（实测镜长，按 review.py 规则，无台词镜看清下限按 1s、不计运镜加成与「停留」，偏保守）：hold 3.5 时 10.6%（999 占 25%），hold 4 时 9.1%（短 TVC 0–6%，999 22%）。

pace 取值依据：
- asl 1.5-3 → 1.2-3：士力架 15s 1.39、《Write the Future》1.10；上限 3 留给分钟级网络片（999 2.97）
- cps 维持 3.5：没测到可靠的 TVC 旁白语速，卡片 3–4 字/秒与 director-review 影视对白区间一致
- slack 维持 1：调到 1.5 误判率不变（10.6%），说明拖沓误判来自无台词长镜，与 slack 无关
- hold 3.5 → 4：取 3.5 时五部范本 10.6% 的镜头被判拖沓，取 4 降到 9.1%，满足「≤10%」；短片 p90 2.66–3.37 仍在线内
- hook 维持 3：士力架笑点在第 1–2.1s；System1、Kantar 都把品牌线索放在前 2–5 秒

来源：
1. Cog (advertisement) — Wikipedia — https://en.wikipedia.org/wiki/Cog_(advert)
2. 1984 (advertisement) — Wikipedia — https://en.wikipedia.org/wiki/1984_(advertisement)
3. Write the Future — Wikipedia — https://en.wikipedia.org/wiki/Write_the_Future
4. Freedom is slavery — Diggit Magazine — https://www.diggitmagazine.com/articles/freedom-slavery-apple-macintosh-television-commercial-1984
5. 1984 model analysis — philpot.education — https://philpot.education/mod/page/view.php?id=350
6. YouTube & Google ABCD Reference Guide — Google — https://services.google.com/fh/files/misc/youtube_google_abcd_reference_guide_en.pdf
7. Validating Google's ABCD framework — Kantar — https://www.kantar.com/industries/technology-and-telecoms/validating-googles-abcd-framework-with-the-power-of-artificial-intelligence
8. This Isn't Another "Just Stick a Logo on It" Piece — System1 — https://system1group.com/blog/this-isnt-another-just-stick-a-logo-on-it-piece
9. Kantar Super Bowl Ad Study — Kantar — https://www.kantar.com/north-america/company-news/kantar-super-bowl-ad-study-15-second-ads-match-30-second-spots
10. When is the best time to introduce a brand — Quirk's — https://www.quirks.com/articles/when-is-the-best-time-to-introduce-a-brand-in-a-commercial
11. R.I.P. Leon — The Stable — https://www.thestable.com.au/tbwamedia-arts-lab-a-dead-lizard-and-a-mad-mum-show-off-what-iphone-14-can-do/
12. Apple × 陈可辛《三分钟》项目页 — 数英 — https://www.digitaling.com/projects/25700.html
13. 陈可辛《三分钟》让 iPhone X 走下了神坛 — 数英 — https://www.digitaling.com/articles/43452.html
14. 999 感冒灵文章 — 数英 — https://www.digitaling.com/articles/42967.html
15. Snickers — Wikipedia — https://en.wikipedia.org/wiki/Snickers
16. Commercials, 30 seconds or not to 30 seconds — Reddit r/editors — https://www.reddit.com/r/editors/comments/ju8gmg/
17. 【深度拉片】TVC 分镜脚本设计解析 — B站 后期风水学PP导 — https://www.bilibili.com/video/BV1zS421A78V
18. 【深度拉片】产品广告逐分镜脚本设计解析 — B站 布斯D — https://www.bilibili.com/video/BV1dH4y1c75G
19. In Video Advertising, Is Longer Stronger? — Think with Google — https://www.thinkwithgoogle.com/_qs/documents/1110/TwG20UK-In-Video-Advertising.pdf
20. 实测原片：https://www.bilibili.com/video/BV1Hb4y1G7mu ；https://www.bilibili.com/video/BV1rG4y1i7bt ；https://www.bilibili.com/video/BV1Si421k744 ；https://www.bilibili.com/video/BV1qs411e7oJ ；https://www.bilibili.com/video/BV1kW41187mi

## 品牌形象宣传片（`brand-film`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| B站《后浪》（2020 龙玺全场大奖、金投赏全场大奖） | 全片 0–232.8s | 146 | 1.59 | 0.90 | 0.44–3.64 | 0 | 何冰近景长镜 8–14s 做锚点，素材 0.5–0.8s；落版 8.5s |
| 大众银行《梦骑士》（台湾奥美，WARC 亚洲效果案例） | 全片 0–182.7s | 102 | 1.79 | 1.57 | 0.64–3.12 | 1 | 转折在 45s（25%）；logo 179s 首现；落版 9.5s |
| New Balance《致匠心》（李宗盛） | 全片 0–210.9s | 106（机检 104） | 1.99（机检 2.03） | 1.58 | 0.70–3.44 | 0 | 前 20s 无旁白；成品鞋 199.5s 才完整出现 |
| Dove《Real Beauty Sketches》（2013 戛纳 Titanium GP） | 全片 0–180.1s | 77（机检 74） | 2.34（机检 2.43） | 1.97 | 1.02–3.52 | 1 | 91.5s 揭晓停 7.1s；落版 12.5s |

语速（本地 mlx_whisper 转写，剔除幻觉段；毛 = 字数 ÷ 去掉 >2s 间隙的说话时段）：
- 《后浪》 · 毛 3.28 / 段内 3.85 字/秒（660 字 / 201.3s，覆盖约 86%）
- 《致匠心》 · 毛 3.06 / 段内 3.45 字/秒（376 字 / 122.8s，覆盖约 58%，第一句前留白 20s）
- 《梦骑士》 · 句内约 3.6 字/秒（约 111 字 / 逐句合计 30.8s，覆盖约 17%）
- Dove（英文采访原声） · 2.65 词/秒（356 词 / 134.5s，覆盖约 75%）

被误判估算（镜长 + 转写时间轴按时长分摊到镜，看清下限按 1s）：cps 3.5 / slack 1.5 / hold 6 时偏紧 27.9%、拖沓 6.1%；cps 3.3 时偏紧升到 29.6%；slack 1 / hold 4 时拖沓 8.0%。偏紧集中在《后浪》（旁白连续压过快切素材，逐镜分摊后每镜都「念不完」），是逐镜模型的局限。

pace 取值依据：
- asl 2-5 → 1.5-3：实测 4 部 1.59–2.34，卡片原「人物叙事型 3.5–5s」无一部做到，已删
- cps 维持 3.5（调研报告曾建议 3.3，未采纳）：毛语速 3.06–3.28，但段内 3.45–3.85；review.py 逐镜算，旁白跨镜流动，取 3.3 反而让顶尖范本偏紧误判从 27.9% 升到 29.6%
- slack 维持 1.5、hold 维持 6：拖沓误判 6.1%（≤10%）；收紧到 slack 1 / hold 4 也只到 8%，但没有证据需要收
- hook 维持 0：《致匠心》开场刻意留白 20s，不宜机检

来源：
1. Dove Real Beauty Sketches — Wikipedia — https://en.wikipedia.org/wiki/Dove_Real_Beauty_Sketches
2. Real Beauty Sketches — dove.com — https://www.dove.com/pr/stories/campaigns/real-beauty-sketches.html
3. Think different — Wikipedia — https://en.wikipedia.org/wiki/Think_different
4. Iñárritu directs two-minute anthem — Shoot Online — https://shootonline.com/?p=27747
5. #LikeAGirl 上线报道 — Shoot Online — https://shootonline.com/?p=34477
6. 胡湘云访谈 — 经理人 — https://www.managertoday.com.tw/articles/view/9656
7. 《梦骑士》文案 — 钛媒体 — https://www.tmtpost.com/32622.html
8. 《梦骑士》背景 — 数英 — https://www.digitaling.com/articles/279222.html
9. Everyone is a Dream Ranger — WARC — https://www.warc.com/content/article/warc-awards-asia/ta-chong-bank-everyone-is-a-dream-ranger/en-gb/97638
10. SG 胜加龙玺获奖 — 数英 — https://www.digitaling.com/articles/381878.html
11. SG 胜加金投赏 2020 — 数英 — https://www.digitaling.com/articles/363313.html
12. 《后浪》文案拆解 — 数英 — https://www.digitaling.com/articles/320473.html
13. W × New Balance — 数英 — https://www.digitaling.com/articles/29171.html
14. 《致匠心》 — 界面 — https://www.jiemian.com/article/284573.html
15. 《油烟情书》文案 — 数英 — https://www.digitaling.com/articles/40795.html
16. 点评粉丝作品之教育品牌宣传片 — B站 映美剪辑实战学院 — https://www.bilibili.com/video/BV1GYgVzeEN6
17. 实测原片：https://www.bilibili.com/video/BV1FV411d7u7 ；https://www.bilibili.com/video/BV1zD4y1R7ux ；https://www.bilibili.com/video/BV1Bs411E7NX ；https://www.bilibili.com/video/BV1ei4y1u7Bu

## 竖屏短剧（`short-drama`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 《盛夏芬德拉》（红果 2025 年度冠军，44.4 亿） | B站官方开篇合集 0–984s（约前 7 集） | 277 | 3.55 | 3.07 | 0.57–6.61 | 0 | 顶部滚动水印每 5s 误切，裁掉上下水印后复测（未裁 306 镜 / 3.22） |
| 《盛夏芬德拉》 | 第 1 集 0–151.5s | 28 | 5.41 | 4.83 | 1.54–11.42 | 0 | 12s 闪前冷开场；茶室剪影长停留 10–14s；集尾转身反应 11s |
| 《一品布衣》（红果 2025 年度破 30 亿） | 第 1–3 集 0–480s | 167 | 2.87 | 2.37 | 1.06–5.01 | 0 | 打斗闪白碎镜约 6 个 |
| 《一品布衣》 | 开场 90 秒 | 35 | 2.57 | 2.27 | 1.15–4.05 | 0 | 首镜 3.3s 古城远景 |
| The Double Life of My Billionaire Husband（ReelShort，播放超 4.19 亿） | 第 1 集全集 99s | 42 | 2.37 | 2.12 | 0.85–4.51 | 3 | 片名卡 + 航拍 + 道具快切后转客厅正反打 |
| Sleeping with the Enemy（ReelShort） | 第 1–10 集 0–785s | 232 | 3.38 | 2.90 | 1.22–6.43 | 0 | 搬运「片段赏析」版；暗调多，可能少检；顶尖依据弱，只作对照 |

切镜口径：PySceneDetect AdaptiveDetector 3.0，最小镜长 0.25s，1–2fps 联系表人工抽查。景别为人工抽中间帧判读（误差约一档）：腰部以上单人合计 Double Life 86%、一品布衣开场 60%、盛夏芬德拉第 1 集 47%（全景 39%）；严格的「近景及更近」只有 21–29%。

语速（mlx-whisper large-v3-turbo，间隔 ≤0.8s 的段并成一组，毛语速 = 字数 ÷ 组跨度）：
- 盛夏芬德拉 合集 · 加权 4.22 / 中位 4.84 字/秒（1979 字 / 469.4s）
- 盛夏芬德拉 第 1 集 · 5.47 字/秒（380 字 / 69.5s，信息密集）
- 一品布衣 前 8 分钟 · 加权 3.89 / 中位 3.94 字/秒（796 字 / 204.8s）
- 台词覆盖时长：两部均约 48%；「口播式」爆款第 1 集 76%（拉片【9】）

逐镜台词负载（台词按词级时间戳分到各镜，≥4 字的台词镜）：余量（镜长 − 字数÷4.5）中位 0.97 / 1.30，p75 1.96 / 2.11；无台词镜中位 2.00 / 2.47，p90 3.77 / 5.60（一品布衣 / 盛夏芬德拉）。

转折间隔：Double Life 第 1 集 4–21s，中位约 11s；一品布衣开头 13–31s；盛夏芬德拉第 1 集 15–36s。

机检误判率（按 review.py 判定线模拟：顶尖范本的镜头被判偏紧/拖沓的比例；取值口径 = 每部范本误判 ≤10% 的最紧值）。
台词按 mlx-whisper 词级时间戳分到各镜；台词镜 拖沓 = 镜长 > max(字数÷cps, 1.0) + slack；无台词镜（镜内没有任何词）拖沓 = 镜长 > max(1.0 + slack, hold)，按固定机位算（实际有运镜会再多一份 slack，所以表里偏严）；外语片只用转写区分有无台词，不参与 slack。

| 范本 | 台词镜 / 无台词镜 | 偏紧 @cps 4 / 4.5 / 5 | 拖沓 @slack 1 / 2 / 3 / 3.5 / 4 / 5 | 超限 @hold 4 / 5 / 5.5 / 6 / 8（slack=4） |
|---|---|---|---|---|
| 一品布衣 前 8 分钟 | 113 / 54 | 13% / 7% / 4% | 44% / 21% / 11% / 5% / 4% / 3% | 2% / 2% / 0% / 0% / 0% |
| 盛夏芬德拉 合集 | 184 / 93 | 19% / 13% / 9% | 52% / 23% / 15% / 12% / **10%** / 5% | 11% / 11% / **8%** / 4% / 3% |
| Double Life 第 1 集 | 英文 / 11 | — | — | 0% / 0% / 0% / 0% / 0% |
| Sleeping with the Enemy 1–10 集 | 英文 / 57 | — | — | 7% / 7% / 7% / 7% / 4% |

偏紧口径说明：表里的偏紧误判多半来自 L-cut 和跨镜旁白——一句话跨过切点，被词级时间戳拆到两镜里，单镜字数÷镜长就显得超速。写分镜时整句落在一镜里（或标画外音），不是真问题，所以 cps 维持原值（team-lead 拍板）。

pace 取值依据（≤10% 口径）：
- asl 2-3.5 → 2-4：包住四部实测 2.37 / 2.87 / 3.38 / 3.55；盛夏芬德拉第 1 集 5.41 属甜宠精品子类型，卡片写 `project.asl` 3.5-5.5
- cps 维持 4.5：并组语速中位 3.94、4.84。偏紧误判在盛夏芬德拉是 13%，超过 10%，但要压到 10% 以下需 cps 5，碰到 validate 每镜 5 字/秒的硬上限；而且偏紧里有一部分是转写把一句话的尾巴分给了下一镜（L-cut），写分镜时整句会写在同一镜，所以不改
- slack 1 → 4：两部都 ≤10% 的最紧值（3.5 时盛夏芬德拉 12%）
- hold 4 → 5.5：四部都 ≤10% 的最紧值（5 时盛夏芬德拉 11%）
- hook 维持 5：盛夏芬德拉 4.5s、一品布衣 3.3s 内给出冲突；Double Life 第 6s 给账单特写

来源：
1. 短剧 App 派 2025 年成绩表 — 香港01 — https://global.hk01.com/即时娱乐/60311101/短剧app派2025年成绩表-它凭44亿点击登顶-女主为交房租拍短剧
2. 竖屏美学：方寸之间展现广袤人间（穆裕）— 人民政协网 / 人民日报海外版 2026-01-04 — https://www.rmzxw.com.cn/c/2026-01-04/3844512.shtml
3. 起底野蛮生长的微短剧 — 央视新闻 2024-12-21 — https://www.peopleapp.com/column/30047779058-500006006362
4. 一些微短剧「爽」点多 — 法治日报 2024-03-27 — https://www.rmzxw.com.cn/c/2024-03-27/3515875.shtml
5. How These 1-Minute Movies Are Making Billions（Colin and Samir × Danny Farber）— The Transcript Desk — https://thetranscriptdesk.substack.com/p/how-these-1-minute-movies-are-making
6. Vertical drama Beneath Crimson Sails created with Blackmagic Design — CreativeCOW — https://creativecow.net/vertical-drama-beneath-crimson-sails-created-with-blackmagic-design/
7. 《冒姓琅琊》导演汪帅：竖屏的劣势怎么破？— B站 — https://www.bilibili.com/video/BV1fACsBzEE4
8. 短剧入行竟栽在竖屏？— B站 张暴撕 — https://www.bilibili.com/video/BV1AyA8z1EFu
9. 深度分析爆剧的视听语言之口播式短剧 — B站 忄荒荒 — https://www.bilibili.com/video/BV1bG7g6dEYi
10. ReelShort CEO Joey Jia interview — TIME — https://time.com/7173765/reelshort-crazy-maple-studio-joey-jia-interview/
11. 实测片源 — B站 BV1MiJZzCE9C、BV1tKq3BBEy1 p01、BV1r94y1n7jJ、BV1xw411p7Xo

## 教程 / 操作演示（`tutorial`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 美食作家王刚《厨师长教你：蛋炒饭》 | 全片 0–180s | 28 | 6.40 | 3.64 | 1.23–16.33 | 0 | 炒制段同机位跳剪漏检，1fps 目测校正后约 36 镜、ASL≈5.0 |
| Basics with Babish EP58 法式洋葱汤 | 全片 0–292s | 130 | 2.25 | 1.77 | 0.63–4.71 | 3 | 正片 19–271s：108 镜，ASL 2.34，中位 1.92，中景和手部特写交替 |
| 秋叶AIExcel《身份证的所有玩法》（竖屏） | 全片 0–69s | 19 | 3.61 | 1.50 | 0.77–11.47 | 2 | 前 18.5s 情景剧 11 镜（ASL≈1.7），录屏每个函数一镜 6–19s |
| Excel从零到一《Ctrl+T》 | 全片 0–251s | 3 | 83.8 | — | — | 0 | 整窗录屏一镜到底不放大，6 个技巧约 40s 一个标题行 |
| Blender Guru 甜甜圈 Part1 | 0–120s | 27 | 4.44 | 2.53 | 0.99–16.69 | 1 | 课程第一集，幻灯片加示例；240–540s 另测 73 镜 ASL 4.11 |
| Blender Guru 甜甜圈 Part3 | 0–180s | 4 | 45.0 | — | — | 1 | 9s 赞助后 171s 整窗录屏一镜到底，讲师小窗常驻 |

切镜口径：PySceneDetect AdaptiveDetector 3.0，最小镜长 0.25s。录屏推拉和同机位跳剪会漏检，备注里写了人工复核结果。

语速（B 站 AI 字幕；字数 = 汉字 + 英文单词 + 数字串）：
- 美食作家王刚·蛋炒饭 · 净 5.06 / 毛 3.50 字/秒（628 字，说话 124.2s / 跨度 179.2s；≥1.5s 的停顿 13 处，最长 8.5s）
- 秋叶AIExcel·身份证 · 净 4.63 / 毛 4.47 字/秒（249 字，53.8s / 55.7s；没有 ≥1.5s 的停顿）
- Excel从零到一·Ctrl+T · 净 4.72 / 毛 4.54 字/秒（1139 字，241.3s / 250.9s；没有 ≥1.5s 的停顿）

pace 取值依据：
- asl 2.5–10：Babish 正片 ASL 2.34，原下限 3 会误判快剪实拍；录屏按子步骤拆镜多在 6–8s，上限 10 维持
- cps 4.5：三部说话时净语速 4.63–5.06，录屏全片毛语速约 4.5；4.5 留了一成余量
- slack 1.5：维持。结果出现后停 0.5–1s，加读字幕的时间够用
- hold 8：维持。王刚无旁白段最长 8.5s（装盘），其余停嘴 3–8s
- hook 0：维持。横屏教程不查钩子；竖屏速学的「3 秒内说出痛点」写在卡片正文里

来源：
1. 厨师长教你：「蛋炒饭」的做法 — B 站 / 美食作家王刚 — https://www.bilibili.com/video/BV1gt411o78F
2. Basics with Babish EP58 法式洋葱汤（中字搬运）— B 站 — https://www.bilibili.com/video/BV1UJ411H7Pc
3. 身份证的所有「玩法」— B 站 / 秋叶AIExcel — https://www.bilibili.com/video/BV1n64y1v7Zb
4. Ctrl+T，Excel 中最强大的快捷键 — B 站 / Excel从零到一 — https://www.bilibili.com/video/BV1bS4y1g7bp
5. Blender Guru 甜甜圈入门教程（Blender 开源字幕组）— B 站 — https://www.bilibili.com/video/BV1Mf4y1h79S
6. van der Meij & van der Meij, Eight Guidelines for the Design of Instructional Videos for Software Training, Technical Communication 60(3), 2013 — 特温特大学 — https://ris.utwente.nl/ws/portalfiles/portal/6827789/s4.pdf
7. Guo, Kim, Rubin, How Video Production Affects Student Engagement, ACM L@S 2014 — MIT CSAIL — https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf
8. Mayer 多媒体学习原则汇总 — Dartmouth — https://services.dartmouth.edu/TDClient/1806/Portal/KB/PrintArticle?ID=171655

## 产品宣传片（`product-promo`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| Apple《Titanium》（iPhone 15 Pro） | 0–30.5s | 22（机检 17） | 1.39（机检 1.79） | 1.50 | 0.28–4.37 | 2 | 末段字卡叠化漏检 6 刀；成品第 22.5s 才露出；落版约 8s（26%） |
| 小米 14 Ultra 功能 TVC | 全片 0–104.5s | 73 | 1.43 | 1.12 | 0.52–2.60 | 1 | 几乎每镜一句卖点花字；开售日期卡 1.5s |
| Apple《Introducing iPhone 11 Pro》 | 0–174s | 91 | 1.91 | 1.47 | 0.68–4.03 | 1 | 第 9.8s 完整亮相 3.8s；落版 5.5s |
| 华为 Mate XT《开合间 见非凡》（2025 金投赏金奖） | 全片 0–196s | 87 | 2.25 | 1.96 | 0.63–4.42 | 1 | 产品 15s 入画、93s 完整展开；落版 8.2s |
| DJI《Introducing Osmo Pocket 3》 | 0–136.5s | 58（机检 57） | 2.35（机检 2.39） | 2.04 | 1.15–3.64 | 2 | 第 4.3s 黑底英雄 4.5s；13 个卖点各 2–4 镜；落版约 10s |

语速：未实测（DJI、《Titanium》无旁白；iPhone 11 Pro、Mate XT 的旁白未转写）。

被误判估算（实测镜长，按 review.py 规则，无台词镜看清下限按 1s、不计运镜加成与「停留」，偏保守）：hold 3.5 时 10.8%，hold 4 时 8.3%，hold 4.5 时 4.9%。

pace 取值依据：
- asl 1.5-3.5 → 1.3-3：实测 5 部 1.39–2.35，最慢的 DJI 也没到 2.5
- cps 维持 3.5：没转写到产品片旁白，卡片「每秒 3–4 字」无反例
- slack 维持 1
- hold 维持 4：取 4 时误判 8.3%（≤10%），取 3.5 超到 10.8%；英雄镜 3.8–4.5s 应标「停留」
- hook 3 → 10：卡片第一拍是「悬念开场 4–10 秒」，review.py 查的是第一拍结束时间；实测完整亮相在 4.3s（DJI）、9.8s（iPhone 11 Pro），前 3 秒都已有 1–2 刀。材质起源型 30 秒片（《Titanium》19s）在 `project.hook` 里放宽

来源：
1. First iPhone 15 Pro ad「Titanium」 — 9to5Mac — https://9to5mac.com/2023/09/14/first-iphone-15-pro-ad-titanium/
2. The new iPhone 15 Pro trailer — iMore — https://www.imore.com/apple/the-new-iphone-15-pro-trailer-gives-a-detailed-look-at-its-mars-ready-titanium-finish
3. Apple 的官宣广告片，哪些才是高分佳作？ — 数英 — https://www.digitaling.com/articles/283555.html
4. Apple 宣传片幕后 — 虎嗅 — https://m.huxiu.com/article/269717.html
5. Shot on iPhone — 爱范儿 — https://www.ifanr.com/1406175
7. DJI Osmo Pocket 4 launch commercial BTS — DroneXL — https://dronexl.co/2026/07/08/dji-osmo-pocket-4-launch-commercial-bts-2/
8. DJI Osmo Pocket 4 launch commercial BTS — DroneXL — https://dronexl.co/2026/04/30/dji-osmo-pocket-4-launch-commercial-bts/
9. 华为 Mate XT《开合间 见非凡》项目页 — 数英 — https://www.digitaling.com/projects/316007.html
10. CCLAB × Huawei Mate XT — Stash — https://www.stashmedia.tv/god-is-in-the-details-cclab-gets-intimate-with-huawei-mate-xt-ultimate-design/
11. 华为 Mate30「这不可能，但很 Mate」 — 数英 — https://www.digitaling.com/projects/83110.html
12. Apple 表盘实拍 — 极客公园 — https://www.geekpark.net/news/227586
13. 【深度拉片】产品广告逐分镜脚本设计解析 — B站 布斯D — https://www.bilibili.com/video/BV1dH4y1c75G
14. Product CGI films — XO3D — https://xo3d.co.uk/services/product-cgi-films/
15. 实测原片：https://www.bilibili.com/video/BV168411v7yT ；https://www.bilibili.com/video/BV1Xf421o7w6 ；https://www.bilibili.com/video/BV1YJ411K79R ；https://www.bilibili.com/video/BV13hpseuEs4 ；https://www.bilibili.com/video/BV1pj411i7yB

## 文旅 / 城市宣传片（`city-tourism`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| JNTO《JAPAN - Where tradition meets the future》 | 全片 0–182s | 122 | 1.49（校正后约 1.3） | 1.00 | 0.46–3.17 | 0（实为 1–2） | 无缝转场漏检，按联系表校正；BGM 约 125 BPM，切点和拍网格的相位集中度 R=0.64（随机约 0.23） |
| 《丁真的世界》 | 全片 0–198s（正片 0–172s） | 93（正片 91） | 2.13（正片约 1.97） | 1.60 | 0.84–4.11 | 0 | 分段：开场 1.3 / 清单段 0.96 / 篝火高光 2.5（34s 无旁白）/ 邀约 2.7 |
| 《有一种叫云南的生活》 | 全片 0–228s（正片 0–220s） | 153（正片 152） | 1.49（正片 1.45） | 1.30 | 0.50–2.56 | 2 | 主题是慢生活仍 1.45s；引子 1.05、四字清单段 1.27，最后 30s 回升到 1.78 |
| （对照，非顶尖）上海 4K 延时城市片 | 全片 0–242s | 92 | 2.63（去掉闪烁误检约 3.0） | 2.38 | 0.29–4.83 | 0 | B站「城市宣传片」播放第一；镜长扎堆在 2–3s，几乎没有人，作「千城一面」反例 |

复核（team-lead 要求，对照原始切镜和 whisper 转写）：云南片「我回到这里」实际出现 5 次（27.9、66.4、92.0、129.1、203.0s）；旁白分句中位 6–7 字；句间停顿中位 0.72–0.79s；丁真清单段 5 个词配 9 镜（不是一词一镜）；云南片名在 31.1s 出、停 3.6s；JNTO 连续半拍以内短镜只有一处，8 镜。

切镜口径：PySceneDetect AdaptiveDetector 3.0，最小镜长 0.25s，联系表人工抽查；航拍占比按每 4 秒抽一帧估计（JNTO 约 8%、云南约 22%、丁真约 28%）。卡片镜数由平均镜长换算：卡点型 1.2–2s，旁白型 1.4–2.5s。

语速（mlx-whisper large-v3-turbo 转写，人工核对字幕）：
- 丁真的世界 · 净 3.70 / 毛 2.47 字/秒（277 字，旁白覆盖 44%）
- 有一种叫云南的生活 · 净 3.96 / 毛 2.38 字/秒（506 字，旁白覆盖 58%）
- 旁白落点：句起点中位比上一刀晚 0.98s（丁真）、1.02s（云南）；跨刀的句子 89%、94%；句间停顿中位 0.74s；句尾到下一刀中位 0.66–0.85s，p90 2.05–2.42s
- JNTO 无旁白，旁白覆盖 0

pace 取值依据：
- asl 1.5-6 → 1.2-3（报告原建议 1.2-6，按 team-lead 要求删掉「慢旅行型 3.5–6s」后收窄上限）：三部顶尖片 1.3–2.0s，最慢的段落（篝火、邀约）2.5–2.7s，取 3；本次没有找到平均镜长超过 3.5s 的顶尖官方文旅片。展映长版、慢直播另在 `project.asl` 写
- cps 维持 3：净语速 3.7–4.0，毛语速 2.4–2.5，「句前约 1 秒画面先行 + 一句话」折算约 2.8
- slack 维持 2：句尾到下一刀的 p90 为 2.05–2.42s
- hold 维持 8：正片里不说话的最长镜 5–7.7s（落版 7.3–7.7s）
- hook 维持 0：三部的第一节拍长度 5.5s、12.7s、32s 差别大；「第 0 秒给地方符号」是内容规则，写进卡片节奏基准

来源：
1. JAPAN - Where tradition meets the future（Spikes Asia 词条）— LIONS The Work — https://www.lovethework.com/work-awards/campaigns/japan-where-tradition-meets-the-future-1458625 —（据搜索摘要，页面正文未加载）
2. JAPAN - Where tradition meets the future（Film Craft 词条）— LIONS The Work — https://www.lovethework.com/work-awards/entries/japan-where-tradition-meets-the-future-30886
3. JNTO VR 片报道 — トラベルボイス — https://www.travelvoice.jp/20180117-104095/print
4. 《丁真的世界》项目页 — 数英网 — https://www.digitaling.com/projects/141841.html
5. 丁真与文旅流量 — 36氪 — https://www.36kr.com/p/996012257956358
6. B站搜索「丁真的世界」「Japan Where tradition meets the future」（按播放排序）— Just One API — 播放量
7. Tourism NT + KWP!「Seek Different」获 2021 CIFFT 世界最佳旅游片 — Campaign Brief — https://campaignbrief.com/?p=212767
8. Seek Different — Vimeo — https://vimeo.com/522264491 —（据搜索摘要；视频需要登录，未实测）
9. Welcome to the Icelandverse — LIONS The Work — https://lovethework.com/work-awards/campaigns/welcome-to-the-icelandverse-755149
10. 「2026 戛纳创意节银狮奖，扬州文旅这支宣传片创意真的绝！」— B站 广告圈poor猴 — https://www.bilibili.com/video/BV1CLjR6BEdE —（获奖说法只来自转载标题，未二次核实）
11. 「成都新版旅游宣传片引发争议！」— B站 老余教你拍广告（本地 whisper 转写）— https://www.bilibili.com/video/BV1dV4y1o75g
12. 「#有一种叫云南的生活 宣传片发布」— B站 云南广播电视台 — https://www.bilibili.com/video/BV1jJ4m1e7BS
13. 「上海城市宣传片（我见过最好的）」— B站 — https://www.bilibili.com/video/BV1uW411N729
14. Tourism Films winners qualify for CIFFT — Cannes Corporate Media & TV Awards — https://www.cannescorporate.com/blog/2021/tourism-films-winners-qualify-for-cifft-awards

## 微电影 / 剧情短片（`micro-film`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 《啥是佩奇》（张大鹏） | 全片 0–493s | 112 | 4.40 | 2.32 | 0.61–8.00 | 0 | 首镜 46s 手持长镜头 + 片名；两场电话戏 38.8s / 42.1s 抽帧确认一镜；阈值 1.8 复测 123 镜 / 4.01 |
| 《邻居的窗户》The Neighbors' Window（Marshall Curry，2020 奥斯卡最佳真人短片） | 全片 2–1110s | 151 | 7.34 | 4.96 | 2.30–15.28 | 0 | 开场 90 秒 8 镜（ASL 11.25）；夜景可能少检个别刀 |
| 《邻居的窗户》 | 高潮台阶对话 969–1067s | 14 | 7.00 | 7.20 | 2.25–14.47 | 0 | 过肩正反打，抽帧确认无漏检 |
| 《三分钟》（陈可辛，Apple 2018） | 全片 0–335s | 188 | 1.78 | 1.29 | 0.54–3.46 | 0 | 275–297s 约 30 刀 0.4–0.8s 快切，311s 停留 14.3s |
| 《小城二月》（邱阳，2017 戛纳短片金棕榈） | 全片 0–880s | 20 | 44.0 | 27.22 | 0.80–125.9 | 0 | 4:3 固定长镜；派出所对话 127s 一镜；含 3 个闪烁碎镜 |

切镜口径同上表，夜戏和手持段用 1fps 联系表抽查。

语速（mlx-whisper，间隔 ≤0.8s 并组）：
- 啥是佩奇 · 加权 4.16 / 中位 4.01 字/秒（842 字 / 202.4s；乡音和广播段有错字）
- 三分钟 · 加权 3.60 / 中位 3.91 字/秒（429 字 / 119.2s）；母亲画外音净语速 4.89
- 小城二月：常州方言，未测

逐镜台词负载（cps 取 4）：余量中位 0.59 / 0.10、p75 2.06 / 1.22；无台词镜中位 2.20 / 1.36、p90 5.02 / 2.94（啥是佩奇 / 三分钟）。

机检误判率（按 review.py 判定线模拟：顶尖范本的镜头被判偏紧/拖沓的比例；取值口径 = 每部范本误判 ≤10% 的最紧值）。
台词按 mlx-whisper 词级时间戳分到各镜；台词镜 拖沓 = 镜长 > max(字数÷cps, 1.0) + slack；无台词镜（镜内没有任何词）拖沓 = 镜长 > max(1.0 + slack, hold)，按固定机位算（实际有运镜会再多一份 slack，所以表里偏严）；外语片只用转写区分有无台词，不参与 slack。

| 范本 | 台词镜 / 无台词镜 | 偏紧 @cps 3.5 / 4 / 4.5 | 拖沓 @slack 2 / 3 / 4 / 5 / 6 | 超限 @hold 6 / 8 / 10 / 12 / 15（slack=5） |
|---|---|---|---|---|
| 啥是佩奇 | 68 / 44 | 31% / 21% / 13% | 21% / 15% / 12% / **10%** / 7% | 2% / 0% / 0% / 0% / 0% |
| 三分钟 | 93 / 89 | 32% / 26% / 17% | 11% / 3% / 1% / 1% / 1% | 1% / 1% / 1% / 1% / 0% |
| 邻居的窗户 | 英文 / 47 | — | — | 30% / 17% / 13% / **9%** / 6% |
| 小城二月（作者向子类型） | 14 / 6 | 7% / 7% / 7% | 86%（任何取值） | 83% / 83% / 83% / 67% / 67% |

偏紧口径说明：表里的偏紧误判多半来自 L-cut 和跨镜旁白——一句话跨过切点，被词级时间戳拆到两镜里，单镜字数÷镜长就显得超速。写分镜时整句落在一镜里（或标画外音），不是真问题，所以 cps 维持原值（team-lead 拍板）。

pace 取值依据（≤10% 口径）：
- asl 3-6 → 3-8：包住叙事向实测 4.40、7.34；三分钟 1.78、小城二月 44 是子类型，卡片写 `project.asl` 1.5-3 和 10-60
- cps 维持 4：并组语速中位 4.01、3.91。偏紧误判 21–26%，主要是画外音和对白跨过快切（三分钟的旁白压在 1–2s 一刀的人潮快切上），写分镜时这类句子要拆到各镜或写成画外音，所以不改 cps；要压到 10% 以下需 cps 5 以上，超过 validate 硬上限
- slack 2 → 5：啥是佩奇 ≤10% 的最紧值（4 时 12%），主要来自 38–50s 带台词的长镜头
- hold 8 → 12：邻居的窗户无台词镜 ≤10% 的最紧值（10 时 13%）
- 小城二月任何取值都会被大量判拖沓（127s 一镜），卡片要求这类整场一镜标「停留」写 `pace_note`
- hook 维持 0

来源：
1. 金狮奖特别期 Talk Share × 张大鹏导演 56 问 — 数英网 2019-01-28 — https://www.digitaling.com/articles/101205.html
2. Marshall Curry — Wikipedia — https://en.wikipedia.org/wiki/Marshall_Curry
3. 独家对话短片金棕榈导演邱阳 — B站 1905 电影网 — https://www.bilibili.com/video/BV1Ui4y1T7PR
4. 《小城二月》拉片 — B站 卷头发的明哥 — https://www.bilibili.com/video/BV19G4y1y7aF
5. Joel & Ethan Coen – Shot | Reverse Shot — YouTube Every Frame a Painting — https://www.youtube.com/watch?v=5UE3jz_O_EM
6. The Social Network: How Editing Turned a Conversation into a Masterpiece — YouTube Cutting Concepts — https://www.youtube.com/watch?v=wX4bKWhtK8M
7. Shot Reverse Shot: How to Shoot Reaction Shots — YouTube StudioBinder — https://www.youtube.com/watch?v=EBykqNDKbKY
8. 实测片源 — B站 BV1Pt411a755、BV1Wa411F7GU、BV1pW411H7sR、BV1e12rBdEGc

## 动画短片（`animation`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 《鹬》Piper（Pixar，第 89 届奥斯卡最佳动画短片） | 全片 12–322s | 47 | 6.60 | 4.75 | 1.70–15.52 | 0 | 19–20s 长镜抽帧确认为固定全景；无对白 |
| 《包宝宝》Bao（石之予，第 91 届奥斯卡最佳动画短片） | 全片 6–425s | 106 | 3.95 | 3.23 | 1.17–7.41 | 1 | 崩溃段 1–1.5s 连切后接 17s；结尾三镜 11–13s |
| 《小妖怪的夏天》（於水，中国奇谭第 1 集） | 正片 94–1225s | 245 | 4.62 | 3.56 | 0.50–10.13 | 0 | 打斗闪白约 15 个碎镜属多检，扣除后约 230 镜 / 4.9s；开场 18s 大远景，结尾 37s 大远景 |
| 《小妖怪的夏天》 | 母子对话戏 755–845s | 14 | 6.43 | 5.00 | 0.46–16.24 | 1 | 18s 双人侧面中景做骨架 |
| 《三个和尚》（阿达，1982 柏林银熊） | 正片 40–1120s | 228 | 4.74 | 3.06 | 0.88–9.72 | 0 | 白底叠化会漏检，ASL 可能偏高约一成；23s 留白长镜开场 |

语速（mlx-whisper，间隔 ≤0.8s 并组）：
- 小妖怪的夏天 · 加权 4.00 / 中位 4.19 字/秒（2125 字 / 531.1s）；母子戏 3.22（271 字 / 84.1s）
- 鹬、包宝宝、三个和尚：无对白

逐镜台词负载（小妖怪，cps 取 4）：余量中位 1.17、p75 2.87、p90 4.47；无台词镜中位 3.16、p90 6.78。全片无对白的范本里超过 8s 的镜头：包宝宝 8%，三个和尚约 18%（含漏检），鹬 36%。

机检误判率（按 review.py 判定线模拟：顶尖范本的镜头被判偏紧/拖沓的比例；取值口径 = 每部范本误判 ≤10% 的最紧值）。
台词按 mlx-whisper 词级时间戳分到各镜；台词镜 拖沓 = 镜长 > max(字数÷cps, 1.0) + slack；无台词镜（镜内没有任何词）拖沓 = 镜长 > max(1.0 + slack, hold)，按固定机位算（实际有运镜会再多一份 slack，所以表里偏严）；外语片只用转写区分有无台词，不参与 slack。

| 范本 | 台词镜 / 无台词镜 | 偏紧 @cps 3.5 / 4 / 4.5 | 拖沓 @slack 2 / 3 / 4 / 4.5 / 5 | 超限 @hold 6 / 8 / 10 / 12 / 15（slack=4.5） |
|---|---|---|---|---|
| 小妖怪的夏天 | 125 / 120 | 31% / 18% / 10% | 34% / 23% / 12% / **10%** / 9% | 10% / 5% / 2% / 1% / 0% |
| 包宝宝（无对白） | 0 / 106 | — | — | 16% / 8% / 5% / 4% / 2% |
| 三个和尚（无对白，叠化漏检偏严） | 0 / 228 | — | — | 23% / 17% / **10%** / 8% / 5% |
| 鹬（无对白喜剧） | 0 / 47 | — | — | 43% / 34% / 19% / 13% / **9%** |

偏紧口径说明：表里的偏紧误判多半来自 L-cut 和跨镜旁白——一句话跨过切点，被词级时间戳拆到两镜里，单镜字数÷镜长就显得超速。写分镜时整句落在一镜里（或标画外音），不是真问题，所以 cps 维持原值（team-lead 拍板）。

pace 取值依据（≤10% 口径）：
- asl 3-5 → 3-7：包住四部实测 3.95 / 4.62 / 4.74 / 6.60
- cps 维持 4：并组语速中位 4.19、加权 4.00；偏紧误判 18%，原因同上（跨镜长句被词级时间戳拆开），压到 10% 需 cps 4.5，暂不改，等有第二部有对白的范本再定
- slack 1.5 → 4.5：小妖怪 ≤10% 的最紧值（4 时 12%）；只有一部有对白的范本
- hold 6 → 10：不含鹬的三部都 ≤10% 的最紧值（三个和尚 10%、包宝宝 5%、小妖怪 2%）。鹬按无对白喜剧子类型处理：取 10 时 19%、12 时 13%、15 时 9%，卡片要求这类长镜标「停留」并写 `pace_note`（team-lead 拍板）
- hook 维持 0

来源：
1. Bao (film) — Wikipedia — https://en.wikipedia.org/wiki/Bao_(film)
2. Bringing a dumpling to life: Q&A with Domee Shi — The China Project — https://thechinaproject.com/2018/07/17/qa-with-domee-shi-pixar-director-of-bao/
3. In Pixar's First Female-Directed Short… — NPR — https://www.npr.org/2018/06/15/619253624/in-pixars-first-female-directed-short-a-dumpling-child-fills-an-empty-nest
4. Piper (film) — Wikipedia — https://en.wikipedia.org/wiki/Piper_(film)
5. Watch the first footage from Piper — /Film — https://www.slashfilm.com/pixar-short-film-piper/
6. Pixar's Piper review — Film Inquiry — https://www.filminquiry.com/pixars-piper-short-review/
7. リミテッド・アニメーション — 日文 Wikipedia — https://ja.wikipedia.org/wiki/リミテッド・アニメーション
8. Spider-Man: Into the Spider-Verse — Wikipedia — https://en.wikipedia.org/wiki/Spider-Man:_Into_the_Spider-Verse
9. Storyboard — Wikipedia — https://en.wikipedia.org/wiki/Storyboard
10. 豆瓣 9.6，2 集封神的《中国奇谭》好看在哪 — 爱范儿 — https://www.ifanr.com/1530422
11. Three Monks — Wikipedia — https://en.wikipedia.org/wiki/Three_Monks
12. 细读动画经典《三个和尚》— B站 正解电影 — https://www.bilibili.com/video/BV1Tr4y1a7bz
13. 实测片源 — B站 BV1BZ4y1H79N、BV197411V7bR、ep706666、BV1Ys411u7Q5

## 知识科普 / 解说（`explainer`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| Kurzgesagt《狂犬病毒》 | 0–90s | 10 | 9.0 | 5.1 | 0.45–36.38 | 0 | 转场靠推拉形变，硬切偏少；目测约 28 个构图（≈3.2s），和官方「约 200 张画面」一致 |
| 3Blue1Brown《形象展示傅里叶变换》 | 0–120s | 4 | 30.0 | 17.7 | — | 0 | 单画布逐句累加；2s 抽帧目测画面状态约 39 次（≈3.1s） |
| Johnny Harris《我为何永远不用公制》 | 0–120s | 62 | 1.94 | 1.10 | 0.33–4.96 | 6 | 冷开场段，逐行打字有 0.2–0.5s 闪切；第 97s 上片名 |
| 何同学《有多快？5G 在日常使用中的真实体验》 | 0–120s | 41 | 2.93 | 2.68 | 0.20–6.36 | 0 | 含 8 个 0.2s 测速闪切，剔除后 33 镜 ASL 3.6；出镜约 20% |
| 小Lin说《一口气了解国债》 | 0–120s | 41 | 2.93 | 2.27 | 0.53–6.92 | 1 | 主讲人约 40%，其余是图表卡和素材 |

切镜口径：PySceneDetect AdaptiveDetector 3.0，最小镜长 0.25s。动画型的推拉、形变转场会漏检，改用抽帧目测数画面状态。卡片「默认规格」里的镜数由实测平均镜长换算（60 秒 ÷ 平均镜长）。

语速（中文用 B 站 AI 字幕，英文用本地 whisper 词级时间戳取前 300s）：
- 何同学·5G · 净 5.15 / 毛 5.01 字/秒（2204 字；旁白覆盖 97%，≥1.5s 的停顿约 110s 一次）
- 小Lin说·国债 · 全片净 6.21 / 毛 5.67 字/秒；前 180s 净 5.85 / 毛 5.28（旁白覆盖 91%，停顿约 39s 一次）
- 混知·退税（漫画解说）· 净 4.95 / 毛 4.87 字/秒（旁白覆盖 98%，停顿约 174s 一次）
- Kurzgesagt（英文原声）· 164 词/分（前 300s 只有 1 处 ≥1.5s 的停顿：第 47–56s logo 音乐段）
- 3Blue1Brown（英文）· 182 词/分（前 300s 有 4 处停顿，都在演示时，每处 2–3s）
- Johnny Harris 中配 · 毛 4.42 字/秒（配音受原片时长约束，只作参考）
- 头部出镜讲解说话时净语速可到 5.5–6 字/秒（小Lin、何同学），只作参考；卡片按 validate.py 红线要求每镜不超过 5 字/秒

pace 取值依据：
- asl 2.5–6：出镜型硬切 ASL 2.9–3.6（Johnny Harris 冷开场 1.9），动画型约 3s 一个状态；没有范本超过 4，上限留到 6 给单画布累加
- cps 4.5：头部净语速 4.95–6.21、毛语速 4.87–5.67；4.5 给普通配音留了余量
- slack 1.5：维持。问句后停 0.5–1s，揭晓前后各留半拍，够用
- hold 6：维持。3B1B 演示停顿 2–3s；片名音乐段 9s 在卡片里要求标「停留」
- hook 15：五部范本都在 15s 内抛出问题或点题（实测 8–11s）

来源：
1. Kurzgesagt《狂犬病毒》官方中字 — B 站 — https://www.bilibili.com/video/BV1f84y1v7qo
2. How to Make a Kurzgesagt Video in 1200 Hours — YouTube / Kurzgesagt — https://www.youtube.com/watch?v=uFk0mgljtns
3. Our video process — kurzgesagt.org — https://kurzgesagt.org/youtube/
4. 3Blue1Brown《形象展示傅里叶变换》官方双语 — B 站 — https://www.bilibili.com/video/BV1pW411J7s8
5. Johnny Harris《我为何永远不用公制》中配 — B 站 — https://www.bilibili.com/video/BV1BYSxB8EiA
6. Why every Johnny Harris video goes viral — YouTube / David Mora — https://www.youtube.com/watch?v=dIKsEhX-vyU
7. 何同学《有多快？5G 在日常使用中的真实体验》— B 站 — https://www.bilibili.com/video/BV1f4411M7QC
8. 小Lin说《一口气了解国债》— B 站 — https://www.bilibili.com/video/BV1LW4y1Q75v
9. 混知《怎么操作，退税更准确？》— B 站 — https://www.bilibili.com/video/BV1jCRXYdES8
10. Guo, Kim, Rubin, How Video Production Affects Student Engagement, ACM L@S 2014 — MIT CSAIL — https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf
11. Mayer 多媒体学习原则汇总 — Dartmouth — https://services.dartmouth.edu/TDClient/1806/Portal/KB/PrintArticle?ID=171655

## MG 动画 / 数据可视化（`motion-graphics`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| BUCK《Apeel – Manifesto》 | 全片 0–75s | 10 | 7.54 | 4.74 | 1.00–27.36 | 1 | 形变转场漏检；2s 抽帧目测约 18 个版式（≈4.2s） |
| 混知《怎么操作，退税更准确？》 | 0–120s | 17 | 7.06 | 6.23 | 0.33–20.69 | 1 | 6 个 0.33s 是口号快闪；章节卡弹入未检出；目测约 25 个版式（≈4.8s） |
| 支付宝×央视《年轻人理财应该注意什么？》 | 全片 0–140s | 6 | 23.27 | 22.02 | — | 0 | 整屏翻色和形变全部漏检；目测约 30 个版式（≈4.7s）；B 站播放仅 4010，作国内常规水准对照 |

切镜口径：PySceneDetect AdaptiveDetector 3.0。MG 的硬切 ASL 被形变转场拉长，不能直接用；版式数用 2s 抽帧目测。

动静节奏（10fps、64×36 灰度，相邻帧平均差 > 2.0 记为「动」）：

| 范本 | 动的占比 | 每分钟动作段 | 动作段中位 | 静止段中位 | 静止段 p90 |
|---|---|---|---|---|---|
| BUCK·Apeel | 40% | 20.7 | 0.75s | 0.9s | 2.56s |
| 支付宝×央视 | 42% | 32.3 | 0.6s | 1.1s | 2.6s |
| 混知·退税 0–120s | 24% | 22.5 | 0.4s | 2.55s | 6.27s |
| Kurzgesagt·狂犬病毒 0–90s | 60% | 17.4 | 0.9s | 1.0s | 3.5s |

阈值降到 1.0 时，Apeel、支付宝动的占比都是 57%，每分钟动作段 23.9 和 30.5。镜头缓慢漂移、循环小动画也会算成「动」。

语速：
- 混知·退税 · 净 4.95 / 毛 4.87 字/秒（B 站 AI 字幕，1695 字，旁白覆盖 98%）
- 支付宝×央视 · 4.05 字/秒（无字幕，本地 whisper 转写，562 字 / 138.6s）

pace 取值依据：
- asl 3–6：维持。按版式场景算，实测 4.2–4.8s
- cps 4：维持。品牌型实测 4.05；漫画解说型 4.87，卡片正文写了可调高
- slack 1：维持。流动型普通状态只停约 1s
- hold 5：维持。流动型静止段 p90 2.2–3.5s，落版 logo 约 2s
- hook 5：维持。60 秒以内按 5s 查（Apeel 2.6s 出主物件）；2 分钟以上的长 MG 实测 8.6–8.8s 才说完问句，卡片正文允许长版放宽到 9s

来源：
1. BUCK《Apeel – Manifesto》（搬运）— B 站 — https://www.bilibili.com/video/BV13T4y1279i
2. Buck (design company) — Wikipedia — https://en.wikipedia.org/wiki/Buck_(design_company)
3. 混知《怎么操作，退税更准确？》— B 站 — https://www.bilibili.com/video/BV1jCRXYdES8
4. 支付宝 × 央视《年轻人理财应该注意什么？》（成都壹元文化）— B 站 — https://www.bilibili.com/video/BV1PY41187dT
5. Kurzgesagt《狂犬病毒》— B 站 — https://www.bilibili.com/video/BV1f84y1v7qo
6. How to Make a Kurzgesagt Video in 1200 Hours — YouTube / Kurzgesagt — https://www.youtube.com/watch?v=uFk0mgljtns
7. Six Essential Motion Design Transitions — School of Motion — https://schoolofmotion.com/blog/six-essential-motion-design-transitions-tutorial
8. Match Cuts — School of Motion — https://www.schoolofmotion.com/blog/match-cuts
9. After Effects 动画教程及工作流程 ft. Buck NY Johan Eriksson（Ben Marriott 官方中字）— B 站 — https://www.bilibili.com/video/BV1wJ41127ZA
10. Motion overview — IBM Carbon Design System — https://carbondesignsystem.com/elements/motion/overview/
11. If every word moves, none of the words feel important — Reddit r/MotionDesign — https://www.reddit.com/r/MotionDesign/comments/1wciwpy/
12. 如何制作一条回形针风格的爆款视频 — B 站 — https://www.bilibili.com/video/BV1T7411p7SY

## 达人口播 / 带货种草（`creator-ad`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 老爸评测《20 款面霜 60 人实测》（抖音，2365 万粉） | 全片 0–46.2s | 33 | 1.40 | 1.08 | 0.16–2.30 | 2 | 阈值 3.0 把产品轮播漏成 36s 长镜，改用阈值 1.5 |
| 骆王宇《这些洁面你不爱，小骆含泪把号卖》（抖音，1491 万粉，147 万赞） | 开场 0–90s | 42 | 2.14 | 1.70 | 0.74–5.42 | 2 | A-roll 跳切占八成，每镜花字 + 贴纸 |
| 骆王宇《精致不是梦，人人都能用》 | 开场 0–90s | 39 | 2.31 | 1.87 | 0.70–4.83 | 0 | 首镜 3.37s，镜内贴纸、花字变化 |
| 老爸评测《贵的行李箱就一定好吗》（21.5 万赞） | 全片 0–58.2s | 25 | 2.33 | 2.13 | 0.84–4.04 | 0 | 首镜 3.8s；第 8.8s 留存钩；5 个维度各一个手上测试 |

赞助段（YouTube 字幕时间轴，不测镜长）：MrBeast（Qtl8lJwbd4g）在 39% 处，约 85s，开始后 8.5s 点名赞助方；LTT（LGA4ZFr-hfo）14% 处 30s 预告 + 片尾约 80s 正式段，CTA 约 10s；B站后期风水学PP导在 83% 处，46s，话题 segue。

语速（本地 mlx_whisper 转写，剔除幻觉段；毛 = 字数 ÷ 去掉 >2s 静默的说话时段）：
- 骆王宇① · 毛 6.30 / 净 7.2 字/秒（1655 字 / 262.7s）
- 骆王宇② · 毛 6.47 / 净 7.5 字/秒（1299 字 / 200.6s）
- 老爸评测《行李箱》 · 毛 5.89 字/秒（314 字 / 53.3s）
- 老爸评测《面霜》 · 毛 5.45 字/秒（86 字 / 15.8s，口播只覆盖 34%）
- B站恰饭段（后期风水学PP导 489–536s） · 毛 5.98 字/秒（276 字 / 46.1s）
- 英文：MrBeast 开场 3.23 词/秒、赞助卖点段 3.79 词/秒；LTT 开场 2.95 词/秒

被误判估算（镜长 + 转写时间轴按时长分摊到镜，看清下限按 1s）：cps 5 时偏紧 70.5%（头部本身就说到 6 字/秒以上，属预期），拖沓 2.9%；cps 4.5 时偏紧 75.5%。slack 0.8 → 1、hold 3 → 2.5 拖沓率都在 2.2–2.9%。

pace 取值依据：
- asl 1.5-4 → 1.3-3：实测 1.40–2.33，上限留给慢节奏知识口播
- cps 4.5 → 5：头部实测 5.45–6.47，但 validate.py 对每镜「台词 + 旁白 ÷ 镜长 > 5 字/秒」硬性报错，分镜按 5 排、真人实拍时自然会更快
- slack 维持 0.8：头部几乎不停顿（骆王宇全片只有 1 处 >2s 间隙），拖沓误判 2.9%
- hold 维持 3：无口播镜只有产品轮播（约 1s）和总结卡（约 2.5s），误判在 ≤10% 内
- hook 维持 3：第一句 1.9–7s 说完，但核心词都在前 3 秒

来源：
1. YouTube & Google ABCD Reference Guide — Google — https://services.google.com/fh/files/misc/youtube_google_abcd_reference_guide_en.pdf
2. YouTube Shorts ABCDs Summary — Google — https://services.google.com/fh/files/misc/formarketingshortsabcdsonesheeters.pdf
3. Creating YouTube Ads That Break Through in a Skippable World — Think with Google — https://business.google.com/aunz/think/marketing-strategies/creating-youtube-ads-that-break-through-in-a-skippable-world/
4. How To Succeed At MrBeast Production — 泄露手册 — https://prog.sijanec.eu/dir/How-To-Succeed-At-MrBeast-Production.pdf
5. Vericast TikTok Best Practices — Vericast — https://vericast.com/wp-content/uploads/2022/09/Vericast-TikTok-Best-Practices-Vertical-CS0761-2022-09-8.5x11.pdf
6. Best Practices To Increase TikTok Video Ad Conversions — WeRSM — https://wersm.com/?p=107933
7. TikTok × Vidmob creative report — Adweek — https://www.adweek.com/adweek-wire/report-reveals-key-visual-and-creative-ad-strategies-for-hooking-tiktok-audiences/
8. Unlock the potential of Reels — Adobe Blog — https://blog.adobe.com/en/publish/2024/11/04/unlock-potential-reels-best-practices-for-creative-success-using-adobe-creative-cloud
9. Disclosures 101 for Social Media Influencers — 美国 FTC 官网（原链接已失效，可在 ftc.gov 按标题搜索）
10. 互联网广告管理办法 — 维基文库 — https://zh.wikisource.org/wiki/互联网广告管理办法
11. An Unfiltered Conversation with Linus Tech Tips — The Transcript Desk — https://thetranscriptdesk.substack.com/p/an-unfiltered-conversation-with-linus
12. What makes a good YouTube sponsorship integration — Creators Agency — https://creatorsagency.co/blog/what-makes-a-good-youtube-sponsorship-integration
13. Intelligibility and preferred rate of Chinese speaking — 香港城市大学 — https://scholars.cityu.edu.hk/en/publications/intelligibility-and-preferred-rate-of-chinese-speaking/
14. Writing spots — American Public Media — https://www.americanpublicmedia.org/writespots
15. 阳狮集团联合巨量引擎营销科学探索兴趣电商 — 数英 — https://www.digitaling.com/articles/784034.html
16. 怎么剪辑出灵动有节奏感的口播视频 — B站 厦九九 — https://www.bilibili.com/video/BV1VYHCedEwi
17. 实测原片：https://www.douyin.com/video/7158419606850276639 ；https://www.douyin.com/video/7140581740334058759 ；https://www.douyin.com/video/7148764672597003558 ；https://www.douyin.com/video/7240276649059667261 ；https://www.youtube.com/watch?v=Qtl8lJwbd4g ；https://www.youtube.com/watch?v=LGA4ZFr-hfo ；https://www.bilibili.com/video/BV1zS421A78V

## 纪录片 / 人物纪实（`documentary`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 《地球脉动 II》第 1 集 · 鬣蜥逃蛇段 | 全段 0–342s | 81 | 4.23 | 3.08 | 1.46–8.96 | 0 | 分段：铺垫 5.5 / 首轮追逐 2.7 / 名场面以 5–11s 长跟拍为主；公开拆解该追逐为 28 镜 2:04（ASL 4.4），本次在甩摇处约漏检 1 刀 |
| 《我们的星球》第 1 集 One Planet | 开场 4.9–330s | 38 | 8.56 | 6.95 | 2.12–15.47 | 0 | 地球升起长镜 42s，旁白约第 46s 才进；点题蒙太奇有个别叠化，可能漏检 1–3 刀 |
| 《徒手攀岩》（Free Solo） | 片名前序幕 30.5–336s | 51 | 5.99 | 4.68 | 1.63–13.98 | 0 | 前 90s 只有 6 镜（ASL 12.4），第一句人声在序幕第 57s；档案段 ASL 4.6；只能量 6 分钟试看 |
| 《我在故宫修文物》第 1 集 | 片头后正片 39.6–360s | 113 | 2.84 | 2.48 | 1.44–5.10 | 0 | 片头 MG 0–39.6s（57 镜 ASL 0.79）没算进来；2fps 抽查切点真实；只能量 6 分钟试看 |
| 《人生一串》第 1 集 | 第一个故事 153.4–243.4s | 36 | 2.50 | 1.96 | 1.03–4.82 | 0 | 冷开场 21–91s ASL 1.65，片头 91–153s ASL 0.80，第一个故事 153–420s 共 106 镜 ASL 2.51 |

切镜口径：PySceneDetect AdaptiveDetector 3.0，最小镜长 0.25s，每部都用 1–2fps 联系表人工抽查。卡片「默认规格」的每分钟镜数由平均镜长换算：解说型 2.5–3.5s → 17–24 镜，观察型 4–9s → 7–14 镜。

语速（mlx-whisper large-v3-turbo 转写，人工区分旁白和同期声；毛语速 = 字数 ÷ 旁白段总跨度，含句间停顿）：
- 我在故宫修文物 · 旁白 · 净 3.91 / 毛 3.59 字/秒（514 字 / 143.2s；旁白覆盖正片 45%）
- 我在故宫修文物 · 同期声 · 净 4.71 字/秒（382 字 / 81.0s）
- 人生一串 · 旁白 · 净 3.99 / 毛 3.22 字/秒（793 字 / 246.5s；旁白覆盖正片 72%）
- 旁白落点（同样两部）：分句起点中位在上一刀之后 1.01s（故宫）、1.16s（人生一串）；跨刀的分句占 72%、62%；有旁白的镜头念完后剩余时间 p90 1.1–1.3s
- 旁白覆盖：Free Solo 序幕 0（只有档案原声和同期声）；BBC 鬣蜥段约 15%，名场面追逐约 90s 无旁白（字幕带联系表抽查）

pace 取值依据：
- asl 5-12 → 2.5-9：国内两部头部作品正片 2.50、2.84，国外观察型 4.23–8.56；解说型项目在 `project.asl` 写 2.5-3.5，观察型写 4-9
- cps 4 → 3.5：旁白毛语速实测 3.22、3.59，原值 4 只是净语速
- slack 维持 4（报告原建议 3，未采纳）：有旁白的镜头剩余 p90 只有 1.1–1.3s，但观察型同期声镜头（话说完后的反应、沉默）没有实测；改 3 会让 samples/12-documentary 第 8 镜（13 字对白给 7s）判拖沓，缺证据，不收紧
- hold 维持 15：三部国外作品 p90 为 9.0–15.5s；超过 15s 的镜头在 Free Solo 和我们的星球各 4 个，全是开场、揭示用的尺度长镜，卡片要求标「停留」写 `pace_note`
- hook 维持 0：观察型开场的第一句人声在 40–60s，按秒查钩子不适用

来源：
1. All about editing: Blue Planet II's editor on how he put together some of the show's iconic scenes — RTS — https://rts.org.uk/article/all-about-editing-blue-planet-iis-editor-how-he-put-together-some-shows-iconic-scenes
2. Planet Earth II: How to Edit Animals — YouTube / Our Changing Climate（字幕经 Just One API）— https://www.youtube.com/watch?v=cCTi0J6AWTE
3. How the BBC makes Planet Earth look like a Hollywood movie — YouTube / Vox（字幕经 Just One API）— https://www.youtube.com/watch?v=qAOKOJhzYXk
4. Planet Earth II — Wikipedia — https://en.wikipedia.org/wiki/Planet_Earth_II
5. Leapin' lizards! 'Real nature' Iguana vs Snakes doco… — The New Daily — https://www.thenewdaily.com.au/entertainment/tv/2017/06/14/truth-documentary-iguana-snakes-chase-nature —（据搜索摘要，未读原文；拼接一事另见来源 2 的字幕）
6. A picture is more powerful than a spoken word… — Q Radio（转述 BBC Wildlife Magazine）— https://www.qradio.com/archive/a-picture-is-more-powerful-than-a-spoken-word-sir-david-attenborough-doesnt-want-to-talk-too-much-on-his-wildlife-shows
7. Tracing the story of life on earth — Christian Science Monitor 1981 — https://www.csmonitor.com/1981/1109/110933.html —（据搜索摘要，未读原文）
8. Our Planet — Wikipedia — https://en.wikipedia.org/wiki/Our_Planet
9. NYFA Screens Oscar-Winning 'Free Solo' with Editor Bob Eisenhardt — NYFA — https://www.nyfa.edu/film-school-blog/free-solo-screening/
10. 91st Oscars Backstage Interview Transcript: Documentary Feature — oscars.org — https://www.oscars.org/press/91st-oscars-backstage-interview-transcript-documentary-feature —（据搜索摘要，未读原文）
11. A Bite of China — Wikipedia — https://en.wikipedia.org/wiki/A_Bite_of_China
12. 舌尖上的中国 第一季 完整文案 — 数英网 — https://www.digitaling.com/articles/11234.html
13. 相信我——这是《舌尖》系列中最深刻的段落 — B站 / 周彤美食工坊（本地 whisper 转写）— https://www.bilibili.com/video/BV1Cf4y1q7Ej
14. 【拉片《舌尖二》】扣三丝 — B站 / 周彤美食工坊（本地 whisper 转写）— https://www.bilibili.com/video/BV13q4y1D7yM
15. 豆瓣 8.9 分，这部真正的中国版深夜食堂… — 爱范儿 — https://www.ifanr.com/1070383
16. 人生一串、我在故宫修文物、徒手攀岩 PGC 季度信息（评分、播放量、集号）— B站公开接口（匿名，未登录）— season_id 24439 / 20792 / 48252
17. 叶君与《我在故宫修文物》 — 新京报 — https://www.bjnews.com.cn/detail/1777248338168720.html
18. 《我在故宫修文物》导演叶君病逝 他让年轻人爱上纪录片 — ourchinastory — https://www.ourchinastory.com/cn/16785 —（据搜索摘要，未读原文）
19. 纪录片创作中的最大痛点：如何选题？如何结构故事？ — B站 / 一点开讲（本地 whisper 转写）— https://www.bilibili.com/video/BV1Af4y197bW
20. 拉片｜图片素材的运用 空镜的串接 人物采访的使用 — B站 / 嚯嚯嚯12345（本地 whisper 转写）— https://www.bilibili.com/video/BV1oZ4y147QJ
21. 分析这部纪录片的剪辑思路，情感维度（美国工厂）— B站 / 弄影老孙（本地 whisper 转写）— https://www.bilibili.com/video/BV1nr4y1M7fi
22. 实测素材 — B站 — https://www.bilibili.com/video/BV1QJ411C7p9 、https://www.bilibili.com/bangumi/play/ep120576 、https://www.bilibili.com/bangumi/play/ep216794 、https://www.bilibili.com/bangumi/play/ep831099 、https://www.bilibili.com/video/BV1oJ41137oE

## 音乐 MV（`mv`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| Childish Gambino《This Is America》（Hiro Murai） | 全片 0–245s | 7 | 34.97 | 8.92 | —（不足 10 镜） | 0 | 4.6–182s 是一个 178s 连续长镜，抽帧确认无明切；只代表一镜到底型 |
| Kendrick Lamar《HUMBLE.》（Dave Meyers & the little homies） | 全片 0–183.5s | 104 | 1.76 | 1.00 | 0.29–3.69 | 0 | 首镜 14.4s 官方署名长镜；主歌一 ASL 0.99，副歌一 3.93（含 10.9s 推镜）；闪切每次 2–3 下、每下 0.25–0.33s，经抽帧确认 |
| 周杰伦《告白气球》 | 全片 0–215.7s | 79 | 2.73 | 2.29 | 1.12–4.25 | 0 | 首镜 11.9s 航拍+歌名；主歌段 ASL 2.45、副歌段 2.22；尾镜 13.7s 全片最长 |
| BTS《Dynamite》 | 23–217s（歌曲正文） | 139 | 1.40 | 0.92 | 0.50–2.88 | 1 | 裁掉 8s 厂牌片头和带非官方台标的开场群像；中段有 4.3s、4.8s、8.7s 三个长镜，167–182s 的 15s 长镜是真实运镜 |

切镜口径：PySceneDetect AdaptiveDetector 3.0，最小镜长 0.25s；B 站搬运版，抽帧人工核对过长镜和闪切。导演署名：《告白气球》《Dynamite》未能从一手来源核实，卡片里只写歌手。

卡拍实测（librosa 0.11 拍点 / 起音检测；音轨单独下载，切点取自上表；±80ms 窗口；另做 ±0.3s 整体偏移扫描，三片均无隐藏锁拍）：
- 告白气球 · 估速 89 BPM · 拍点命中 27.3%（随机期望 23.8%）· 4 拍组相位 Rayleigh p≈0.007（小节层面弱聚集）· 强起音命中 9%（随机平移 11%）
- Dynamite · 估速 112 BPM（官方 114）· 拍点命中 36.0%（随机 30.0%）· Rayleigh 单拍 p≈0.11 · 强起音命中 16%（随机平移 18%）
- HUMBLE. · 估速 152 BPM · 拍点命中 39.2%（随机 40.5%）· Rayleigh 单拍 p≈0.81 · 强起音命中 18%（随机平移 16%）

语速：无（MV 歌词不进 `vo`，本次没有对白样本）。

pace 取值依据：
- asl 0.8–4：三支常规 MV 全片 ASL 1.40–2.73（说唱主歌密段 0.99，副歌定格段 3.93）；原来的 0.5–6 太宽查不出问题。一镜到底（This Is America 35s）、Live Session 在 `project.asl` 另写
- cps 4：维持，没有对白样本
- slack 2：维持，没有反证
- hold 10：三支常规 MV 有 8 个超过 10s 的无台词长镜，全是前奏立世界、副歌定格或尾奏收束，多带运镜；8 会把它们全判拖沓，更长的签名镜标「停留」
- hook 0：维持。4 部前 3 秒 0–1 刀，首镜 4.6–14.4s

来源：
1. This Is America（索尼音乐中国搬运）— B 站 — https://www.bilibili.com/video/BV1uJ41187KZ
2. HUMBLE.（木JJ 字幕版）— B 站 — https://www.bilibili.com/video/BV1kx411S77K
3. 告白气球（1080P 原版）— B 站 — https://www.bilibili.com/video/BV1xx411u7Mu
4. Dynamite（WNS 中字）— B 站 — https://www.bilibili.com/video/BV1Lh411o7rJ
5. Hiro Murai / Larkin Seiple 访谈 — Kodak — https://www.kodak.com/en/motion/blog-post/hiro-murai-larkin-seiple/
6. Childish Gambino's 'This is America': Behind the music — Gulf News — https://gulfnews.com/entertainment/music/childish-gambinos-this-is-america-behind-the-music-1.61158700
7. "This Is America" director Hiro Murai breaks down the video — The Fader — https://thefader.com/2018/05/11/this-is-america-director-hiro-murai-music-video-interview
8. Interview: The Editor of "This is America" — PremiumBeat — https://www.premiumbeat.com/blog/interview-editor-this-is-america/
9. Humble (song) — Wikipedia — https://en.wikipedia.org/wiki/Humble_(song)
10. Hiro Murai — Wikipedia — https://en.wikipedia.org/wiki/Hiro_Murai
11. Emily Caston, 'The first cut is the deepest': excerpts from a focus group on editing music videos — Music, Sound and the Moving Image 11:1 (2017) — https://repository.uwl.ac.uk/id/eprint/4706/
12. The Chemical Brothers: Star Guitar — Visual Music Archive — https://visualmusicarchive.org/works/w/the-chemical-brothers-star-guitar.html
13. Michel Gondry's happy accidents — Signal v. Noise — https://signalvnoise.com/archives2/michel_gondrys_happy_accidents
14. 南门录像厅《剪辑师是怎么来给视频卡点提升剪辑节奏的？》— B 站（本地语音转写）— https://www.bilibili.com/video/BV1xV411r739
15. 南门录像厅《如何张弛有度的卡点》— B 站（本地语音转写）— https://www.bilibili.com/video/BV1Qk4y1274M
16. 杰威尔音乐《最伟大的作品 幕后花絮》— B 站（本地语音转写）— https://www.bilibili.com/video/BV1XT411j7vr
17. Cutting one frame ahead of the beat? — Reddit r/VideoEditing — https://www.reddit.com/r/VideoEditing/comments/ikqjdo/
18. BTS' 'Dynamite' breaks YouTube Premiere and 24-hour records — YouTube 官方博客 — https://blog.youtube/culture-and-trends/bts-dynamite-breaks-youtube-premiere-records/
19. Dynamite (BTS song) — Wikipedia — https://en.wikipedia.org/wiki/Dynamite_(BTS_song)

## Vlog（`vlog`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| Casey Neistat《$21,000 头等舱座位》 | 正片开场 90s（裁掉搬运片头 0–11s） | 18（人工估 35–40） | 5.00（人工估 2.3–2.6） | 3.29 | 1.41–11.72 | 0 | 检测器把字卡叠画、超延时、自拍跳切并成长镜，按人工刀数用 |
| Yes Theory《搭便车穿越中国》 | 0–92s（到开局黑卡） | 37 | 2.49 | 1.50 | 0.63–5.15 | 0 | 3–5s 光晕转场多检约 3 刀；70–92s 规则动画计 1 镜 22s |
| 飓多多《公司派我去坐 30 万的火车》 | 0–90s | 40（人工估 46–48） | 2.25（人工估约 1.9） | 1.85 | 0.90–3.77 | 0 | 对镜段跳切漏检；分段 ASL 0–15s 1.85、15–30s 2.13、30–60s 2.18、60–90s 2.86 |
| 房琪kiki《你以为这是宫崎骏的漫画，但其实，它是大理》 | 全片 0–63s | 34 | 1.85 | 1.80 | 1.00–2.58 | 2（含黑场多检，实为 1） | 检测与 2fps 联系表一致；切点对齐旁白句首（偏差 ≤0.4s），旁白覆盖约 87% |

切镜口径：PySceneDetect AdaptiveDetector 3.0，最小镜长 0.25s；同机位跳切会漏检，对镜段按联系表人工数刀。开场 90 秒剪辑密度（含跳切）23–32 刀/分钟（Casey 35–40 刀/90s、飓多多 46–48/90s 为人工估，Yes Theory 37/92s、房琪 33/63s）。子代理报告里「对镜约每 2.5–4 秒一处跳切」「定点走入 2.5s」「A-roll 连续 8–17s」只有人工目测、没有留下原始记录，未写进卡片。

语速（mlx-whisper large-v3-turbo 转写，音画对位已核对；毛语速 = 字数 ÷ 首句起点到末句终点）：
- 房琪 · 抒情旁白 · 净 4.43 / 毛 3.94 字/秒（243 字）
- 飓多多 · 开场快旁白（0–42.6s）· 净 6.03 / 毛 5.92 字/秒（252 字）
- 飓多多 · 现场对镜与对话（43–91s）· 净 5.05 / 毛 4.36 字/秒（205 字）
- 飓多多 · 信息旁白（93–114s）· 净 4.59 / 毛 4.38 字/秒（90 字）

pace 取值依据：
- asl 2-8 → 2-6：4 部开场实测 ASL 1.85–2.5s（Casey 检测值把跳切并入也只有 5.0）；按「一个要点一行」写分镜，A-roll 行 8–15s、B-roll 行 1–3s，混合后约 2.5–5s
- cps 维持 4.5：毛语速对镜对话 4.4、信息旁白 4.4、抒情旁白 3.9、开场快旁白 5.9，4.5 落在主体区间
- slack 3 → 2：旁白型切点落在句首（偏差 ≤0.4s），对镜段靠跳切去掉停顿。注意 samples/14-vlog 第 11 镜（21 字、8.5s、已标停留）会判拖沓，需要补 `pace_note` 或缩到 7.8s
- hold 12 → 8：Yes Theory、飓多多、房琪三部全片 p90 为 5.15、3.77、2.58s（Casey 检测值 11.72 是跳切和字卡被合并的结果）；10–30s 的情绪长镜要标「停留」并写 `pace_note`
- hook 0 → 15：4 部范本都在 15s 内说出前提；竖屏短 vlog 在 `project.hook` 写 3

来源：
1. 飓多多StormCrew《公司派我去坐30万的火车…》及系列播放数据 — B站 / Just One API — https://www.bilibili.com/video/BV1fSFnzzEwc
2. 《影视飓风 Tim：先做标题和封面，再定内容架构》— 汽车之家 — https://www.autohome.com.cn/news/202511/1310715.html
3. 房琪kiki《你以为这是宫崎骏的漫画，但其实，它是大理》及账号播放数据 — B站 / Just One API — https://www.bilibili.com/video/BV1w5411m7Tu
4. Top Chinese KOLs in 2023 — Hicom Asia — https://www.hicom-asia.com/top-chinese-kols-in-2023/ —（据搜索摘要，未读原文）；另参考 人人都是产品经理《旅行博主内容对比》— https://www.woshipm.com/operate/4572961.html
5. The Nerdwriter 对 Casey Neistat 日更 vlog 的分析 — YouTube（字幕经 Just One API）— https://youtu.be/JbiJqTBCQuw ；介绍文 — https://laughingsquid.com/an-insightful-analysis-showcasing-the-unique-style-of-casey-neistats-seemingly-effortless-daily-vlog/
6. How Casey Neistat Changed Vlogging Forever — In Depth Cine — https://indepthcine.com/videos/casey-neistat
7. Casey Neistat《$21,000 First Class Airplane Seat》中字搬运 — B站 — https://www.bilibili.com/video/BV1TJ411r7Ux
8. Peter McKinnon B-roll 教学 — YouTube（字幕经 Just One API）— https://youtu.be/TXzLvYN-HSc ；转述 Videomaker — https://www.videomaker.com/videonews/2017/09/use-more-b-roll-to-instantly-make-your-videos-look-more-cinematic/
9. Yes Theory《Hitchhiking across China》搬运 — B站 — https://www.bilibili.com/video/BV1pe411C7X7 ；Tommy Dajer Skillshare 课程页 — https://www.skillshare.com/de/classes/storytelling-durch-film-wie-man-fesselnde-videos-fur-youtube-erstellt/1022218532 —（课程页据搜索摘要，未读原文）
10. Measure key moments for audience retention — YouTube 帮助中心 — https://support.google.com/youtube/answer/9314415 —（页面直取失败，据搜索摘要）
11. 映美剪辑学院 海伦《拉片解析【自媒体VLOG】》— B站（AI 字幕经 Just One API）— https://www.bilibili.com/video/BV1Z6azzgEDq

## 预告片 / 游戏 PV（`trailer-pv`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 《社交网络》正式预告（Mark Woollen & Associates） | 5.1–132.6s | 102 | 1.25 | 0.92 | 0.58–2.25 | 0 | 裁掉分级绿卡和 MovieClips 片尾；三段 ASL 1.62 / 1.20 / 0.87；片名卡 3.8s、日期卡 2.6s |
| 《盗梦空间》预告 #3 | 3.1–141.2s | 73 | 1.89 | 1.38 | 0.83–2.97 | 1 | 首镜是厂牌；高潮慢镜 5.25s → 黑场约 0.9s → 片名约 5s → button 约 4s → 日期 1.5s |
| 《流浪地球2》终极预告 | 全片 0–188.6s | 124 | 1.52 | 1.17 | 0.67–2.69 | 2 | 前两刀是黑场字卡；主创名字卡约 1–1.8s；片名卡 3.5s，184s 后是二维码尾板 |
| 《黑神话：悟空》最终预告（阈值 3.0） | 全片 0–285.8s | 90 | 3.18 | 2.07 | 0.83–5.53 | 0 | 水墨式叠化和暗场漏检多，当上限用；首镜含 6s 黑场 logo 和 14s 立世界运镜 |
| 《黑神话：悟空》最终预告（阈值 1.5） | 全片 0–285.8s | 140 | 2.04 | 1.30 | 0.37–4.00 | 0 | 补回叠化切点但会把闪白算成刀，真实 ASL 在 2.0–3.2 之间；水墨片名约 14s，25s 剧情 button |

切镜口径：PySceneDetect AdaptiveDetector 3.0（黑神话另跑 1.5），最小镜长 0.25s；B 站官方号或搬运版，抽帧核对片名、黑场、button 位置。

分段 ASL（秒）：社交网络 1.62 → 1.20 → 0.87；盗梦空间 2.34 → 2.06 → 1.43 / 1.54；流浪地球2 1.57 →（对白段 1.95）→ 1.19 → 1.36 → 1.33；黑神话（阈值 1.5）3.10 → 1.28 → 2.03 → 1.19 → 1.28，两轮快切之间有一个 10.6s 长镜。

卡拍实测（librosa；±80ms 窗口）：
- 社交网络 · 拍点命中 50.5%（随机 43.1%）· 强起音 10%（随机平移 11%）
- 流浪地球2 · 拍点命中 33.0%（随机 32.8%）· Rayleigh p≈0.77
- 盗梦空间 · 拍点命中 26.9%（随机 32.8%）；全片最强的 10 个声音重击中 8 个在 ±250ms 内有切点（随机时刻 27%），5 个在 ±50ms 内
- 黑神话 · 切点与拍点显著锁相（Rayleigh p<0.001），但多数切点比拍点早 0.12–0.2s（3–5 帧）；拍点与起音的偏差中位数 0ms，音视频容器起点都是 0

语速：
- 《流浪地球2》终极预告 · 毛 2.6 字/秒（B 站 AI 字幕纯中文 29 句，258 字 / 99.2s；本地 Whisper 转写句段一致；单句 1.2–5.0 字/秒，说明性台词和 AI 播报 3.5–4.1，情绪重句 1–1.5）。单一样本且和说明性台词的 3.5–4.1 不一致，卡片 cps 暂不改，留作以后参考
- 《黑神话》最终预告 · 测不了（无字幕，Whisper 转写被配乐干扰成幻听）

pace 取值依据：
- asl 1.2–3：拿 2011 金预告片奖 Best in Show 的社交网络 ASL 1.25，流浪地球2 1.52，盗梦空间 1.89；上限 3 留给世界观 CG PV（黑神话 2.0–3.2）
- cps 3.5：维持。唯一中文样本毛语速 2.6，但说明性台词 3.5–4.1，证据不一致
- slack 1：维持，没有反证
- hold 6：维持。p90 为 2.25–5.5s；超过 6s 的无台词镜头只有立世界开场、高潮慢镜和片名揭示，按「停留」处理
- hook 6：维持。4 部有 3 部在 7s 内给出第一个钩子；先放厂牌的游戏 PV 在 6–8s

来源：
1. 社交网络 正式预告（桃桃字幕组搬运）— B 站 — https://www.bilibili.com/video/BV1Ts411o7To
2. 盗梦空间 Trailer #3 — B 站 — https://www.bilibili.com/video/BV19j411r7EM
3. 黑神话：悟空 最终预告（游戏科学官方）— B 站 — https://www.bilibili.com/video/BV1oH4y1c7Kk
4. 流浪地球2 终极预告（官方）— B 站 — https://www.bilibili.com/video/BV1UY4y1Z7KD
5. How to Make a Movie Trailer - Editing 3-Act Trailer Structure — YouTube / Derek Lieu — https://www.youtube.com/watch?v=MhfyvQihMa8
6. How to Make an Indie Game Trailer — YouTube / Game Maker's Toolkit — https://www.youtube.com/watch?v=4CSYA9R70R8
7. 千舟cut《预告片剪辑的结构思路》— B 站（本地语音转写，内容基本转述自 5）— https://www.bilibili.com/video/BV1JZ421u7ra
8. 南门录像厅《如何张弛有度的卡点》— B 站（本地语音转写）— https://www.bilibili.com/video/BV1Qk4y1274M
9. Mark Woollen — Wikipedia — https://en.wikipedia.org/wiki/Mark_Woollen
10. The Social Network: a short film that's also a trailer — RogerEbert.com — https://www.rogerebert.com/scanners/the-social-network-a-short-film-thats-also-a-trailer
11. The Social Network: Choral Rendition of Radiohead's Creep — UBC 课程博客 — https://blogs.ubc.ca/musc326a/?p=806
12. BRAAAM — Wikipedia — https://en.wikipedia.org/wiki/BRAAAM
13. BRAAAM 声音来源争议报道（Zarin / Zimmer / Hemsey）— The Hollywood Reporter — https://www.hollywoodreporter.com/news/braaams-beginners-how-a-horn-793220
14. 《黑神话：悟空》TGA 2024 获最佳动作游戏、玩家之声 — IT之家 — https://www.ithome.com/0/844/828.htm
15. Cutting one frame ahead of the beat? — Reddit r/VideoEditing — https://www.reddit.com/r/VideoEditing/comments/ikqjdo/

## 片头 / 活动开场片（`opening-title`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| 《七宗罪》片头（Kyle Cooper，阈值 3.0） | 2.3–129.1s | 110 | 1.19 | 0.81 | 0.25–2.63 | 0 | 手刮字、闪帧、抖动会多检；四段 ASL 1.71 / 1.28 / 0.94 / 1.07 |
| 《七宗罪》片头（阈值 5.0） | 2.3–129.1s | 71 | 1.84 | 1.08 | 0.26–4.09 | 0 | 镜数下限，真实值在两种阈值之间 |
| 《真探》第一季片头（Patrick Clair） | 5.8–97.9s | 45 | 2.05 | 2.00 | 0.20–3.96 | 0 | 裁掉 HBO 台标；叠化 / 多重曝光过渡会漏检；片名在 84–90s 火光中出现 |
| 北京冬奥会二十四节气倒计时（张艺谋团队） | 全片 0–212s | 109 | 1.94 | 1.50 | 0.80–3.00 | 0 | 首镜 17.7s 说明字卡；24→11 数字卡 2.97–3.07s、每数约 11s（6.9–15.1s）；9→2 恒定 2.73s；「1 立春」约 7.6s |
| 《长安十二时辰》第一集开场（曹盾） | 0–161.8s | 12 | 13.49 | 2.50 | 1.14–91.6 | 0 | 127s 连续长镜（抽帧确认无明切）+ 25s 内 10 镜快切 + 书法片名 3.1s + 时辰卡 6.5s；只代表一镜到底型 |

切镜口径：PySceneDetect AdaptiveDetector 3.0（七宗罪另跑 5.0），最小镜长 0.25s；B 站搬运版，抽帧核对数字卡、片名和长镜。未实测、只用制作资料的范本：Saul Bass《迷魂记》《惊魂记》、《权力的游戏》（约 90s 连续飞行）、《西部世界》。《繁花》片头在 B 站只搜到纯音乐版，没能实测。

卡拍实测（librosa；±80ms 窗口）：
- 真探 · 单拍 Rayleigh p≈0.56；按 4 拍分组 Rayleigh p≈0.0002，平均相位≈0（落在小节线）；小节线命中 25.6%（随机 8.2%）
- 七宗罪 · 拍点命中 25.2%（随机 23.8%）；最强 10 个重击只有 2 个在 ±100ms 内有切点
- 冬奥倒计时 · 拍点命中 39.8%（随机 36.3%）；Rayleigh 单拍 p≈0.12

设计者口述（冬奥倒计时美术设计去尘）：全片三分钟，每个节气 7–9 秒；原方案每节气约 8 镜、每镜 0.5–1.5 秒，信息太多、全球观众看不懂，压到每节气 3 个左右。实测每个数字后仍检出 4–6 个内容镜（运镜里的大变化也会被算成刀）。

语速：无（范本几乎没有旁白）。

pace 取值依据：
- asl 1–3：维持。实测 1.19–2.05（七宗罪 1.19 / 1.84，真探 2.05，冬奥 1.94）；一镜到底型（长安 13.5）在 `project.asl` 另写
- cps 3：维持，没有旁白样本
- slack 0.8：维持，没有反证
- hold 4：维持。p90 为 2.6–4.1s；超过 4s 的无字镜头只在开场静场、立世界长镜和一镜到底里出现
- hook 5：卡片写开头静场 2–4s，实测去台标后首镜 4.0–5.3s，用 3 会把正常的静场判超时

来源：
1. 七宗罪 片头 — B 站 — https://www.bilibili.com/video/BV16x411f7q8
2. 真探 第一季片头 — B 站 — https://www.bilibili.com/video/BV1Qs411o7Gv
3. 北京冬奥会开幕式二十四节气倒计时（4K50P 纯净版）— B 站 — https://www.bilibili.com/video/BV17q4y1b793
4. 长安十二时辰 第一集开场 — B 站 — https://www.bilibili.com/video/BV1T2AizBEJf
5. Se7en — Art of the Title — https://www.artofthetitle.com/title/se7en/
6. True Detective — Art of the Title — https://www.artofthetitle.com/title/true-detective/
7. Game of Thrones — Art of the Title — https://www.artofthetitle.com/title/game-of-thrones/
8. Westworld — Art of the Title — https://www.artofthetitle.com/title/westworld/
9. Vertigo — Art of the Title — https://www.artofthetitle.com/title/vertigo/
10. 25 Celebrated Saul Bass Title Sequences — The Marginalian — https://www.themarginalian.org/2011/11/28/saul-bass-title-sequences/
11. 怪物尚志MonsLog《冬奥开幕倒计时美术设计去尘：创造前所未有的中国意象》— B 站（AI 字幕）— https://www.bilibili.com/video/BV1FL4y1s7qC
12. Primetime Emmy Award for Outstanding Main Title Design — Wikipedia — https://en.wikipedia.org/wiki/Primetime_Emmy_Award_for_Outstanding_Main_Title_Design
13. 光明日报《二十四节气倒计时，很美很中国！》— B 站 — https://www.bilibili.com/video/BV12m4y1o7ww

## 发布会 / 活动纪实（`event-recap`）

| 范本 | 量的段落 | 镜数 | 平均镜长 | 中位 | p10–p90 | 前 3 秒刀数 | 备注 |
|---|---|---|---|---|---|---|---|
| Tomorrowland 2012 官方 aftermovie | 全片 0–1200s | 714 | 1.68 | 1.21 | 0.46–3.21 | 0 | 0–60s 翻书序幕的叠化漏检；正片分段 ASL 1.4–1.8，960–1080s 最快 1.18；BGM 主体约 129 BPM |
| ULTRA CHINA 2017 上海站 aftermovie | 全片 0–347s | 279 | 1.24 | 0.96 | 0.52–2.08 | 0 | 首镜是 logo 卡；breakdown 只挂一个 6.7s 片名大全景，drop 后 90–120s ASL 0.90；0.5s 以下甩镜可能少量多检 |
| 北京冬奥会闭幕式短片《再见》 | 全片 0–146s | 72 | 2.02 | 1.83 | 1.21–2.99 | 1 | 硬切为主，抽查无明显漏检；分段 2.6 → 1.96 → 1.55 → 2.1 → 2.25s，镜长极匀 |

切镜口径：PySceneDetect AdaptiveDetector 3.0，最小镜长 0.25s，联系表抽查。卡点检验：切点落在强 onset（±58ms）上的比例 36% / 40% / 34%，随机基线 34% / 34% / 33%，没有逐拍对齐；Tomorrowland 每 5 秒的音量与刀数相关 r=0.39，响段（>−7dB）ASL 约 1.2s，静段（<−12dB）约 2.0s。画面配比（两部电音节各抽 60 帧人工分类）：规模 32–35%，观众 + 表演者 51–56%，细节与品牌 8–17%。纯快剪 90 秒镜数由平均镜长 1–1.8s 换算为 50–90。复核：5s 以上的镜头占 2.8%（Tomorrowland）、1.8%（ULTRA）、1.4%（冬奥）；Tomorrowland 尾声 1094–1180s 镜长多在 1.8–3.7s，约为正片中位的 1.8 倍；冬奥收尾 2.25s，是中段 1.55s 的 1.45 倍。

语速：北京冬奥闭幕片（CCTV 转播版）· 净 3.7 / 毛 2.8 字/秒（157 字；这段人声可能是转播解说或致辞混入，只作参考）

pace 取值依据：
- asl 维持 1-4：实测全片 1.24–2.02s，落在区间下段；上限 4 留给人物线集锦（本次没有实测）。纯快剪项目在 `project.asl` 写 1-1.8
- cps 维持 4：唯一中文样本毛 2.8、净 3.7 字/秒且归属存疑；回顾片人声多是一句话的现场短句
- slack 维持 1.5：现场原声一句说完就接下一段，不留长尾
- hold 维持 8：两部电音节 8s 以上的镜头不到 1%，breakdown 长镜 6.7s
- hook 6 → 4：60–180s 社媒回顾的三条一手来源都把钩子压在前 2–4 秒（F1 快剪 2s、Andreas Hem 3s、Sarellas 4s）；长版 aftermovie 在 `project.hook` 写 0

来源：
1. How To Make The Perfect Music Festival AfterMovie — Robin Piree 博客 — https://robinpiree.com/blog/how-to-make-the-perfect-music-festival-after-movie
2. The festival after-movie that feels like home — Ticket Fairy 博客 — https://www.ticketfairy.com/blog/2025/08/25/the-festival-after-movie-that-feels-like-home-editing-and-rights/
3. Get to Grips with the Music Festival Aftermovie — FestivalPro — https://festivalpro.com/festival-management/2103/news/2022/9/29/Get-to-Grips-with-the-Music-Festival-Aftermovie.html
4. Tomorrowland 2012 Official Aftermovie（搬运）— B站 — https://www.bilibili.com/video/BV1Gs411k7Xb
5. How to Edit a 🔥 Event Recap Video for Brands — Peter Sarellas — YouTube（字幕经 Just One API）— https://www.youtube.com/watch?v=6L2v4B4teE0
6. How to make BETTER aftermovies! — Andreas Hem — YouTube（字幕经 Just One API）— https://www.youtube.com/watch?v=jtnpnmxQVcE
7. 【剪辑思维】【商业活动实战】用音乐创造结构 — 千舟cut — B站（本地 whisper 转写）— https://www.bilibili.com/video/BV1CY411n77u
8. 商业活动类视频剪辑案例分享｜F1活动剪辑 — 梨与橙PD — B站（本地 whisper 转写）— https://www.bilibili.com/video/BV17p421Q7bu
9. ULTRA CHINA 2017 Official Aftermovie — 香蕉娱乐OFFICIAL — B站 — https://www.bilibili.com/video/BV19W411W71Y
10. YouTube UK Blog 2014-07（Tomorrowland 2011–2013 aftermovie 合计约 2.6 亿播放）— https://youtube-uk.googleblog.com/2014/07/
11. Red Bull Dance Your Style World Final 2024 Mumbai — Webby Awards — https://winners.webbyawards.com/2025/video-film/general-video-film/events-live-streams/326993/red-bull-dance-your-style-world-final-2024-mumbai
12. 北京冬奥会闭幕式导演专访 — 新京报 — https://m.bjnews.com.cn/detail/164518327014528.html
13. 北京冬奥会闭幕式短片 — 人民日报 — B站 — https://www.bilibili.com/video/BV1Jm4y1o7wf
14. 商业快剪第16期｜什么是教科书级别的活动快剪 — 才紫哥 — B站（前 40 分钟本地 whisper 转写）— https://www.bilibili.com/video/BV1f64y1D7x9
