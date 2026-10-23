// 示例区块（替换成项目自己的地形）。每个区块导出 build(ctx) 返回 Group，可选 update(t)。
export function build({ THREE, layout, materials: M, geom }) {
  const e = layout.EXTENT;
  const ground = new THREE.Mesh(geom.planeM(e.x1 - e.x0 + 400, e.z1 - e.z0 + 400), M.ground);
  ground.rotation.x = -Math.PI / 2;
  ground.position.set((e.x0 + e.x1) / 2, layout.LEVELS.ground ?? 0, (e.z0 + e.z1) / 2);
  ground.receiveShadow = true;
  return new THREE.Group().add(ground);
}
