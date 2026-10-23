// 预设机位（截图对比用）。pos/target 单位米，坐标系见 layout.js
export const VIEWS = {
  top: { ortho: true },
  aerial: { pos: [-150, 110, 120], target: [0, 0, 0], fov: 45 },
  'street-west': { pos: [30, 1.6, 8.0], target: [-20, 2.2, 7.0], fov: 55 },      // 南岸廊棚街，向西看
  'river-east': { pos: [-60, 1.2, 0.5], target: [0, 2.5, -1], fov: 50 },         // 河面上，向东看两岸
  'river-west': { pos: [40, 1.0, -0.5], target: [-14, 3, 0], fov: 50 },          // 河面上，向西看通济桥
  'bridge-corner': { pos: [-26, 1.8, -10], target: [-8, 2.5, -12], fov: 55 },     // 桥里桥
  'north-bank': { pos: [-40, 1.5, 4.5], target: [-40, 4, -10], fov: 55 },        // 从南岸看北岸枕水人家
  'branch-north': { pos: [0.5, 1.4, -2], target: [0, 3, -50], fov: 50 },         // 支河向北
  'branch-south': { pos: [0.5, 1.4, 10], target: [1, 3, 60], fov: 50 },          // 支河向南
  dye: { pos: [60, 3, 32], target: [32, 4, 52], fov: 55 },                       // 染坊晒布场
  pagoda: { pos: [-20, 6, -10], target: [-215, 25, -215], fov: 30 },             // 远望白莲塔
};
