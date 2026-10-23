# {{项目名}} · 子 Agent 施工规范

> 模板：把 {{…}} 换成项目内容，复制到项目根目录的 BRIEF.md。乌镇的实际版本见 examples/wuzhen.md。

项目根目录：`{{项目绝对路径}}`。three.js r170，原生 ES 模块，没有构建步骤。

## 硬规则

1. **不准用任何外部 3D 模型、贴图、照片、字体文件或网络资源。** 几何、材质、纹理全部用代码生成，纹理可以用 Canvas 画。
2. **坐标只能从 `src/layout.js` 读。** 不要自己编建筑、桥、树的位置。需要细节位置（比如灯笼挂点）时，从 layout 的记录推导出来，或者用 `shared` 里生成器提供的挂点函数。
3. **你只能改自己的那个区块文件**：`src/zones/<你的区块>.js`，外加 `review-<你的区块>.md` 和 `out/shots/<你的区块>/`。下面这些公共文件只读，**发现 bug 写进 review 文件报告，不要自己改**：
   `src/layout.js` `src/rng.js` `src/materials.js` `src/geom.js` `src/shared.js` `src/paths.js` `src/sky.js` `src/lighting.js` `src/main.js` `scripts/*`
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
| `layout` | `src/layout.js` 的全部导出：{{列出本项目的数据数组}} |
| `materials` | 全局材质：{{列出材质名}}（发光材质的亮度由 lighting.js 统一控制，不要自己改 emissiveIntensity） |
| `rng` | `rng(key)` → `{ next, range(a,b), int(a,b), pick(arr), chance(p) }` |
| `geom` | `boxM(w,h,d)`、`planeM(w,h)`：UV 以米为单位；`place(geom,{x,y,z,rx,ry,rz})`；`mergeByMaterial([{geom,mat}])` → Group（会丢顶点色和自定义属性）；`tiledRoofSlope`、`eaveTiles` |
| `shared` | 项目公共生成器：{{比如 buildHouse(h, ctx)、houseAnchors(h)}} |
| `paths` | `loopAlong(points, speed, offset, t)` → `{x,z,rotY,dir}`；`lerp smoothstep clamp01 easeInOutCubic` |
| `scene` `renderer` | 只读，用于 Reflector 之类需要它们的对象 |

**UV 约定**：所有几何的 UV 单位是米，全局材质的贴图 repeat 已经按真实尺寸设好。自己建 BufferGeometry 时也按米写 UV。

## 坐标系

单位米。原点 = {{原点在哪}}；+X 朝东，+Z 朝南，Y 朝上。{{各种标高}}。太阳方位 {{°}}，高度从 {{°}} 降到 {{°}}。

## 性能预算（实时交互）

交付物是在浏览器里实时渲染的交互模型，用户的设备可能远不如开发机。目标设备：{{电脑 / 也要手机}}。
- 全场景上限：{{比如 电脑 500 万三角形、500 draw call；手机 150 万、200}}。本区块分到：{{三角形}}、{{draw call}}。
- 同材质合并（`mergeByMaterial`），重复的小物件用 `InstancedMesh`。
- 不要给小物件开 `castShadow`；发光物不投影。
- 不要加实时 PointLight / SpotLight（lighting.js 已经统一放好了）。
- 要做反射用 `three/addons/objects/Reflector.js`，并让 shader 支持 `uReflect = 0`（低档会关反射）。不要自己建离屏渲染目标。
- **交互模型可以从任何角度看**：背面、侧面、高处俯视都要过得去，不能只做朝镜头那一面。

## 截图与对比（每个区块必须做，最多 3 轮）

```bash
cd {{项目绝对路径}}
node scripts/check-layout.mjs                       # 先确认 layout 没被改坏
node scripts/shot.mjs --zones _ground,_water,<你的区块> --views top,<相关预设> --t 0 --out out/shots/<你的区块>
node scripts/shot.mjs ... --t 70                    # 再看一次华灯初上
node scripts/shot.mjs ... --view "name:px,py,pz:tx,ty,tz:fov"   # 自定义机位，可多次
```

- `_ground`、`_water` 是主 Agent 放的临时地面和平水面，其他人的区块还没做完时用它们当背景。`terrain` 和 `water` 两个区块本身就不要再叠这两个占位了。
- 预设机位在 `scripts/views.mjs`：{{列出}}。局部俯视用 `--rect "name:x0,x1,z0,z1"`。
- `top` 是正交俯视，自动叠加 layout 轮廓（洋红线），用来检查**位置**：有没有东西压进河道、压到别人的区域。
- 截完用 Read 工具看图，对照参考照片（或下面的参考特征）逐条检查，写进 `review-<区块>.md`：
  - **位置**：俯视图里每样东西是否落在 layout 规定的范围里
  - **比例**：檐高和河宽之比、拱桥高跨比、人眼高度（1.6m）看过去是否合理
  - **颜色**：墙不能纯白（暖灰），瓦是蓝灰不是纯黑，木构是暗栗色，石头偏青灰
  - **细节密度**：近景特写会拍到的物件够不够细
  - 每一轮写明：发现的问题 → 改了什么 → 改完的截图路径
- 天空和曝光由主 Agent 在调，不归你管，看的时候忽略天空。

## {{主题}}参考特征（附了照片就对照照片；没有照片就按这些描述对照）

- {{材质颜色：墙、顶、木、石分别是什么颜色、什么旧化}}
- {{每类建筑的标志性构件}}
- {{近景特写会拍到的物件该是什么样}}
- {{时段的光线特征}}
