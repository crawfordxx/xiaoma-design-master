# layout.js 约定

layout.js 是全项目唯一的坐标来源。它只放数据（外加少量纯计算的辅助函数），不 import three.js，这样 node 脚本可以直接读它做检查。

## 必须导出的

| 导出 | 说明 |
|---|---|
| `EXTENT` | `{x0,x1,z0,z1}`，主要区块的范围。俯视图和 plan.svg 按它取景 |
| `LEVELS` | 各种标高，至少有 `ground`。有水就加 `water`、`bed` |
| `ZONES` | 区块 id 数组 = 子 Agent 清单，main.js 按这个顺序加载 `src/zones/<id>.js` |
| `lighting` | `sunBearingDeg`、`sunElevationStartDeg/EndDeg`、`glowStart/End`、`duration`、`pointLights` |
| `viewer` | 交互模型默认设定：`name`、`title`、`time`（光照时刻）、`view`（初始视角 `{pos,target,fov}`）、`minDistance`、`maxDistance` |
| `CHECK` | 见下文，所有检查脚本都读它 |
| `extraChecks()` | 返回项目特有规则的错误字符串数组（比如“桥两端必须落在岸上”） |

坐标系：单位米，+X 朝东，+Z 朝南，Y 朝上。原点放在场景最重要的位置（十字河口、主殿前），并在文件头注释写清楚。

方位角：0=北(-Z)，90=东(+X)，180=南(+Z)，270=西(-X)。水平方向向量 = `(sin b, -cos b)`。

## CHECK 结构

```js
export const CHECK = {
  solids:  [{ id, rect, group? }],                 // 实体，两两不能重叠；同 group 的可以互相重叠
  keepOut: [{ id, rect, allow?: ['bridge'] }],     // 禁区（水面、道路），实体不能压进来，除非 id 以 allow 里的前缀开头
  zones:   [{ id, rect }],                         // 只用来画图的区域
  volumes: [{ id, rect, y0, y1, open?(x,y,z) }],   // 镜头碰撞体；open 返回 true 表示开口（桥洞、门洞）
  paths:   [{ id, points: [[x,z],...], halfWidth, mustStayIn: [keepOut id], ignore?: [solid id 前缀] }],
  floorAt?(x, z),                                  // 相机最低高度（交互模型和镜头检查都用），默认 ground + 0.4；有水面时要自定义
};
```

`CHECK` 是从内容数据**推导**出来的，不要手抄一遍坐标。例：

```js
CHECK.solids = [
  ...houses.map((h) => ({ id: `house ${h.id}`, rect: h.footprint })),
  ...trees.map((t) => ({ id: `tree ${t.id}`, rect: circleRect(t) })),
];
CHECK.volumes = houses.map((h) => ({ id: h.id, rect: pad(h.footprint, 0.8), y0: -0.5, y1: ridgeY(h) + 0.5 }));
```

## 内容数据怎么写

- **独特的建筑**（主殿、塔、桥）：逐个写记录，字段包括 id、中心或矩形、朝向、关键尺寸。
- **成批的同类建筑**（民居、摊位）：写“排”的定义（沿哪条线、哪几段、进深多少），用固定种子的 rng 在 layout.js 里展开成逐栋记录。每栋记录都要带 `footprint`，生成器和检查脚本都用它。
- **运动物体**（船、行人）：写路径折线、速度、offset。offset 用来对齐“第几秒经过哪里”，这样镜头才能拍到它穿过桥洞。
- **镜头会特写的物件**：layout 里只需要定到“哪棵树、哪栋房子”，精确的特写坐标让负责的 Agent 在 review 里报告。

## 例子

乌镇的完整 layout 见 `examples/wuzhen.md`：两条河十字相交、88 栋民居分 8 排展开、11 处水阁、4 座桥、3 条船线。
