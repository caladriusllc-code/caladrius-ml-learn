<template>
  <section class="mlp-loss" aria-label="Dernière couche cachée, couche de sortie et mesure de l'erreur">
    <svg
      class="diagram"
      viewBox="0 0 880 560"
      role="img"
      aria-label="Seize neurones de la dernière couche cachée envoient leur signal vers dix neurones de sortie. Chaque sortie est comparée à l'étiquette réelle dans une couche de mesure d'erreur, et la perte totale monte dans une jauge."
    >
      <defs>
        <filter id="ml-glow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <!-- Connexions au repos -->
      <g class="wires">
        <path v-for="(e, k) in WIRES" :key="'w' + k" :d="e.d" :stroke-opacity="e.o" />
      </g>

      <!-- Connexions illuminées (cyan = contribution positive, orange = négative) -->
      <g class="overlays">
        <path
          v-for="(o, k) in active.ov" :key="'ov' + k"
          :d="o.d" pathLength="1" stroke-dasharray="1 1"
          :stroke-dashoffset="1 - o.prog"
          :stroke="o.c" :stroke-width="o.w"
          :opacity="o.prog < 0.005 ? 0 : o.op"
        />
      </g>

      <!-- Impulsions -->
      <g class="particles">
        <circle v-for="(p, i) in active.pu" :key="'pu' + i" :cx="p.x" :cy="p.y" :r="p.r" :fill="p.c" />
      </g>

      <!-- Dernière couche cachée (16) et sortie (10) -->
      <g v-for="n in NODES" :key="'n' + n.l + '-' + n.k">
        <circle
          v-if="flash[n.l - 1] > 0.02"
          class="flash" :cx="n.x" :cy="n.y" :r="n.r + 2 + flash[n.l - 1] * 9"
          :opacity="flash[n.l - 1] * 0.9" filter="url(#ml-glow)"
        />
        <circle
          class="ring" :cx="n.x" :cy="n.y" :r="n.r + 2.5"
          :stroke="val(n) < -0.02 ? NEG : '#fff'"
          :stroke-dasharray="val(n) < -0.02 ? '3 3' : null"
        />
        <circle class="core" :cx="n.x" :cy="n.y" :r="n.r" />
        <circle
          :cx="n.x" :cy="n.y" :r="n.r" fill="#fff"
          :fill-opacity="clamp(Math.abs(val(n))) * 0.95"
        />
        <text
          class="node-text" :class="{ small: n.l === 1 }"
          :x="n.x" :y="n.y + (n.l === 1 ? 3.2 : 3.6)"
          :style="{ fill: Math.abs(val(n)) > 0.6 ? '#050505' : '#fff' }"
        >{{ fr(val(n), n.l === 1 ? 1 : 2) }}</text>
      </g>

      <!-- Probabilités de sortie -->
      <g v-for="k in IDX" :key="'bar' + k">
        <rect class="bar-bg" :x="BAR.x" :y="outY(k) - 5" :width="BAR.w" height="10" rx="5" />
        <rect
          class="bar" :x="BAR.x" :y="outY(k) - 5"
          :width="Math.max(0, BAR.w * actsShown[1][k])" height="10" rx="5"
          :filter="k === win && winOp > 0.1 ? 'url(#ml-glow)' : null"
        />
      </g>

      <!-- Classe prédite -->
      <g :opacity="winOp">
        <circle class="halo" :cx="X.o" :cy="outY(win)" r="26" />
        <circle class="winner" :cx="X.o" :cy="outY(win)" r="22" filter="url(#ml-glow)" />
      </g>

      <!-- Couche de mesure d'erreur : anneau épais = étiquette réelle, remplissage = −log ŷ -->
      <g :opacity="0.4 + 0.6 * errOp">
        <g v-for="k in IDX" :key="'err' + k">
          <circle
            v-if="flash[2] > 0.02 && k === label"
            class="flash" :cx="X.e" :cy="outY(k)" :r="16 + flash[2] * 9"
            :opacity="flash[2] * 0.9" filter="url(#ml-glow)"
          />
          <circle
            v-if="k === label" class="target" :cx="X.e" :cy="outY(k)" r="19"
            :opacity="errOp"
          />
          <circle class="core" :cx="X.e" :cy="outY(k)" r="14" />
          <circle
            :cx="X.e" :cy="outY(k)" r="14" fill="#fff"
            :fill-opacity="k === label ? errOp * 0.95 : 0"
          />
          <text
            class="node-text" :x="X.e" :y="outY(k) + 4"
            :style="{ fill: k === label && errOp > 0.5 ? '#050505' : '#fff' }"
          >{{ k === label && errOp > 0.5 ? 1 : 0 }}</text>
        </g>
      </g>

      <!-- Perte totale : jauge de 0 (haut vide) à ln 10 (réponse uniforme, jauge pleine) -->
      <g>
        <line
          class="link" :x1="X.e + 22" :x2="GAUGE.x" :y1="outY(label)" :y2="outY(label)"
          :opacity="gaugeP"
        />
        <rect class="gauge-bg" :x="GAUGE.x" :y="GAUGE.y" :width="GAUGE.w" :height="GAUGE.h" rx="4" />
        <rect
          class="gauge" :x="GAUGE.x" :width="GAUGE.w" rx="4"
          :y="GAUGE.y + GAUGE.h - gaugeH" :height="gaugeH"
          :filter="gaugeH > 2 ? 'url(#ml-glow)' : null"
        />
      </g>
    </svg>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* =====================================================================
   1. Les dix images (28 × 28) : elles servent uniquement à produire des
      activations réalistes dans la dernière couche cachée.
   ===================================================================== */
