// 场景平面图 —— 全项目唯一的坐标来源。只放数据，不依赖 three.js，node 可以直接 import 做检查。
// 单位米。原点 = 场景中心（自己定，写清楚）；+X 朝东，+Z 朝南，Y 朝上。
// 字段约定见 skill 的 references/layout-schema.md。
import { rng } from './rng.js';

export const EXTENT = { x0: -100, x1: 100, z0: -100, z1: 100 };
export const LEVELS = { ground: 0 };

// 区块清单 = 子 Agent 清单（main.js 按这个顺序加载 src/zones/<id>.js）
export const ZONES = ['terrain'];

// ---------- 场景内容（按项目自己定义，例子见 references/examples/） ----------
export const buildings = [
  // { id: 'hall', rect: { x0: -10, x1: 10, z0: -30, z1: -14 }, height: 14 },
];

// ---------- 光照 ----------
// 方位角：0=北(-Z)，90=东(+X)，180=南(+Z)，270=西(-X)；水平方向向量 = (sin b, -cos b)
export const lighting = {
  sunBearingDeg: 250, sunElevationStartDeg: 7, sunElevationEndDeg: 2,
  glowStart: 0.2, glowEnd: 1.0, duration: 70,
  pointLights: [], // [{ x, y, z, color, distance }]，只放镜头里真需要照亮地面的那几盏
};

// ---------- 交互模型的默认设定（viewer.js 读取；嵌入时传参可以覆盖） ----------
export const viewer = {
  name: '示例场景',                                   // 加载层和演示页标题
  title: '示例场景 · 加载中…',
  time: 50,                                            // 光照时刻（0 ~ lighting.duration）
  view: { pos: [90, 55, 90], target: [0, 0, 0], fov: 45 }, // 初始视角：一眼能看懂整个场景的高位斜视
  minDistance: 1.5,                                    // 最近能推到多近（要让特写物件看得清）
  maxDistance: 420,                                    // 最远能拉多远（别拉出远景、露出场景边界）
};

// ---------- 检查用的统一结构（check-layout / check-cameras / plan-svg / 俯视叠图都读它） ----------
export const CHECK = {
  // 实体：互相不能重叠。group 相同的可以互相重叠（比如同一组建筑的附属件）
  solids: buildings.map((b) => ({ id: b.id, rect: b.rect, group: b.id })),
  // 禁区（水面、道路……）：实体不能压进来，除非 id 以 allow 里的前缀开头
  keepOut: [
    // { id: 'pond', rect: {...}, allow: ['bridge'] },
  ],
  // 只用于画图的区域（铺装、院落……）
  zones: [],
  // 镜头碰撞体：rect × [y0, y1]；open(x,y,z) 返回 true 表示这里是可穿过的开口（桥洞、门洞）
  volumes: buildings.map((b) => ({ id: b.id, rect: b.rect, y0: -1, y1: b.height + 1 })),
  // 运动路径：必须整段留在 mustStayIn 的并集里
  paths: [
    // { id: 'boat1', points: [[-50, 0], [50, 0]], halfWidth: 0.9, mustStayIn: ['pond'] },
  ],
};

// 项目特有的规则（比如“桥两端必须落在岸上”），返回错误字符串数组
export function extraChecks() {
  return [];
}
