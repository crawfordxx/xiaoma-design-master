// 水面 + 摇橹船。
// 水面：Reflector 反射（画面 1/2 分辨率）+ 自定义 shader：程序化波纹扰动反射 UV（竖向拉长）、
// 菲涅尔、浑绿水色、驳岸边压暗；船的 V 形尾迹、橹叶涟漪和水沫也在 shader 里算。
// 船：木船体 + 乌篷 + 长橹，橹按 2.5s 周期往复摇，橹叶入水处溅水花。全部只由 t 决定。
import * as THREE from 'three';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { WATER } from '../materials.js';
import { sunDirection } from '../lighting.js';

const TAU = Math.PI * 2;
const DEG = Math.PI / 180;
const STROKE = 2.5;            // 摇橹周期（秒）
const OAR_YAW = 0.25;          // 橹左右摆幅（弧度）。橹叶末端横向最远约 0.92m，平桥桥墩离船舷只留 0.3m
const OAR_TWIST = 0.55;        // 橹叶翻转幅度（弧度）
const BLADE_TILT = 20 * DEG;   // 橹叶一段向后下斜插入水
const LOOM_TILT = 26 * DEG;    // 橹柄一段向前上翘
const BLADE_LEN = 3.3;
const LOOM_LEN = 1.5;
const RINGS_PER_BOAT = 4;
const SPLASH_SLOTS = 8;        // 水花参数表循环使用的槽数
const DROPS_PER_BURST = 40;
const BURSTS = 2;              // 同时可见的最近几次水花
const GRAVITY = 9.8;
const CANOPY_MAX = 1.6;        // 船篷最高点离水面上限（平桥净空 2.2m）
const LIGHT_REF = 1.3;         // 水色亮度基准：t=0 时 (天光 1.25 + 太阳 2.6×sin6°)/1.3 ≈ 1.17。比天光调亮前亮 17%，但 t=70 时不至于在暗场景里发青发亮

let state = null;

// ---------------------------------------------------------------- 船的姿态（t 的纯函数）

function boatPose(st, t) {
  const p = st.paths.boatAt(st.rec, t);
  const [a, b, c, d, e] = st.ph;
  const stroke = TAU * (t + e) / STROKE;
  return {
    x: p.x, z: p.z, dir: p.dir,
    y: p.y + 0.018 * Math.sin(TAU * t / 3.3 + a) + 0.007 * Math.sin(TAU * t / 1.9 + b),
    rotY: p.rotY + 0.012 * Math.sin(stroke + 0.6),
    roll: 0.02 * Math.sin(TAU * t / 4.1 + c) + 0.012 * Math.sin(stroke),
    pitch: 0.009 * Math.sin(TAU * t / 3.3 + a + 1.2) + 0.004 * Math.sin(TAU * t / 2.2 + d),
    yaw: OAR_YAW * Math.sin(stroke),
    twist: OAR_TWIST * Math.cos(stroke),
  };
}

const _m = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const _e = new THREE.Euler();
const _one = new THREE.Vector3(1, 1, 1);
const _p = new THREE.Vector3();

function boatMatrix(pose, out = _m) {
  _e.set(pose.roll, pose.rotY, pose.pitch, 'YZX');
  return out.compose(_p.set(pose.x, pose.y, pose.z), _q.setFromEuler(_e), _one);
}

// 橹杆与水面的交点（世界坐标），也就是橹叶入水处
function oarEntry(st, t) {
  const pose = boatPose(st, t);
  const m = boatMatrix(pose);
  const P0 = new THREE.Vector3(st.pivot.x, st.pivot.y, 0).applyMatrix4(m);
  const ct = Math.cos(BLADE_TILT);
  const D = new THREE.Vector3(-ct * Math.cos(pose.yaw), -Math.sin(BLADE_TILT), ct * Math.sin(pose.yaw))
    .transformDirection(m);
  const k = (st.waterY - P0.y) / D.y;
  return { x: P0.x + D.x * k, z: P0.z + D.z * k, pose };
}

// 第 k 次橹到头（换向）的时刻：yaw = OAR_YAW·(-1)^k
const reversalTime = (st, k) => STROKE * (0.25 + 0.5 * k) - st.ph[4];
const lastReversal = (st, t) => Math.floor(((t + st.ph[4]) / STROKE - 0.25) / 0.5);

// ---------------------------------------------------------------- 水面 shader

const NSTEPS = 6; // layout.waterSteps 的条数，build 里会核对

