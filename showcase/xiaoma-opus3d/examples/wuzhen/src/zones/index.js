// 区块注册表：静态引用，打包工具才能把所有区块打进一个文件。
// _ground / _water 是施工期的临时占位，只在截图测试时用到。
import * as terrain from './terrain.js';
import * as water from './water.js';
import * as housesNorth from './houses-north.js';
import * as housesSouth from './houses-south.js';
import * as bridges from './bridges.js';
import * as landmarks from './landmarks.js';
import * as ground from './_ground.js';
import * as waterStub from './_water.js';

export const ZONE_MODULES = {
  terrain, water, 'houses-north': housesNorth, 'houses-south': housesSouth, bridges, landmarks,
  _ground: ground, _water: waterStub,
};
export const DEFAULT_ZONES = ['terrain', 'water', 'houses-north', 'houses-south', 'bridges', 'landmarks'];
