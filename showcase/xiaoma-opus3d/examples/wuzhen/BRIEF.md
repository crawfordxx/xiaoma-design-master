# 乌镇场景 · 子 Agent 施工规范

项目根目录：本仓库的 `examples/wuzhen/`。three.js r170，原生 ES 模块，没有构建步骤。

## 硬规则

1. **不准用任何外部 3D 模型、贴图、照片、字体文件或网络资源。** 几何、材质、纹理全部用代码生成，纹理可以用 Canvas 画。
2. **坐标只能从 `src/layout.js` 读。** 不要自己编建筑、桥、树的位置。需要细节位置（比如灯笼挂点）时，从 layout 的记录推导出来，或者用 `houseAnchors(h)`。
3. **你只能改自己的那个区块文件**：`src/zones/<你的区块>.js`，外加 `review-<你的区块>.md` 和 `out/shots/<你的区块>/`。下面这些公共文件只读，**发现 bug 写进 review 文件报告，不要自己改**：
   `src/layout.js` `src/rng.js` `src/materials.js` `src/geom.js` `src/house.js` `src/paths.js` `src/lighting.js` `src/main.js` `scripts/*`
4. **随机数一律 `rng('<区块>-<物件 id>')`，禁止 `Math.random`。** 同一个 key 永远给出同一串数。
5. **动画只由 t 决定。** `update(t)` 必须是 t 的纯函数：不准用 `clock.getDelta()`、`performance.now()`、`Date`，也不准累加上一帧的状态。同一个 t 调两次，画面必须一样。
6. 材质优先用 `ctx.materials` 里的全局材质。确实需要新材质（比如水面 shader、布料）可以在自己文件里建，但颜色要和全局材质协调。

## 接口

```js
// src/zones/<区块>.js
export function build(ctx) { /* 返回一个 THREE.Group（可以是 async） */ }
export function update(t) { /* 可选，t 单位秒，0~70 */ }
```

`ctx` 里有：

| 字段 | 内容 |
|---|---|
| `THREE` | three.js |
| `layout` | `src/layout.js` 的全部导出：`EXTENT LEVELS BAY rivers bridges streets houses pavilionFootprint corridors waterSteps dyeYard pagoda backdrop trees boats lighting` |
| `materials` | 全局材质：`wall tile tileRidge wood woodDark stoneSlab embankment cloth lantern lanternFrame interiorGlow windowGlow darkInterior flagCloth bark foliageWillow foliageCamphor earth field`（灯笼和室内暖光的亮度由 lighting.js 统一控制，不要自己改 emissiveIntensity） |
| `rng` | `rng(key)` → `{ next, range(a,b), int(a,b), pick(arr), chance(p) }` |
| `geom` | `boxM(w,h,d)`、`planeM(w,h)`：UV 以米为单位；`place(geom,{x,y,z,rx,ry,rz})`；`mergeByMaterial([{geom,mat}])` → Group；`tiledRoofSlope({width,run,rise,sag,detail})` 带瓦垄的屋面；`eaveTiles(width, M)` 滴水瓦当；`TILE_PITCH` |
| `buildHouse(h, {materials, rng})` | 参数化民居，h 是 `layout.houses` 里的一条记录 |
| `houseAnchors(h)` | 世界坐标挂点：`front`（正门侧檐下）、`waist`（腰檐下）、`doors`、`water`（临水侧檐下/水阁檐下）、`ridgeY` |
| `houseToWorld(h,x,y,z)`、`HOUSE` | 民居局部坐标 → 世界坐标；民居尺寸常量 |
| `paths` | `boatAt(boatOrId, t)` → `{x,y,z,rotY,dir}`（船头朝局部 +X）；`lerp smoothstep clamp01 easeInOutCubic` |
| `scene` `renderer` | 只读，用于 Reflector 之类需要它们的对象 |

**UV 约定**：所有几何的 UV 单位是米，全局材质的贴图 repeat 已经按真实尺寸设好。自己建 BufferGeometry 时也按米写 UV。

## 坐标系

单位米。原点 = 十字河口中心；+X 朝东，+Z 朝南，Y 朝上。地面（驳岸顶面）`y=0`，水面 `y=-1.2`，河床 `y=-3.2`。太阳在西偏南（方位 260°），高度从 6° 降到 1°。

## 性能预算

最终 1920×1080 带水面反射、bloom 要渲染 2100 帧。请做到：
- 同材质合并（`mergeByMaterial`），重复的小物件用 `InstancedMesh`。每个区块 draw call 尽量 < 150。
- 不要给小物件开 `castShadow`；灯笼不投影。
- 不要加实时 PointLight / SpotLight（lighting.js 已经统一放好了灯笼点光源）。

## 截图与对比（每个区块必须做，最多 3 轮）

```bash
cd examples/wuzhen
node scripts/check-layout.mjs                       # 先确认 layout 没被改坏
node scripts/shot.mjs --zones _ground,_water,<你的区块> --views top,<相关预设> --t 0 --out out/shots/<你的区块>
node scripts/shot.mjs ... --t 70                    # 再看一次华灯初上
node scripts/shot.mjs ... --view "name:px,py,pz:tx,ty,tz:fov"   # 自定义机位，可多次
```

- `_ground`、`_water` 是主 Agent 放的临时地面和平水面，其他人的区块还没做完时用它们当背景。`terrain` 和 `water` 两个区块本身就不要再叠这两个占位了。
- 预设机位在 `scripts/views.mjs`：`top aerial street-west river-east river-west bridge-corner north-bank branch-north branch-south dye pagoda`。
- `top` 是正交俯视，自动叠加 layout 轮廓（洋红线），用来检查**位置**：有没有东西压进河道、压到别人的区域。
- 截完用 Read 工具看图，对照下面的乌镇参考特征逐条检查，写进 `review-<区块>.md`：
  - **位置**：俯视图里每样东西是否落在 layout 规定的范围里
  - **比例**：檐高和河宽之比、拱桥高跨比、人眼高度（1.6m）看过去是否合理
  - **颜色**：墙不能纯白（暖灰），瓦是蓝灰不是纯黑，木构是暗栗色，石头偏青灰
  - **细节密度**：近景特写会拍到的物件够不够细
  - 每一轮写明：发现的问题 → 改了什么 → 改完的截图路径
- 天空和曝光由主 Agent 在调，不归你管，看的时候忽略天空。

## 乌镇参考特征（没有附照片，按这些描述对照）

- 白墙黛瓦，墙面有水渍霉斑、墙脚返潮发绿；木构是深栗壳色，老旧发暗
- 枕水人家：房子背面直接临河，有些用石柱木桩把水阁挑到河面上；水阁一圈花格窗，窗下是木板
- 南岸沿河是廊棚：木柱 + 单坡瓦顶，靠水一侧是“美人靠”长木座椅，檐下挂一串红灯笼
- 石拱桥用青灰条石砌，拱券石缝清楚，桥面是台阶，两侧石栏板和望柱；拱和倒影合成一个圆
- 河埠头：从驳岸伸进水里的几级石阶，最下面几级常年泡水、发暗长青苔
- 摇橹船：木船，船中部有拱形乌篷，船尾一支长橹
- 染坊：高高的竹木架子上挂着几米长的蓝印花布，一条条垂下来，随风轻摆
- 傍晚：灯笼和窗户亮起来，倒影在水面上拉成长条