const WaterShader = {
  name: 'WuzhenWater',
  uniforms: THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {
    color: { value: null },
    tDiffuse: { value: null },
    textureMatrix: { value: null },
    uTime: { value: 0 },
    uLight: { value: 1 },
    uReflect: { value: 1 },
    uShallow: { value: new THREE.Color() },
    uDeep: { value: new THREE.Color() },
    uHalf: { value: new THREE.Vector2(6, 4) },
    uSunDir: { value: new THREE.Vector3(1, 0.1, 0) },
    uSunCol: { value: new THREE.Color() },
  }]),
  vertexShader: /* glsl */`
    uniform mat4 textureMatrix;
    varying vec4 vUv;
    varying vec3 vWorld;
    #include <common>
    #include <fog_pars_vertex>
    #include <logdepthbuf_pars_vertex>
    void main() {
      vUv = textureMatrix * vec4(position, 1.0);
      vec4 wp = modelMatrix * vec4(position, 1.0);
      vWorld = wp.xyz;
      vec4 mvPosition = viewMatrix * wp;
      gl_Position = projectionMatrix * mvPosition;
      #include <logdepthbuf_vertex>
      #include <fog_vertex>
    }`,
  fragmentShader: /* glsl */`
    #define NB 3
    #define NR 12
    #define NS 6
    #define STREAK_TAPS 16
    #define STREAK_LEN 0.1
    #define STREAK_T 0.4
    #define STREAK_GAIN 4.0
    #define TRANS_MAX 0.85
    #define TRANS_LEN 0.45
    uniform sampler2D tDiffuse;
    uniform float uTime, uLight, uReflect;
    uniform vec3 uSunDir, uSunCol;
    uniform vec3 uShallow, uDeep;
    uniform vec2 uHalf;          // 主河、支河半宽
    uniform vec4 uBoat[NB];      // x, z, 航向 dx, dz
    uniform vec2 uBoatSize[NB];  // 船长、船宽
    uniform vec3 uOar[NB];       // 橹叶入水处 x, z, 强度
    uniform vec4 uRing[NR];      // 涟漪圆心 x, z, 年龄, 振幅
    uniform float uDepth;        // 水面到河床
    uniform vec4 uStepA[NS];     // 河埠头：岸线中点 x, z, 伸向河心的方向 nx, nz
    uniform vec4 uStepB[NS];     // 半宽, 伸出长度, 坡度 k, 截距 c（踏步面近似成 y = c - k·u）
    varying vec4 vUv;
    varying vec3 vWorld;
    #include <common>
    #include <fog_pars_fragment>
    #include <logdepthbuf_pars_fragment>

    // NaN 防护：Metal 快速数学下 isnan/isinf 会被优化掉，用位模式判断非有限值
    bool nonFinite(float x) { return (floatBitsToUint(x) & 0x7f800000u) == 0x7f800000u; }
    bool nonFinite3(vec3 v) { return nonFinite(v.x) || nonFinite(v.y) || nonFinite(v.z); }
    vec2 safeNorm(vec2 v, vec2 fallback) { float l = length(v); return l > 1e-6 ? v / l : fallback; }

    float hash12(vec2 p) {
      vec3 p3 = fract(vec3(p.xyx) * 0.1031);
      p3 += dot(p3, p3.yzx + 33.33);
      return fract((p3.x + p3.y) * p3.z);
    }
    float vnoise(vec2 p) {
      vec2 i = floor(p); vec2 f = fract(p); vec2 u = f * f * (3.0 - 2.0 * f);
      return mix(mix(hash12(i), hash12(i + vec2(1, 0)), u.x),
                 mix(hash12(i + vec2(0, 1)), hash12(i + vec2(1, 1)), u.x), u.y);
    }
    // 像素覆盖的水面尺寸比波长大时把这一层波衰减掉，远处不闪
    float att(float lam, float fp) { return 1.0 - smoothstep(lam * 0.12, lam * 0.5, fp); }
    float gw(vec2 p, vec2 d, float lam, float a, float fp) {
      float k = 6.2832 / lam;
      return a * att(lam, fp) * sin(k * dot(normalize(d), p) - sqrt(9.8 * k) * uTime);
    }

    // 船后 V 形尾迹（开尔文角 19.5°）+ 尾后横波
    float wakeH(vec2 p, vec4 b, vec2 sz, float fp) {
      vec2 q = p - b.xy;
      float along = dot(q, b.zw);
      float lat = abs(dot(q, vec2(-b.w, b.z)));
      float a = sz.x * 0.5 - along;          // 离船头的距离
      if (a < 0.0 || a > 45.0 || lat > 0.36 * a + 3.0) return 0.0;
      float arm0 = sz.y * 0.4 + 0.354 * a;
      float w = 0.16 + 0.05 * a;
      float e = (lat - arm0) / w;
      float env = exp(-a / 15.0) * smoothstep(0.0, 0.8, a);
      float h = 0.028 * env * exp(-e * e) * sin(9.0 * (lat - arm0) + 2.6 * a);
      float inside = smoothstep(arm0 + w, arm0 - w, lat) * smoothstep(sz.x, sz.x + 1.5, a);
      h += 0.009 * env * inside * sin(8.16 * a);
      // 橹搅过的一道乱水（只扰动法线，不发白）
      float s = a - sz.x - 0.8;
      if (s > 0.0) h += 0.005 * exp(-lat * lat / 0.2) * exp(-s / 5.0) * smoothstep(0.0, 0.5, s)
                      * (vnoise(p * 5.0 + uTime * vec2(0.3, 0.2)) - 0.5);
      return h * att(0.6, fp);
    }

    float heightAt(vec2 p, float fp) {
      float h = 0.0;
      // 长波按一张低频噪声分片强弱，避免整齐的搓衣板纹
      float m = 0.35 + 1.3 * vnoise(p * 0.16 + uTime * vec2(0.04, 0.01));
      h += m * gw(p, vec2(0.97, 0.24), 3.1, 0.006, fp);
      h += m * gw(p, vec2(0.85, -0.53), 1.9, 0.005, fp);
      h += (1.7 - m) * gw(p, vec2(0.99, -0.12), 1.17, 0.0035, fp);
      h += gw(p, vec2(-0.3, 0.95), 1.0, 0.0018, fp);
      h += (1.7 - m) * gw(p, vec2(0.62, 0.78), 0.71, 0.0021, fp);
      h += gw(p, vec2(0.93, 0.37), 0.47, 0.0015, fp);
      h += gw(p, vec2(0.80, -0.60), 0.29, 0.0009, fp);
      h += gw(p, vec2(0.45, -0.89), 0.19, 0.0005, fp);
      vec2 w = p + 0.7 * vec2(vnoise(p * 0.4 + uTime * 0.1), vnoise(p * 0.4 + 5.0 - uTime * 0.1));
      h += 0.007 * att(1.6, fp) * vnoise(w * 0.9 + uTime * vec2(0.25, 0.04));
      h += 0.003 * att(0.6, fp) * vnoise(w * 2.3 - uTime * vec2(0.1, 0.3));
      h += 0.0011 * att(0.2, fp) * vnoise(p * 6.5 + uTime * vec2(0.4, -0.2));
      for (int i = 0; i < NB; i++) h += wakeH(p, uBoat[i], uBoatSize[i], fp);
      // 橹叶换向时荡开的一圈圈涟漪
      float hr = 0.0;
      for (int j = 0; j < NR; j++) {
        vec4 r = uRing[j];
        vec2 q = p - r.xy;
        float d2 = dot(q, q);
        if (d2 > 9.0 || r.z < 0.0) continue;
        float rr = sqrt(d2);
        float R = 0.06 + 0.42 * r.z;
        float e = (rr - R) / (0.07 + 0.09 * r.z);
        hr += r.w * exp(-1.0 * r.z) * exp(-e * e) * cos((rr - R) * 30.0) * smoothstep(0.0, 0.08, rr);
      }
      h += hr * att(0.2, fp);
      // 橹叶搅动的乱流
      for (int i = 0; i < NB; i++) {
        vec2 q = p - uOar[i].xy;
        float f = exp(-dot(q, q) / 0.09) * uOar[i].z;
        if (f > 0.001) h += f * 0.006 * att(0.15, fp) * (vnoise(p * 14.0 + uTime * 3.0) - 0.5);
      }
      return h;
    }

    // 按亮度取高光部分（不分通道截，免得偏色）
    vec3 hiPart(vec3 c) {
      float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
      return c * (max(l - STREAK_T, 0.0) / max(l, 1e-4));
    }

    float foamAt(vec2 p) {
      float f = 0.0;
      for (int i = 0; i < NB; i++) {
        vec4 b = uBoat[i]; vec2 sz = uBoatSize[i];
        vec2 q = p - b.xy;
        float along = dot(q, b.zw);
        float lat = abs(dot(q, vec2(-b.w, b.z)));
        float a = sz.x * 0.5 - along;
        if (a > 0.0 && a < 20.0) {
          float arm0 = sz.y * 0.4 + 0.354 * a;
          float e = (lat - arm0) / (0.1 + 0.03 * a);
          f += 0.3 * exp(-e * e) * exp(-a / 3.0);                       // 船头分水
        }
        vec2 o = p - uOar[i].xy;
        f += uOar[i].z * (0.9 * exp(-dot(o, o) / 0.003) + 0.3 * exp(-dot(o, o) / 0.03));
      }
      for (int j = 0; j < NR; j++) {
        vec4 r = uRing[j];
        if (r.z < 0.0) continue;
        float rr = length(p - r.xy);
        float e = (rr - 0.06 - 0.42 * r.z) / (0.05 + 0.05 * r.z);
        f += 0.35 * exp(-e * e) * exp(-r.z * 2.2);
        f += 0.5 * exp(-rr * rr / 0.015) * exp(-r.z * 1.6);
      }
      // 打碎成一簇簇泡沫
      // 打碎成一簇簇泡沫（各层旋转错开，避免值噪声的方格感）
      vec2 p2 = mat2(0.8, -0.6, 0.6, 0.8) * p; vec2 p3 = mat2(0.28, 0.96, -0.96, 0.28) * p;
      float n = vnoise(p * 11.0 + uTime * vec2(0.3, -0.2)) * 0.45 + vnoise(p2 * 29.0 - uTime * 0.5) * 0.35
              + vnoise(p3 * 71.0 + uTime * 0.7) * 0.2;
      float fc = min(f, 1.0);
      return clamp(fc * smoothstep(0.55 - 0.3 * fc, 0.66, n), 0.0, 1.0);
    }

    // 折射光线在水里走多远碰到东西：河床、驳岸墙、河埠头踏步（近似成斜面）
    float underwaterPath(vec2 p, vec3 rd) {
      float t = uDepth / max(-rd.y, 0.02);
      bool inMain = abs(p.y) < uHalf.x; bool inBranch = abs(p.x) < uHalf.y;
      float tz = abs(rd.z) > 1e-4 ? (sign(rd.z) * uHalf.x - p.y) / rd.z : 1e4;
      float tx = abs(rd.x) > 1e-4 ? (sign(rd.x) * uHalf.y - p.x) / rd.x : 1e4;
      t = min(t, inMain && inBranch ? max(tz, tx) : (inMain ? tz : tx));
      for (int i = 0; i < NS; i++) {
        vec4 a = uStepA[i]; vec4 b = uStepB[i];
        vec2 q = p - a.xy; vec2 side = vec2(-a.w, a.z);
        float u0 = dot(q, a.zw); float w0 = dot(q, side);
        if (u0 > b.y + 1.0 || abs(w0) > b.x + 1.0) continue;
        float rn = dot(rd.xz, a.zw);
        float den = rd.y + b.z * rn;
        if (abs(den) < 1e-3) continue; // 光线和踏步面平行（Metal 快速数学下 inf/NaN 的比较不可靠，必须提前跳过）
        float ts = (b.w - b.z * u0) / den;
        float us = u0 + ts * rn; float ws = w0 + ts * dot(rd.xz, side);
        if (ts > 0.0 && us > -0.05 && us < b.y && abs(ws) < b.x) t = min(t, ts);
      }
      return clamp(t, 0.0, 50.0);
    }

    void main() {
      #include <logdepthbuf_fragment>
      vec2 p = vWorld.xz;
      float fp = length(fwidth(p));
      float eps = 0.03;
      float h0 = heightAt(p, fp);
      vec2 g = vec2(heightAt(p + vec2(eps, 0.0), fp) - h0, heightAt(p + vec2(0.0, eps), fp) - h0) / eps;
      vec3 toCam = cameraPosition - vWorld;
      vec3 V = toCam / max(length(toCam), 1e-4);
      vec3 N = normalize(vec3(-g.x, 1.0, -g.y));

      // 各向异性扰动：沿视线方向的坡度推动反射图的竖向（倒影被拉成竖条），横向很小
      vec2 F = safeNorm(-V.xz, vec2(1.0, 0.0));
      vec2 R = vec2(-F.y, F.x);
      float w = abs(vUv.w) < 1e-5 ? 1e-5 : vUv.w; // 反射相机平面上 w→0
      vec2 uv = vUv.xy / w + vec2(dot(g, R) * 0.03, dot(g, F) * 0.26);
      float stretch = 0.0045 + clamp(fp * 0.008, 0.0, 0.009);
      vec3 refl = vec3(0.0); float ws = 0.0;
      for (int k = -3; k <= 3; k++) {
        float wk = exp(-float(k * k) / 6.0);
        refl += texture2D(tDiffuse, clamp(uv + vec2(0.0, float(k) * stretch), 0.002, 0.998)).rgb * wk;
        ws += wk;
      }
      refl /= ws;
      // 灯笼、亮窗这类高亮部分再沿竖向拉成长条，并按横向的波纹带打碎成一节一节
      vec3 hi = vec3(0.0); ws = 0.0;
      for (int k = 0; k < STREAK_TAPS; k++) {
        float o = (float(k) / float(STREAK_TAPS - 1) - 0.5) * 2.0 * STREAK_LEN;
        float wk = 1.0 - abs(o) / (STREAK_LEN * 1.15);
        vec3 c = texture2D(tDiffuse, clamp(uv + vec2(0.0, o), 0.002, 0.998)).rgb;
        hi += hiPart(c) * wk;
        ws += wk;
      }
      hi /= ws;
      float band = vnoise(vec2(dot(p, R) * 1.2, dot(p, F) * 5.0) + vec2(0.0, uTime * 0.8));
      band = 0.15 + 0.85 * smoothstep(0.3, 0.7, band);
      vec3 hb = hiPart(refl);
      refl += mix(hb, STREAK_GAIN * hi, band) - hb;
      refl *= vec3(0.9, 0.95, 0.92);
      bool reflBad = nonFinite3(refl); // 反射图里如果混进了别的区块的 inf/NaN，不让它污染整帧

      // 浑水本色：深绿灰，带大块的浊度变化；靠驳岸处压暗
      float tn = vnoise(p * 0.07 + 3.1) * 0.6 + vnoise(p * 0.29) * 0.4;
      vec3 body = mix(uDeep, uShallow, 0.3 + 0.45 * tn) * uLight;
      float bank = max(uHalf.x - abs(p.y), uHalf.y - abs(p.x));
      float shade = mix(0.5, 1.0, smoothstep(0.0, 2.0, bank));
      // 近处浑水本身反射率低，靠一点迎光/背光的明暗把波纹和涟漪显出来
      float facing = dot(-g, safeNorm(uSunDir.xz, vec2(1.0, 0.0)));
      body *= shade * clamp(1.0 + 3.0 * facing, 0.6, 1.6);
      vec3 foamCol = vec3(0.42, 0.45, 0.43) * uLight * shade;
      float foam = foamAt(p);

      float cosT = clamp(dot(N, V), 0.0, 1.0);
      float fres = (0.045 + 0.955 * pow(1.0 - cosT, 5.0)) * uReflect;
      #ifdef USE_FOG
        float fogF = 1.0 - exp(-fogDensity * fogDensity * vFogDepth * vFogDepth);
        body = mix(body, fogColor, fogF);
        foamCol = mix(foamCol, fogColor, fogF);
      #endif
      // 反射图里已经按“眼→水面→物体”全程加过雾，这里不再叠
      if (reflBad) refl = body;
      refl = min(refl, vec3(1e3));
      vec3 col = mix(body, refl * mix(0.8, 1.0, shade), fres);
      // 夕阳碎金：太阳的高光按方位角收窄、按仰角放宽，拉成一条竖向的光带
      vec3 Rv = reflect(-V, N);
      float dAz = max(1.0 - dot(safeNorm(Rv.xz, vec2(1.0, 0.0)), safeNorm(uSunDir.xz, vec2(1.0, 0.0))), 0.0);
      float dEl = Rv.y - uSunDir.y;
      float glint = exp(-dAz / 0.0006 - dEl * dEl / 0.006) * step(0.0, uSunDir.y);
      col += uSunCol * glint * fres * 2.5 * uReflect;
      col = mix(col, foamCol, foam * 0.85);
      // 近处透进去 0.3~0.5m：看得见泡水的踏步、水线下的青苔；深处和掠射角不透
      vec3 rd = refract(-V, N, 1.0 / 1.33);
      float trans = TRANS_MAX * (1.0 - fres) * (1.0 - foam) * exp(-underwaterPath(p, rd) / TRANS_LEN);
      // 混合方式：结果 = src.rgb + dst·src.a（见 buildWater 的 CustomBlending）
      trans = clamp(trans, 0.0, TRANS_MAX);
      col = clamp(col, 0.0, 1e3);
      // 最后一道保护：任何一项算坏了就退回不透明的本色（NaN 进了 bloom 会把整帧染黑）
      if (nonFinite3(col) || nonFinite(trans)) { col = uDeep * 0.5; trans = 0.0; }
      gl_FragColor = vec4(col * (1.0 - trans), trans);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`,
};

