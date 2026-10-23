// 临时占位（主 Agent 维护）：河道以外的平地，terrain.js 完成前给其他区块截图当背景
export function build({ THREE, layout, materials: M, geom }) {
  const g = new THREE.Group();
  const xs = [-130, -4, 4, 130]; const zs = [-90, -6, 6, 90];
  for (let i = 0; i < 3; i += 2) for (let j = 0; j < 3; j += 2) {
    const w = xs[i + 1] - xs[i]; const d = zs[j + 1] - zs[j];
    const m = new THREE.Mesh(geom.boxM(w, 3.2, d), M.stoneSlab);
    m.position.set((xs[i] + xs[i + 1]) / 2, -1.6, (zs[j] + zs[j + 1]) / 2);
    m.receiveShadow = true; g.add(m);
  }
  return g;
}
