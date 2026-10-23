// 临时占位（主 Agent 维护）：平静的深色水面，water.js 完成前用
export function build({ THREE, layout }) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(400, 300), new THREE.MeshStandardMaterial({ color: 0x2a3634, roughness: 0.15, metalness: 0.2 }));
  m.rotation.x = -Math.PI / 2; m.position.y = layout.LEVELS.water;
  return new THREE.Group().add(m);
}