// 河埠头踏步面近似：terrain.js 的 STEP（6 级，从 y=0 下到 -1.7）。u = 离岸距离，
// 踏步面 y ≈ -r/2 - (r/t)·u（r 每级高，t 每级深），换算到以水面为 0 的高度
const STEP_BOTTOM = -1.7; const STEP_COUNT = 6;
function stepPlane(st, waterY) {
  const r = -STEP_BOTTOM / STEP_COUNT; const t = st.depth / STEP_COUNT;
  const dirs = { S: [0, -1], N: [0, 1], BW: [1, 0], BE: [-1, 0] };
  const [nx, nz] = dirs[st.bank];
  const cx = (st.rect.x0 + st.rect.x1) / 2; const cz = (st.rect.z0 + st.rect.z1) / 2;
  // 岸线中点 = 踏步矩形中心往岸里退半个伸出长度
  const ox = cx - nx * st.depth / 2; const oz = cz - nz * st.depth / 2;
  return {
    a: new THREE.Vector4(ox, oz, nx, nz),
    b: new THREE.Vector4(st.width / 2, st.depth, r / t, -r / 2 - waterY),
  };
}

function buildWater(ctx) {
  const { layout, renderer, geom } = ctx;
  const [main, branch] = ['main', 'branch'].map((id) => layout.rivers.find((r) => r.id === id).rect);
  const pad = 0.6; // 伸到驳岸下面，免得接缝漏底
  // 十字形水面（局部 XY 平面，转到水平后 世界 z = -局部 y）
  const rects = [
    { x0: main.x0, x1: main.x1, z0: main.z0 - pad, z1: main.z1 + pad },
    { x0: branch.x0 - pad, x1: branch.x1 + pad, z0: branch.z0, z1: main.z0 - pad },
    { x0: branch.x0 - pad, x1: branch.x1 + pad, z0: main.z1 + pad, z1: branch.z1 },
  ];
  const g = mergeGeometries(rects.map((r) => geom.place(geom.planeM(r.x1 - r.x0, r.z1 - r.z0),
    { x: (r.x0 + r.x1) / 2, y: -(r.z0 + r.z1) / 2 })));
  const size = renderer.getDrawingBufferSize(new THREE.Vector2());
  const water = new Reflector(g, {
    shader: WaterShader,
    textureWidth: Math.round(size.x / 2),
    textureHeight: Math.round(size.y / 2),
    multisample: 4,
  });
  water.rotation.x = -Math.PI / 2;
  water.position.y = layout.LEVELS.water;
  water.material.fog = true;
  // 半透明：结果 = src.rgb + dst·src.a，透出去的部分在 shader 里按水中路径长度衰减
  Object.assign(water.material, {
    transparent: true, blending: THREE.CustomBlending, blendEquation: THREE.AddEquation,
    blendSrc: THREE.OneFactor, blendDst: THREE.SrcAlphaFactor,
    blendSrcAlpha: THREE.ZeroFactor, blendDstAlpha: THREE.OneFactor,
  });
  water.renderOrder = -1; // 在其他半透明物（水珠）之前画
  const u = water.material.uniforms;
  u.uShallow.value.set(WATER.shallow);
  u.uDeep.value.set(WATER.deep);
  u.uHalf.value.set((main.z1 - main.z0) / 2, (branch.x1 - branch.x0) / 2);
  u.uDepth = { value: layout.LEVELS.water - layout.LEVELS.bed };
  if (layout.waterSteps.length !== NSTEPS) throw new Error(`waterSteps 有 ${layout.waterSteps.length} 条，shader 按 ${NSTEPS} 条写的`);
  const steps = layout.waterSteps.map((st) => stepPlane(st, layout.LEVELS.water));
  u.uStepA = { value: steps.map((v) => v.a) };
  u.uStepB = { value: steps.map((v) => v.b) };
  u.uBoat = { value: [0, 1, 2].map(() => new THREE.Vector4(1e4, 1e4, 1, 0)) };
  u.uBoatSize = { value: [0, 1, 2].map(() => new THREE.Vector2(7, 1.6)) };
  u.uOar = { value: [0, 1, 2].map(() => new THREE.Vector3(1e4, 1e4, 0)) };
  u.uRing = { value: Array.from({ length: 3 * RINGS_PER_BOAT }, () => new THREE.Vector4(1e4, 1e4, -1, 0)) };
  // 正交俯视（对位图）不做反射：Reflector 的斜裁剪只适用于透视相机
  const reflect = water.onBeforeRender;
  water.onBeforeRender = (r, s, cam, ...rest) => {
    u.uReflect.value = cam.isOrthographicCamera ? 0 : 1;
    if (!cam.isOrthographicCamera) reflect(r, s, cam, ...rest);
  };
  return water;
}

