// 区块注册表：静态引用，打包工具才能把所有区块打进一个文件。
// 加一个区块 = 在这里 import 一行 + 在 ZONE_MODULES 里登记 + 写进 layout.ZONES。
// 以 _ 开头的是施工期的临时占位，只在截图测试时用到。
import * as terrain from './terrain.js';
import * as ground from './_ground.js';
import * as layout from '../layout.js';

export const ZONE_MODULES = {
  terrain,
  _ground: ground,
};
export const DEFAULT_ZONES = layout.ZONES;
