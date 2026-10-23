// 程序化黄昏天空（替代物理天空，便于控制颜色）。颜色在线性空间里插值，参数只由 t 决定。
import * as THREE from 'three';

const vert = /* glsl */`
varying vec3 vDir;
void main() {
  vDir = normalize((modelMatrix * vec4(position, 1.0)).xyz - cameraPosition);
  vec4 p = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
  gl_Position = p.xyww; // 永远在最远处
}`;

const frag = /* glsl */`
uniform vec3 sunDir;
uniform vec3 zenith; uniform vec3 horizonSun; uniform vec3 horizonAnti; uniform vec3 sunGlow; uniform vec3 sunDisc;
uniform vec3 cloudLit; uniform vec3 cloudShade; uniform float discIntensity; uniform float glowStrength;
varying vec3 vDir;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
  vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}
float fbm(vec2 p) { float v = 0.0; float a = 0.5; for (int i = 0; i < 5; i++) { v += a * noise(p); p *= 2.03; a *= 0.5; } return v; }

void main() {
  vec3 d = normalize(vDir);
  float h = d.y;
  vec2 dh = normalize(d.xz + 1e-5); vec2 sh = normalize(sunDir.xz);
  float az = clamp(dot(dh, sh) * 0.5 + 0.5, 0.0, 1.0); // 1 = 朝太阳方位，0 = 背对（必须夹紧，否则 pow 出 NaN）
  vec3 horizon = mix(horizonAnti, horizonSun, pow(az, 1.6));
  float up = clamp(h, 0.0, 1.0);
  vec3 col = mix(horizon, zenith, pow(up, 0.55));
  float cosA = max(dot(d, sunDir), 0.0);
  col += glowStrength * sunGlow * (pow(cosA, 8.0) * 0.3 + pow(cosA, 64.0) * 0.8) * exp(-up * 3.0);
  // 层云：投影到天穹平面上的拉长 fbm
  if (h > 0.0) {
    vec2 uv = d.xz / (h + 0.06);
    float c = fbm(uv * vec2(0.9, 2.6) + vec2(3.1, 7.7));
    c = smoothstep(0.52, 0.78, c) * smoothstep(0.0, 0.05, h) * (1.0 - smoothstep(0.35, 0.7, h));
    vec3 cc = mix(cloudShade, cloudLit, pow(az, 2.0) * (0.4 + 0.6 * pow(cosA, 4.0)));
    col = mix(col, cc, c * 0.85);
  }
  col += sunDisc * discIntensity * smoothstep(0.99975, 0.99990, cosA);
  if (h < 0.0) col = mix(horizon, horizon * 0.55, clamp(-h * 6.0, 0.0, 1.0)); // 地平线以下：雾霭
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

const C = (hex) => new THREE.Color(hex); // three 的 Color 默认把 hex 当 sRGB 转成线性
// 两个关键时刻的调色板：start = 日落前（太阳 6°），end = 华灯初上（太阳 1°）
const PALETTE = {
  start: { zenith: C(0x4f6c99), horizonSun: C(0xf0b27a), horizonAnti: C(0xa9a3b4), sunGlow: C(0xffc07a), sunDisc: C(0xfff1d6), cloudLit: C(0xf3b18a), cloudShade: C(0x8d8798) },
  end: { zenith: C(0x22304f), horizonSun: C(0xe2784a), horizonAnti: C(0x6e6481), sunGlow: C(0xff8a45), sunDisc: C(0xffc58a), cloudLit: C(0xe0806a), cloudShade: C(0x4e4a60) },
};

export function createSky() {
  const uniforms = {
    sunDir: { value: new THREE.Vector3(0, 0.1, 1) }, discIntensity: { value: 6 }, glowStrength: { value: 1 },
    ...Object.fromEntries(Object.keys(PALETTE.start).map((k) => [k, { value: PALETTE.start[k].clone() }])),
  };
  const mat = new THREE.ShaderMaterial({ uniforms, vertexShader: vert, fragmentShader: frag, side: THREE.BackSide, depthWrite: false, fog: false });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(4000, 48, 24), mat);
  mesh.frustumCulled = false;
  mesh.renderOrder = -1;
  mesh.onBeforeRender = (r, s, camera) => { mesh.position.copy(camera.position); mesh.updateMatrixWorld(); };
  return {
    mesh,
    uniforms,
    set(sunDir, k) {
      uniforms.sunDir.value.copy(sunDir);
      uniforms.glowStrength.value = 0.45 + 0.55 * k; // 太阳越高光晕越刺眼，开头压低
      for (const key of Object.keys(PALETTE.start)) uniforms[key].value.copy(PALETTE.start[key]).lerp(PALETTE.end[key], k);
    },
    horizonColor(k, towardSun) {
      const a = PALETTE.start.horizonSun.clone().lerp(PALETTE.end.horizonSun, k);
      const b = PALETTE.start.horizonAnti.clone().lerp(PALETTE.end.horizonAnti, k);
      return b.lerp(a, towardSun);
    },
  };
}