// ---------------------------------------------------------------- 船

function weaveTexture(rng) {
  // 乌篷竹篾编织：2.5cm 宽的篾片人字斜纹，乌黑带一点桐油光。覆盖 0.4m × 0.4m
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const x = c.getContext('2d');
  const r = rng('water-weave');
  x.fillStyle = '#0d0a08';
  x.fillRect(0, 0, 256, 256);
  const n = 16; const s = 256 / n;
  for (let j = 0; j < n; j++) {
    for (let i = 0; i < n; i++) {
      const over = (i + j) % 4 < 2; // 斜纹：两上两下
      const v = r.range(-6, 6);
      const base = over ? [30, 27, 23] : [19, 17, 15];
      const gr = over ? x.createLinearGradient(i * s, 0, i * s + s, 0) : x.createLinearGradient(0, j * s, 0, j * s + s);
      gr.addColorStop(0, `rgb(${base[0] + v - 8},${base[1] + v - 7},${base[2] + v - 6})`);
      gr.addColorStop(0.5, `rgb(${base[0] + v + 10},${base[1] + v + 8},${base[2] + v + 6})`);
      gr.addColorStop(1, `rgb(${base[0] + v - 8},${base[1] + v - 7},${base[2] + v - 6})`);
      x.fillStyle = gr;
      x.fillRect(i * s + 0.5, j * s + 0.5, s - 1, s - 1);
    }
  }
  for (let k = 0; k < 900; k++) { // 篾面细纹与积灰
    x.globalAlpha = r.range(0.05, 0.25);
    x.fillStyle = r.pick(['#000000', '#4a3d30', '#2b241d']);
    x.fillRect(r.range(0, 256), r.range(0, 256), r.range(1, 6), 1);
  }
  x.globalAlpha = 1;
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1 / 0.4, 1 / 0.4);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}