const PI = Math.PI
const arc = (cx, cy, rx, ry, a0, a1, n = 32) =>
  Array.from({ length: n + 1 }, (_, i) => {
    const a = a0 + ((a1 - a0) * i) / n
    return [cx + rx * Math.cos(a), cy + ry * Math.sin(a)]
  })

const STROKES = [
  [arc(14, 14, 6.5, 10, 0, 2 * PI, 40)],
  [[[11, 8], [15, 4], [15, 24]]],
  [arc(14, 9.5, 6, 5.5, PI, 2 * PI + 0.6), [[19, 12.6], [7.5, 24], [21, 24]]],
  [arc(14, 9, 5.5, 5, PI + 0.6, 2.5 * PI), arc(14, 18.5, 6, 5.5, 1.5 * PI, 2.5 * PI + 0.9)],
  [[[17, 24], [17, 4], [6, 17], [22, 17]]],
  [[[20, 5], [9, 5], [8, 13], [10.2, 12.2]], arc(14, 17.5, 6.5, 6.5, -2.2, 2.7)],
  [[[19, 5], [13, 7], [9, 13], [8, 18.5]], arc(14, 18.5, 6, 5.5, 0, 2 * PI, 36)],
  [[[7, 5], [21, 5], [12, 24]]],
  [arc(14, 9, 5, 4.5, 0, 2 * PI), arc(14, 18.5, 6, 5.5, 0, 2 * PI, 36)],
  [arc(14, 10, 6, 5.5, 0, 2 * PI), [[20, 10], [18, 17], [12, 24]]],
]

function segDist(px, py, a, b) {
  const dx = b[0] - a[0]
  const dy = b[1] - a[1]
  const len2 = dx * dx + dy * dy || 1
  const u = Math.max(0, Math.min(1, ((px - a[0]) * dx + (py - a[1]) * dy) / len2))
  return Math.hypot(px - a[0] - u * dx, py - a[1] - u * dy)
}

function renderDigit(strokes) {
  const segs = []
  strokes.forEach((p) => { for (let i = 0; i < p.length - 1; i++) segs.push([p[i], p[i + 1]]) })
  return Array.from({ length: 784 }, (_, idx) => {
    const x = (idx % 28) + 0.5
    const y = Math.floor(idx / 28) + 0.5
    let d = Infinity
    for (const [a, b] of segs) d = Math.min(d, segDist(x, y, a, b))
    return Math.max(0, Math.min(1, (1.9 - d) / 1.1))
  })
}

