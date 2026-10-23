// 临时占位（主 Agent 维护）：一块平地，terrain 区块完成前给其他区块截图当背景。
// 场景里有水面、下沉区域时，按 layout 挖空或另写 _water.js 之类的占位。
export function build({ THREE, layout, materials: M, geom }) {
  const e = layout.EXTENT; const w = (e.x1 - e.x0) + 60; const d = (e.z1 - e.z0) + 60;
  const m = new THREE.Mesh(geom.planeM(w, d), M.ground);
  m.rotation.x = -Math.PI / 2;
  m.position.set((e.x0 + e.x1) / 2, layout.LEVELS.ground ?? 0, (e.z0 + e.z1) / 2);
  m.receiveShadow = true;
  return new THREE.Group().add(m);
}