// 船体型线：s=0 船尾，s=1 船头。两头收窄、起翘、船底抬出水面
function hullStation(s, L, B) {
  const e = Math.abs(2 * s - 1);
  const bow = s > 0.5;
  return {
    x: (s - 0.5) * L,
    hw: (B / 2) * (1 - (bow ? 0.74 : 0.62) * e ** 2.4),
    ys: 0.36 + (bow ? 0.34 : 0.28) * e ** 2.5,
    yk: -0.24 + (bow ? 0.44 : 0.4) * e ** 3,
  };
}
const HULL_POW = 2.2;
const sectionY = (st, u) => st.yk + (st.ys - st.yk) * Math.abs(u) ** HULL_POW;
const halfWidthAt = (st, y) => st.hw * Math.min(1, Math.max(0, (y - st.yk) / (st.ys - st.yk)) ** (1 / HULL_POW));

function hullGeometry(L, B) {
  const NS = 40; const NU = 16;
  const pos = []; const uv = []; const idx = [];
  for (let i = 0; i <= NS; i++) {
    const st = hullStation(i / NS, L, B);
    let girth = 0; let prev = null;
    const row = [];
    for (let j = 0; j <= NU; j++) {
      const u = -1 + (2 * j) / NU;
      const pt = [st.x, sectionY(st, u), st.hw * u];
      if (prev) girth += Math.hypot(pt[1] - prev[1], pt[2] - prev[2]);
      prev = pt; row.push([pt, girth]);
    }
    for (const [pt, gi] of row) { pos.push(...pt); uv.push(gi - girth / 2, st.x); }
  }
  const W = NU + 1;
  for (let i = 0; i < NS; i++) {
    for (let j = 0; j < NU; j++) {
      const a = i * W + j; const b = a + W; const c = a + 1; const d = b + 1;
      idx.push(a, b, c, b, d, c);
    }
  }
  const outer = new THREE.BufferGeometry();
  outer.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  outer.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  outer.setIndex(idx);
  outer.computeVertexNormals();
  const inner = outer.clone();
  const rev = [];
  for (let k = 0; k < idx.length; k += 3) rev.push(idx[k], idx[k + 2], idx[k + 1]);
  inner.setIndex(rev);
  const n = inner.attributes.normal;
  for (let k = 0; k < n.count; k++) n.setXYZ(k, -n.getX(k), -n.getY(k), -n.getZ(k));
  return [outer, inner, transom(0, L, B), transom(1, L, B)];
}