const IDX = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
const DIGITS = STROKES.map(renderDigit)

/* =====================================================================
   2. Réseau 784 → 16 → 16 → 10 : propagation avant réelle
      h¹ = tanh(W¹x)   h² = tanh(W²h¹)   ŷ = softmax(W³h² + b)
   W¹ et W² aléatoires (graine fixe) ; W³ est ajustée en forme close sur
   ces dix images pour que la bonne classe l'emporte.
   ===================================================================== */
function rng(seed) {
  return () => {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
const rand = rng(2024)
const W1 = Array.from({ length: 16 }, () => Array.from({ length: 784 }, () => (rand() * 2 - 1) * 0.25))
const W2 = Array.from({ length: 16 }, () => Array.from({ length: 16 }, () => rand() * 2 - 1))

const dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0)

function hidden(px) {
  const h1 = W1.map((row) => Math.tanh(dot(row, px)))
  const h2 = W2.map((row) => Math.tanh(dot(row, h1)))
  return { h1, h2 }
}

function solve(A, B) {
  const n = A.length
  const M = A.map((r, i) => [...r, ...B[i]])
  for (let c = 0; c < n; c++) {
    let p = c
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r
    ;[M[c], M[p]] = [M[p], M[c]]
    const pv = M[c][c]
    for (let k = c; k < M[c].length; k++) M[c][k] /= pv
    for (let r = 0; r < n; r++) {
      if (r === c) continue
      const f = M[r][c]
      if (!f) continue
      for (let k = c; k < M[r].length; k++) M[r][k] -= f * M[c][k]
    }
  }
  return M.map((r) => r.slice(n))
}

// Logit visé pour la bonne classe : 3 → probabilité ≈ 69 %, perte ≈ 0,37 (bien visible)
const TARGET_LOGIT = 3
const HM = DIGITS.map((px) => [...hidden(px).h2, 1])
const K = HM.map((a, i) => HM.map((b, j) => dot(a, b) + (i === j ? 1e-3 : 0)))
const TARGET = IDX.map((i) => IDX.map((j) => (i === j ? TARGET_LOGIT : 0)))
const ALPHA = solve(K, TARGET)
const W3 = Array.from({ length: 17 }, (_, i) =>
  Array.from({ length: 10 }, (_, j) => HM.reduce((s, row, n) => s + row[i] * ALPHA[n][j], 0))
)

function forward(px) {
  const { h2 } = hidden(px)
  const z = IDX.map((j) => h2.reduce((s, h, i) => s + h * W3[i][j], W3[16][j]))
  const m = Math.max(...z)
  const e = z.map((v) => Math.exp(v - m))
  const s = e.reduce((a, v) => a + v, 0)
  return { h2, y: e.map((v) => v / s) }
}
const NET = DIGITS.map(forward)

// Entropie croisée : L = −log(ŷ_étiquette), l'étiquette de l'exemple k est k
const LN10 = Math.log(10)
const LOSSES = NET.map((n, k) => -Math.log(n.y[k]))

/* =====================================================================
   3. Géométrie
   ===================================================================== */
const X = { h: 130, o: 430, e: 690 }
const BAR = { x: 462, w: 100 }
const GAUGE = { x: 810, y: 88, w: 28, h: 424 }
const CY = 300
const yHid = (k) => CY + (k - 7.5) * 27.5
const outY = (k) => CY + (k - 4.5) * 44

const NODES = [
  ...Array.from({ length: 16 }, (_, k) => ({ l: 1, k, x: X.h, y: yHid(k), r: 10.5 })),
  ...IDX.map((k) => ({ l: 2, k, x: X.o, y: outY(k), r: 14 })),
]

// Couche 0 : h² (16) → sortie (10). Couche 1 : sortie k → mesure d'erreur k.
const E0 = []
for (let j = 0; j < 10; j++) {
  for (let s = 0; s < 16; s++) {
    const x1 = X.h + 12
    const x2 = X.o - 14 - 2
    const y1 = yHid(s)
    const y2 = outY(j)
    const xm = (x1 + x2) / 2
    E0.push({
      s, j,
      pts: [[x1, y1], [xm, y1], [xm, y2], [x2, y2]],
      d: `M ${x1} ${y1} C ${xm} ${y1}, ${xm} ${y2}, ${x2} ${y2}`,
    })
  }
}
const E1 = IDX.map((k) => {
  const x1 = BAR.x + BAR.w + 8
  const x2 = X.e - 22
  const y = outY(k)
  const third = (x2 - x1) / 3
  return {
    s: k, j: k, o: 0.22,
    pts: [[x1, y], [x1 + third, y], [x1 + 2 * third, y], [x2, y]],
    d: `M ${x1} ${y} L ${x2} ${y}`,
  }
})
const EDGES = [E0, E1]

// Opacité au repos de la couche 0 : proportionnelle à |W3|
{
  const raw = E0.map((e) => Math.abs(W3[e.s][e.j]))
  const m = Math.max(...raw)
  E0.forEach((e, n) => { e.o = Number((0.05 + 0.2 * (raw[n] / m)).toFixed(3)) })
}
const WIRES = [...E0, ...E1]

// Contribution de chaque connexion, normalisée dans [−1, 1]
const CONTR = NET.map(({ h2, y }) => {
  const a = new Array(160)
  for (let j = 0; j < 10; j++) for (let i = 0; i < 16; i++) a[j * 16 + i] = h2[i] * W3[i][j]
  const m0 = Math.max(...a.map(Math.abs)) || 1
  const m1 = Math.max(...y) || 1
  return [a.map((v) => v / m0), y.map((v) => v / m1)]
})

/* =====================================================================
   4. Outils
   ===================================================================== */
const POS = '#67e8f9'
const NEG = '#fb923c'
const clamp = (v) => Math.min(1, Math.max(0, v))
const ease = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2)