// 船头/船尾的封板（两面）
function transom(s, L, B) {
  const st = hullStation(s, L, B);
  const pts = [];
  for (let j = 0; j <= 16; j++) { const u = -1 + j / 8; pts.push([st.x, sectionY(st, u), st.hw * u]); }
  const pos = []; const uv = [];
  for (let j = 0; j < pts.length - 1; j++) {
    for (const p of [pts[j], pts[j + 1], [st.x, st.ys, 0], pts[j + 1], pts[j], [st.x, st.ys, 0]]) {
      pos.push(...p); uv.push(p[2], p[1]);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.computeVertexNormals();
  return g;
}

// 沿船长方向的一条水平板（甲板、舱底板），stations: [{x, y, hw}]，法线朝上
function deckStrip(stations) {
  const pos = []; const uv = []; const idx = [];
  stations.forEach(({ x, y, hw }, i) => {
    pos.push(x, y, -hw, x, y, hw);
    uv.push(-hw, x, hw, x);
    if (i > 0) { const L0 = (i - 1) * 2; const L1 = i * 2; idx.push(L0, L0 + 1, L1, L0 + 1, L1 + 1, L1); }
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

function stationsBetween(s0, s1, n, L, B, yOf) {
  return Array.from({ length: n + 1 }, (_, i) => {
    const st = hullStation(s0 + ((s1 - s0) * i) / n, L, B);
    const y = yOf(st);
    return { x: st.x, y, hw: halfWidthAt(st, y) };
  });
}

function tubeAlong(points, r, seg = 48) {
  return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p))), seg, r, 6, false);
}

// 拱形篷：沿 X 从 x0 到 x1，椭圆拱 半宽 rz、拱高 ry，起拱高度 y0
function archShell(x0, x1, y0, rz, ry) {
  const N = 28; const pos = []; const uv = []; const idx = [];
  let arc = 0;
  for (let k = 0; k <= N; k++) {
    const f = (Math.PI * k) / N;
    const y = y0 + ry * Math.sin(f); const z = rz * Math.cos(f);
    if (k > 0) { const fp = (Math.PI * (k - 1)) / N; arc += Math.hypot(y - (y0 + ry * Math.sin(fp)), z - rz * Math.cos(fp)); }
    pos.push(x0, y, z, x1, y, z);
    uv.push(arc, x0, arc, x1);
    if (k > 0) { const a = (k - 1) * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

const archPoints = (x, y0, rz, ry) => Array.from({ length: 17 }, (_, k) => {
  const f = (Math.PI * k) / 16;
  return [x, y0 + ry * Math.sin(f), rz * Math.cos(f)];
});

function buildBoatStatic(rec, ctx, canopyMat) {
  const { materials: M, geom } = ctx;
  const L = rec.length; const B = rec.beam;
  const parts = [];
  const add = (g, mat) => parts.push({ geom: g, mat });
  for (const g of hullGeometry(L, B)) add(g, M.wood);

  // 船舷护木（上沿一道粗的，下面一道细的腰箍）
  for (const side of [-1, 1]) {
    const top = []; const wale = [];
    for (let i = 0; i <= 30; i++) {
      const st = hullStation(i / 30, L, B);
      top.push([st.x, st.ys + 0.01, side * (st.hw + 0.012)]);
      const y = st.ys - 0.14;
      wale.push([st.x, y, side * (halfWidthAt(st, y) + 0.018)]);
    }
    add(tubeAlong(top, 0.036), M.woodDark);
    add(tubeAlong(wale, 0.022), M.woodDark);
  }
  // 舱底板、船头甲板、船尾甲板（摇橹人站的地方）
  add(deckStrip(stationsBetween(0.16, 0.85, 20, L, B, () => 0.02)), M.wood);
  add(deckStrip(stationsBetween(0.85, 1.0, 8, L, B, (st) => st.ys - 0.05)), M.wood);
  add(deckStrip(stationsBetween(0.0, 0.17, 8, L, B, (st) => st.ys - 0.05)), M.wood);
  for (const s of [0.17, 0.85]) { // 甲板前沿横梁
    const st = hullStation(s, L, B);
    add(geom.place(geom.boxM(0.08, 0.1, st.hw * 2 - 0.02), { x: st.x, y: st.ys - 0.08 }), M.woodDark);
  }

  // 乌篷：两节，后节略大套在前节外面；顶高控制在 CANOPY_MAX 以内
  const mid = hullStation(0.5, L, B);
  const y0 = mid.ys + 0.03;
  const ry = Math.min(0.88, CANOPY_MAX - 0.18 - y0);
  const secs = [
    { x0: -0.17 * L, x1: 0.02 * L, rz: mid.hw + 0.05, ry: ry + 0.04 },
    { x0: 0.0, x1: 0.13 * L, rz: mid.hw + 0.01, ry },
  ];
  for (const c of secs) {
    add(archShell(c.x0, c.x1, y0, c.rz, c.ry), canopyMat);
    for (const x of [c.x0 + 0.03, (c.x0 + c.x1) / 2, c.x1 - 0.03]) add(tubeAlong(archPoints(x, y0, c.rz + 0.012, c.ry + 0.012), 0.022, 24), M.woodDark);
    for (const side of [-1, 1]) add(geom.place(geom.boxM(c.x1 - c.x0, 0.05, 0.04), { x: (c.x0 + c.x1) / 2, y: y0, z: side * c.rz }), M.woodDark);
  }
  for (const x of [-0.12 * L, 0.06 * L]) { // 舱里两条坐板
    add(geom.place(geom.boxM(0.3, 0.04, mid.hw * 1.7), { x, y: 0.26 }), M.wood);
    add(geom.place(geom.boxM(0.05, 0.24, mid.hw * 1.5), { x, y: 0.13 }), M.woodDark);
  }

  // 船尾橹人头（支橹的木桩）
  const sp = hullStation(0.07, L, B);
  const pivot = { x: sp.x, y: sp.ys + 0.12 };
  add(geom.place(new THREE.CylinderGeometry(0.035, 0.05, 0.16, 8), { x: pivot.x, y: pivot.y - 0.08 }), M.woodDark);
  add(geom.place(geom.boxM(0.3, 0.08, 0.3), { x: pivot.x, y: sp.ys - 0.03 }), M.woodDark);
  const ropeAnchor = new THREE.Vector3(pivot.x + 1.0, hullStation(0.07 + 1.0 / L, L, B).ys - 0.04, 0);
  add(geom.place(geom.boxM(0.06, 0.05, 0.06), { x: ropeAnchor.x, y: ropeAnchor.y }), M.woodDark);

  const mesh = geom.mergeByMaterial(parts, { castShadow: false, receiveShadow: true });
  return { mesh, pivot, ropeAnchor, canopyTop: y0 + ry + 0.04 + 0.034 };
}

// 橹：在支点坐标系里，橹柄一段向前上翘（不翻转），橹叶一段向后下斜，可绕自身轴翻转
function buildOar(ctx) {
  const { materials: M, geom } = ctx;
  const pivot = new THREE.Group();
  const loomParts = [];
  const cl = Math.cos(LOOM_TILT); const sl = Math.sin(LOOM_TILT);
  loomParts.push({ geom: geom.place(new THREE.CylinderGeometry(0.026, 0.034, LOOM_LEN, 8), { x: cl * LOOM_LEN / 2, y: sl * LOOM_LEN / 2, rz: -Math.PI / 2 + LOOM_TILT }), mat: M.wood });
  loomParts.push({ geom: geom.place(new THREE.CylinderGeometry(0.02, 0.02, 0.26, 8), { x: cl * LOOM_LEN, y: sl * LOOM_LEN, rx: Math.PI / 2 }), mat: M.woodDark });
  loomParts.push({ geom: geom.place(new THREE.SphereGeometry(0.06, 10, 8), { y: 0.0 }), mat: M.woodDark }); // 橹脐
  pivot.add(geom.mergeByMaterial(loomParts, { castShadow: false }));

  const tilt = new THREE.Group();
  tilt.rotation.z = BLADE_TILT; // 局部 -X 向下倾
  const twist = new THREE.Group();
  // 杆一直通到橹叶末端当脊，橹叶是贴在脊上的薄板
  const shaft = geom.place(new THREE.CylinderGeometry(0.016, 0.038, BLADE_LEN - 0.05, 10), { x: -(BLADE_LEN - 0.05) / 2, rz: Math.PI / 2 });
  // 橹叶：扁长木板，靠杆一端窄，末端宽 0.19m
  const blade = geom.boxM(BLADE_LEN - 1.65, 0.016, 0.2);
  const bp = blade.attributes.position;
  for (let k = 0; k < bp.count; k++) {
    const f = bp.getX(k) / (BLADE_LEN - 1.65) + 0.5; // 0 = 末端, 1 = 靠杆
    bp.setZ(k, bp.getZ(k) * (1 - 0.8 * f));
      }
  blade.computeVertexNormals();
  geom.place(blade, { x: -(1.65 + BLADE_LEN) / 2 });
  twist.add(geom.mergeByMaterial([{ geom: shaft, mat: M.wood }, { geom: blade, mat: M.wood }], { castShadow: false }));
  tilt.add(twist);
  pivot.add(tilt);
  return { pivot, twist };
}

function buildBoat(rec, ctx, canopyMat) {
  const st = { rec, paths: ctx.paths, waterY: ctx.layout.LEVELS.water };
  const r = ctx.rng(`water-${rec.id}`);
  st.ph = [r.range(0, TAU), r.range(0, TAU), r.range(0, TAU), r.range(0, TAU), r.range(0, STROKE)];
  const group = new THREE.Group();
  group.name = rec.id;
  const s = buildBoatStatic(rec, ctx, canopyMat);
  group.add(s.mesh);
  if (s.canopyTop > CANOPY_MAX) throw new Error(`${rec.id} 船篷高 ${s.canopyTop.toFixed(2)}m 超过 ${CANOPY_MAX}m`);
  st.pivot = s.pivot; st.ropeAnchor = s.ropeAnchor;
  const oar = buildOar(ctx);
  oar.pivot.position.set(s.pivot.x, s.pivot.y, 0);
  group.add(oar.pivot);
  st.oarPivot = oar.pivot; st.twist = oar.twist;
  // 橹绳：从橹柄拉到船尾甲板
  const rope = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 1, 5), ctx.materials.woodDark);
  group.add(rope);
  st.rope = rope;
  st.group = group;
  // 水花参数表：每槽一次换向的 DROPS_PER_BURST 颗水珠
  const sr = ctx.rng(`water-${rec.id}-splash`);
  st.splash = Array.from({ length: SPLASH_SLOTS }, () => Array.from({ length: DROPS_PER_BURST }, () => ({
    delay: sr.range(0, 0.45) ** 1.5 / 0.45 ** 0.5,
    ox: sr.range(-0.25, 0.1), oz: sr.range(-0.08, 0.08),
    vx: sr.range(-0.5, 0.25), vy: sr.range(0.45, 1.5), vz: sr.range(0.1, 0.9),
    r: sr.range(0.0025, 0.008) * (sr.chance(0.15) ? 1.8 : 1),
  })));
  return st;
}

// ---------------------------------------------------------------- build / update

export function build(ctx) {
  const { layout } = ctx;
  const root = new THREE.Group();
  const water = buildWater(ctx);
  root.add(water);

  const canopyMat = new THREE.MeshStandardMaterial({ name: 'boatCanopy', map: weaveTexture(ctx.rng), roughness: 0.62, side: THREE.DoubleSide });
  const boats = layout.boats.map((rec) => buildBoat(rec, ctx, canopyMat));
  boats.forEach((b) => root.add(b.group));

  const dropMat = new THREE.MeshStandardMaterial({
    name: 'splash', color: 0xdfe6e3, roughness: 0.08, transparent: true, opacity: 0.6, depthWrite: false,
  });
  const drops = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), dropMat, boats.length * BURSTS * DROPS_PER_BURST);
  drops.frustumCulled = false;
  drops.castShadow = false;
  root.add(drops);

  const u = water.material.uniforms;
  boats.forEach((b, i) => u.uBoatSize.value[i].set(b.rec.length, b.rec.beam));
  // 太阳光由 lighting.js 按 t 设好（先于各区块 update），这里只读它的颜色和强度给水面高光用
  let sun = null; let hemi = null;
  ctx.scene.traverse((o) => {
    if (o.isDirectionalLight && !sun) sun = o;
    if (o.isHemisphereLight && !hemi) hemi = o;
  });
  state = { boats, drops, u, sun, hemi, waterY: layout.LEVELS.water };
  update(0);
  return root;
}

const _v = new THREE.Vector3();
const _a = new THREE.Vector3();
const _b = new THREE.Vector3();
const _yUp = new THREE.Vector3(0, 1, 0);
const _dm = new THREE.Matrix4();

function updateBoat(st, i, t, u) {
  const now = oarEntry(st, t);
  const pose = now.pose;
  st.group.position.set(pose.x, pose.y, pose.z);
  st.group.rotation.set(pose.roll, pose.rotY, pose.pitch, 'YZX');
  st.oarPivot.rotation.y = pose.yaw;
  st.twist.rotation.x = pose.twist;

  // 橹绳：橹柄末端（船体坐标）→ 甲板绳桩
  const cl = Math.cos(LOOM_TILT) * LOOM_LEN * 0.92;
  _a.set(st.pivot.x + cl * Math.cos(pose.yaw), st.pivot.y + Math.sin(LOOM_TILT) * LOOM_LEN * 0.92, -cl * Math.sin(pose.yaw));
  _b.copy(st.ropeAnchor);
  _v.subVectors(_a, _b);
  st.rope.position.addVectors(_a, _b).multiplyScalar(0.5);
  st.rope.scale.set(1, _v.length(), 1);
  st.rope.quaternion.setFromUnitVectors(_yUp, _v.normalize());

  u.uBoat.value[i].set(pose.x, pose.z, pose.dir[0], pose.dir[1]);
  u.uOar.value[i].set(now.x, now.z, 1);
  const k0 = lastReversal(st, t);
  for (let j = 0; j < RINGS_PER_BOAT; j++) {
    const te = reversalTime(st, k0 - j);
    const c = oarEntry(st, te);
    u.uRing.value[i * RINGS_PER_BOAT + j].set(c.x, c.z, t - te, 0.009);
  }
  return k0;
}