function bez(pts, u) {
  const m = 1 - u
  const [p0, p1, p2, p3] = pts
  return [
    m * m * m * p0[0] + 3 * m * m * u * p1[0] + 3 * m * u * u * p2[0] + u * u * u * p3[0],
    m * m * m * p0[1] + 3 * m * m * u * p1[1] + 3 * m * u * u * p2[1] + u * u * u * p3[1],
  ]
}

// Nombre au format français (virgule, vrai signe moins)
const fr = (n, d) => {
  const v = Math.abs(n) < 0.5 * Math.pow(10, -d) ? 0 : n
  const s = Math.abs(v).toFixed(d).replace('.', ',')
  return v < 0 ? '\u2212' + s : s
}

/* =====================================================================
   5. Horloge : un exemple toutes les DUR ms, en boucle
   ===================================================================== */
const DUR = 6200
const TOTAL = DUR * 10
const stepIdx = ref(0)
const t = ref(0)
let raf = 0
let t0 = 0

function frame(ts) {
  if (!t0) t0 = ts
  const tau = (ts - t0) % TOTAL
  const k = Math.floor(tau / DUR)
  stepIdx.value = k
  t.value = tau - k * DUR
  raf = requestAnimationFrame(frame)
}

onMounted(() => {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) t.value = 5500 // image fixe : tout est calculé
  else raf = requestAnimationFrame(frame)
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* =====================================================================
   6. Chronologie d'un exemple (ms)
   ===================================================================== */
const S = [600, 3000]            // départ des impulsions : h² → sortie, sortie → erreur
const STAG = [26, 30]            // décalage entre sources
const DRAW = 650                 // durée d'une impulsion
const REV = [300, 1900, 3900]    // h² connue, sortie connue, erreur connue
const ACT_WIN = [[S[0], REV[1] + 750], [S[1], REV[2] + 750]]

const step = computed(() => NET[stepIdx.value])
const endFade = computed(() => 1 - clamp((t.value - (DUR - 300)) / 300))
const rev = computed(() => REV.map((r) => ease(clamp((t.value - r) / 300))))

// Valeurs affichées : h² (16) puis ŷ (10)
const actsShown = computed(() =>
  [step.value.h2, step.value.y].map((a, l) => a.map((v) => v * rev.value[l] * endFade.value))
)
const val = (n) => actsShown.value[n.l - 1][n.k]

const flash = computed(() =>
  REV.map((r) => clamp((t.value - r) / 200) * (1 - clamp((t.value - r - 200) / 500)))
)

/* Connexions illuminées et impulsions */
const active = computed(() => {
  const T = t.value
  const d = stepIdx.value
  const res = { ov: [], pu: [] }
  for (let l = 0; l < 2; l++) {
    if (T < ACT_WIN[l][0] || T > ACT_WIN[l][1]) continue
    const fade = 1 - clamp((T - REV[l + 1] - 200) / 500)
    const E = EDGES[l]
    const C = CONTR[d][l]
    for (let n = 0; n < E.length; n++) {
      const rel = l === 0 ? C[E[n].j * 16 + E[n].s] : C[E[n].s]
      const a = Math.abs(rel)
      if (a < 0.12) continue
      const e = E[n]
      const u = (T - S[l] - e.s * STAG[l]) / DRAW
      const prog = ease(clamp(u))
      const c = rel > 0 ? POS : NEG
      res.ov.push({ d: e.d, prog, w: 0.9 + 2.4 * a, op: fade * (0.3 + 0.7 * a), c })
      if (u > 0 && u < 1) {
        const [x, y] = bez(e.pts, prog)
        res.pu.push({ x, y, r: 1.6 + 2.4 * a, c })
      }
    }
  }
  return res
})

/* Classe prédite */
const win = computed(() => step.value.y.indexOf(Math.max(...step.value.y)))
const winOp = computed(() => clamp((t.value - 2300) / 300) * endFade.value)

/* Mesure d'erreur */
const label = computed(() => stepIdx.value)
const loss = computed(() => LOSSES[stepIdx.value])
const errOp = computed(() => rev.value[2] * endFade.value)
const gaugeP = computed(() => ease(clamp((t.value - 4000) / 700)) * endFade.value)
const gaugeH = computed(() => GAUGE.h * clamp(loss.value / LN10) * gaugeP.value)
</script>

<style scoped>
.mlp-loss {
  box-sizing: border-box;
  width: 100%;
  color: #fff;
  background: #050505;
  display: flex;
  justify-content: center;
  align-items: center;  
}

.diagram {
  display: flex;
  width: 100%;
  height: 100%;
}

/* Connexions */
.wires path {
  fill: none;
  stroke: #fff;
  stroke-width: 0.6;
}
.overlays path {
  fill: none;
  stroke-linecap: round;
}

/* Neurones */
.ring {
  fill: none;
  stroke-width: 1.2;
}
.core {
  fill: #050505;
  stroke: #fff;
  stroke-width: 1.4;
}
.flash {
  fill: none;
  stroke: #fff;
  stroke-width: 1.2;
}
.node-text {
  text-anchor: middle;
  font: italic 10px Georgia, 'Times New Roman', serif;
  pointer-events: none;
}
.node-text.small {
  font-size: 9px;
}

/* Sortie */
.bar-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.4);
  stroke-width: 1;
}
.bar {
  fill: #fff;
}
.winner {
  fill: none;
  stroke: #fff;
  stroke-width: 1.8;
}
.halo {
  fill: none;
  stroke: rgba(255, 255, 255, 0.3);
  stroke-width: 1;
  animation: halo 5s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: center;
}

/* Mesure d'erreur */
.target {
  fill: none;
  stroke: #fff;
  stroke-width: 2.4;
}
.link {
  stroke: #fff;
  stroke-width: 1.2;
}
.gauge-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.45);
  stroke-width: 1;
}
.gauge {
  fill: #fff;
}

@keyframes halo {
  0%, 100% { opacity: 0.3; transform: scale(0.96); }
  50% { opacity: 1; transform: scale(1.06); }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; }
}
</style>