// 换向时橹叶带起的水珠：抛物线，落回水面就消失
function updateSplash(st, t, k0, drops, cursor, waterY) {
  const speed = st.rec.speed;
  let n = cursor;
  for (let j = 0; j < BURSTS; j++) {
    const k = k0 - j;
    const te = reversalTime(st, k);
    const side = ((k % 2) + 2) % 2 === 0 ? 1 : -1;
    const table = st.splash[((k % SPLASH_SLOTS) + SPLASH_SLOTS) % SPLASH_SLOTS];
    for (const d of table) {
      const a = t - te - d.delay;
      _dm.makeScale(0, 0, 0);
      if (a >= 0) {
        const e = oarEntry(st, te + d.delay);
        const c = Math.cos(e.pose.rotY); const sn = Math.sin(e.pose.rotY);
        // 船体局部 (x,z) → 世界：x 轴 (c, -sn)，z 轴 (sn, c)
        const lx = d.ox; const lz = side * d.oz;
        const vx = d.vx + speed; const vz = side * d.vz;
        _v.set(
          e.x + c * lx + sn * lz + (c * vx + sn * vz) * a,
          waterY + 0.01 + d.vy * a - 0.5 * GRAVITY * a * a,
          e.z - sn * lx + c * lz + (-sn * vx + c * vz) * a,
        );
        if (_v.y > waterY - 0.004) {
          // 水珠沿速度方向拉长，越飞越小
          _b.set(c * vx + sn * vz, d.vy - GRAVITY * a, -sn * vx + c * vz);
          const sp = _b.length();
          const r = d.r * (1 - 0.35 * Math.min(1, a / 0.3));
          _q.setFromUnitVectors(_yUp, _b.normalize());
          _dm.compose(_v, _q, _a.set(r, r * (1 + 0.9 * sp), r));
        }
      }
      drops.setMatrixAt(n++, _dm);
    }
  }
  return n;
}

export function update(t) {
  if (!state) return;
  const { boats, drops, u, sun, hemi, waterY } = state;
  u.uTime.value = t;
  const dir = sunDirection(t);
  u.uSunDir.value.copy(dir);
  // 浑水本色跟着水平面受光走：天光 + 太阳×sin(高度角)，t=0 时归一到 1
  if (sun && hemi) {
    u.uSunCol.value.copy(sun.color).multiplyScalar(sun.intensity);
    u.uLight.value = (hemi.intensity + sun.intensity * Math.max(0, dir.y)) / LIGHT_REF;
  }
  let cursor = 0;
  boats.forEach((st, i) => {
    const k0 = updateBoat(st, i, t, u);
    cursor = updateSplash(st, t, k0, drops, cursor, waterY);
  });
  drops.instanceMatrix.needsUpdate = true;
}
