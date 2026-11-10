<template>
  <section class="mlp-demo" aria-label="Perceptron multicouche : propagation avant">
    <svg
      class="diagram"
      viewBox="0 0 820 420"
      role="img"
      aria-label="Un perceptron multicouche à trois entrées, deux couches cachées de cinq neurones et trois sorties. Le signal se propage couche après couche, puis la sortie la plus forte désigne la classe prédite."
    >
      <defs>
        <filter id="mlp-glow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <!-- ============ En-têtes de couches ============ -->
      <g v-for="(L, l) in LAYERS" :key="'hd' + l" :opacity="hdrOp[l]">
        <text class="hd" :x="L.x" y="30">{{ L.name }}</text>
        <text class="hd-sub" :x="L.x" y="50">{{ L.sub }}</text>
      </g>

      <!-- ============ Connexions au repos : épaisseur = |poids|, pointillés si négatif ============ -->
      <g class="wires">
        <path
          v-for="(e, k) in ALL"
          :key="'w' + k"
          :d="e.d"
          :stroke-width="wireWidth(e.w)"
          :stroke-dasharray="e.w < 0 ? '5 6' : null"
        />
      </g>

      <!-- Projections : les connexions s'illuminent au passage du signal -->
      <g class="overlays" filter="url(#mlp-glow)">
        <path
          v-for="(o, k) in overlay"
          :key="'ov' + k"
          :d="o.d"
          pathLength="1"
          stroke-dasharray="1 1"
          :stroke-dashoffset="1 - o.prog"
          :stroke-width="o.width"
          :opacity="o.op"
        />
      </g>

      <!-- Impulsions -->
      <g class="particles" filter="url(#mlp-glow)">
        <circle v-for="(p, i) in pulses" :key="'pu' + i" :cx="p.x" :cy="p.y" :r="p.r" :opacity="p.o" />
      </g>

      <!-- ============ Neurones ============ -->
      <g v-for="n in NODES" :key="'n' + n.l + '-' + n.k">
        <circle
          v-if="flash[n.l] > 0.02"
          :cx="n.x" :cy="n.y" :r="26 + flash[n.l] * 9"
          class="flash"
          :opacity="flash[n.l] * 0.9"
          filter="url(#mlp-glow)"
        />
        <circle
          class="ring"
          :cx="n.x" :cy="n.y" r="25"
          :stroke-dasharray="val(n) < 0 ? '3 4' : null"
        />
        <circle class="core" :cx="n.x" :cy="n.y" r="18" />
        <circle
          :cx="n.x" :cy="n.y" r="18"
          fill="#fff"
          :fill-opacity="clamp(Math.abs(val(n)) / 1.0) * 0.95"
        />
        <text
          class="node-text" :x="n.x" :y="n.y + 4.5"
          :style="{ fill: Math.abs(val(n)) > 0.6 ? '#050505' : '#fff' }"
        >{{ fr(val(n), 1) }}</text>
      </g>

      <!-- Étiquettes des entrées -->
      <text v-for="(n, k) in LAYER_NODES[0]" :key="'xl' + k" class="sym" :x="n.x - 55" :y="n.y + 6">x{{ SUB[k] }}</text>

      <!-- Sorties : probabilités (softmax) et classe prédite -->
      <g v-for="(n, k) in LAYER_NODES[3]" :key="'out' + k">
        <text class="sym start" :x="BAR_X" :y="n.y - 14">ŷ{{ SUB[k] }}</text>
        <rect class="bar-bg" :x="BAR_X" :y="n.y - 6" :width="BAR_W" height="12" rx="6" />
        <rect
          class="bar" :x="BAR_X" :y="n.y - 6"
          :width="Math.max(0, BAR_W * outShown[k])" height="12" rx="6"
          :filter="k === win && winOp > 0.1 ? 'url(#mlp-glow)' : null"
        />
        <text class="pct" :x="BAR_X + BAR_W" :y="n.y + 26" :opacity="rev[3]">{{ fr(outShown[k] * 100, 0) }} %</text>
      </g>
      <g :opacity="winOp">
        <circle class="halo" :cx="LAYER_NODES[3][win].x" :cy="LAYER_NODES[3][win].y" r="34" />
        <circle class="winner" :cx="LAYER_NODES[3][win].x" :cy="LAYER_NODES[3][win].y" r="31" filter="url(#mlp-glow)" />
      </g>

    </svg>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* ---------- Réseau 3 → 5 → 5 → 3 ----------
   Poids tirés une fois pour toutes (générateur à graine), puis propagation avant réelle :
   h¹ = tanh(W¹x), h² = tanh(W²h¹), ŷ = softmax(W³h²). Rien n'est écrit en dur. */
const SIZES = [3, 5, 5, 3]
const SAMPLES_X = [
  [0.8, -0.4, 1.0],
  [-0.7, 0.9, 0.3],
  [0.2, 0.6, -0.9],
]

function rng(seed) {
  return () => {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
const rand = rng(7)
const SCALE = [1.3, 1.0, 1.15]
// W[l][j][i] : poids de la source i (couche l) vers le neurone j (couche l+1)
const W = SCALE.map((s, l) =>
  Array.from({ length: SIZES[l + 1] }, () =>
    Array.from({ length: SIZES[l] }, () => Number(((rand() * 2 - 1) * s).toFixed(2)))
  )
)

function forward(x) {
  const acts = [x]
  for (let l = 0; l < 3; l++) {
    const z = W[l].map((row) => row.reduce((a, w, i) => a + w * acts[l][i], 0))
    if (l < 2) acts.push(z.map(Math.tanh))
    else {
      const m = Math.max(...z)
      const e = z.map((v) => Math.exp(v - m))
      const s = e.reduce((a, v) => a + v, 0)
      acts.push(e.map((v) => v / s))
    }
  }
  return { x, acts }
}

const DUR = 6400
const STEPS = SAMPLES_X.map((x, k) => ({ ...forward(x), start: k * DUR }))
const TOTAL = STEPS.length * DUR + 800

/* ---------- Géométrie ---------- */
const XS = [95, 285, 475, 665]
const BAR_X = 706
const BAR_W = 82
const SUB = '\u2081\u2082\u2083\u2084\u2085'
const yOf = (n, k) => (n === 3 ? 230 + (k - 1) * 100 : 230 + (k - 2) * 68)

const LAYERS = [
  { x: XS[0], name: 'Entrée', sub: 'x ∈ ℝ³' },
  { x: XS[1], name: 'Cachée 1', sub: 'h¹ ∈ ℝ⁵' },
  { x: XS[2], name: 'Cachée 2', sub: 'h² ∈ ℝ⁵' },
  { x: XS[3], name: 'Sortie', sub: 'ŷ ∈ ℝ³' },
]
const LAYER_NODES = SIZES.map((n, l) => Array.from({ length: n }, (_, k) => ({ l, k, x: XS[l], y: yOf(n, k) })))
const NODES = LAYER_NODES.flat()

// Connexions : de chaque neurone de la couche l vers chaque neurone de la couche l+1
const ALL = []
for (let l = 0; l < 3; l++) {
  LAYER_NODES[l + 1].forEach((b, j) => {
    LAYER_NODES[l].forEach((a, i) => {
      const x1 = a.x + 25
      const x2 = b.x - 25
      const xm = (x1 + x2) / 2
      ALL.push({
        l, i, j,
        w: W[l][j][i],
        pts: [[x1, a.y], [xm, a.y], [xm, b.y], [x2, b.y]],
        d: `M ${x1} ${a.y} C ${xm} ${a.y}, ${xm} ${b.y}, ${x2} ${b.y}`,
      })
    })
  })
}

/* ---------- Outils ---------- */
const clamp = (v) => Math.min(1, Math.max(0, v))
const ease = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2)
const lerp = (a, b, k) => a + (b - a) * k
const wireWidth = (w) => 0.6 + Math.abs(w) * 1.7

function bez(pts, u) {
  const m = 1 - u
  const [p0, p1, p2, p3] = pts
  return [
    m * m * m * p0[0] + 3 * m * m * u * p1[0] + 3 * m * u * u * p2[0] + u * u * u * p3[0],
    m * m * m * p0[1] + 3 * m * m * u * p1[1] + 3 * m * u * u * p2[1] + u * u * u * p3[1],
  ]
}

// Nombres à la française : virgule décimale, vrai signe moins
const fr = (n, d) => {
  const v = Math.abs(n) < 0.5 * Math.pow(10, -d) ? 0 : n
  const s = Math.abs(v).toFixed(d).replace('.', ',')
  return v < 0 ? '\u2212' + s : s
}

/* ---------- Horloge ---------- */
const stepIdx = ref(0)
const t = ref(0)
let raf = 0
let t0 = 0

function locate(tau) {
  for (let k = STEPS.length - 1; k >= 0; k--) {
    if (tau >= STEPS[k].start) {
      stepIdx.value = k
      t.value = Math.min(tau - STEPS[k].start, DUR)
      return
    }
  }
}
function frame(ts) {
  if (!t0) t0 = ts
  locate((ts - t0) % TOTAL)
  raf = requestAnimationFrame(frame)
}
onMounted(() => {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    stepIdx.value = 0
    t.value = 5300 // image fixe : propagation terminée, classe prédite visible
  } else {
    raf = requestAnimationFrame(frame)
  }
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* ---------- Chronologie d'un exemple (ms) ---------- */
const S = [400, 1900, 3400] // départ des impulsions entre couches l → l+1
const REV = [0, 1450, 2950, 4450] // moment où chaque couche prend sa valeur
const WIN = [[0, 1000], [1450, 2400], [2950, 3900], [4450, 5800]]

const step = computed(() => STEPS[stepIdx.value])
const prev = computed(() => STEPS[(stepIdx.value - 1 + STEPS.length) % STEPS.length])
const endFade = computed(() => 1 - clamp((t.value - (DUR - 350)) / 350))
const enterK = computed(() => ease(clamp(t.value / 350)))
const rev = computed(() => REV.map((r) => ease(clamp((t.value - r) / 350))))

const shownX = computed(() => step.value.x.map((x, i) => lerp(prev.value.x[i], x, enterK.value)))
const actsShown = computed(() =>
  [1, 2, 3].map((l) => step.value.acts[l].map((a) => a * rev.value[l] * endFade.value))
)
const outShown = computed(() => actsShown.value[2])
const val = (n) => (n.l === 0 ? shownX.value[n.k] : actsShown.value[n.l - 1][n.k])

const flash = computed(() =>
  REV.map((r, l) => (l === 0 ? 0 : clamp((t.value - r) / 200) * (1 - clamp((t.value - r - 200) / 500))))
)

const hdrOp = computed(() =>
  WIN.map(([a, b]) => 0.4 + 0.6 * clamp((t.value - a) / 250) * (1 - clamp((t.value - b) / 300)))
)

/* ---------- Connexions et impulsions ---------- */
const contrib = (e) => step.value.acts[e.l][e.i] * e.w
const uOf = (e) => (t.value - S[e.l] - e.i * 50) / 800

const overlay = computed(() =>
  ALL.map((e) => {
    const c = Math.abs(contrib(e))
    const fade = 1 - clamp((t.value - S[e.l] - 1100) / 600)
    return {
      d: e.d,
      prog: ease(clamp(uOf(e))),
      width: wireWidth(e.w) + 0.8,
      op: c < 0.01 ? 0 : fade * (0.35 + 0.65 * clamp(c / 0.8)),
    }
  })
)

const pulses = computed(() => {
  const out = []
  ALL.forEach((e) => {
    const u0 = uOf(e)
    if (u0 <= 0 || u0 >= 1) return
    const c = Math.abs(contrib(e))
    if (c < 0.01) return
    const rBase = 1.8 + 2.6 * clamp(c / 0.8)
    for (let k = 0; k < 3; k++) {
      const [x, y] = bez(e.pts, ease(clamp(u0 - k * 0.05)))
      out.push({ x, y, r: Math.max(rBase - k * 0.8, 0.7), o: 1 - k * 0.3 })
    }
  })
  return out
})

/* ---------- Sortie : classe prédite ---------- */
const win = computed(() => {
  const o = step.value.acts[3]
  return o.indexOf(Math.max(...o))
})
const winOp = computed(() => clamp((t.value - 4800) / 300) * endFade.value)

</script>

<style scoped>
.mlp-demo {
  --white: #fff;
  --muted: rgba(255, 255, 255, 0.58);
  box-sizing: border-box;
  width: 100%;
  padding: clamp(16px, 3vw, 30px);
  overflow: hidden;
  color: #fff;
  background: #050505;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

.diagram {
  display: block;
  width: 100%;
  height: auto;
  overflow: visible;
}
.diagram text {
  text-anchor: middle;
}

/* En-têtes */
.hd {
  fill: #fff;
  font: italic 17px Georgia, 'Times New Roman', serif;
}
.hd-sub {
  fill: var(--muted);
  font: italic 14px Georgia, 'Times New Roman', serif;
}

/* Connexions */
.wires path {
  fill: none;
  stroke: rgba(255, 255, 255, 0.2);
  stroke-linecap: round;
}
.overlays path {
  fill: none;
  stroke: #fff;
  stroke-linecap: round;
}
.particles circle {
  fill: #fff;
}

/* Neurones */
.ring {
  fill: none;
  stroke: rgba(255, 255, 255, 0.78);
  stroke-width: 1.4;
}
.core {
  fill: #050505;
  stroke: #fff;
  stroke-width: 1.6;
}
.node-text {
  fill: #fff;
  font: italic 13px Georgia, serif;
}
.flash {
  fill: none;
  stroke: #fff;
  stroke-width: 1.2;
}
.sym {
  fill: rgba(255, 255, 255, 0.8);
  font: italic 18px Georgia, 'Times New Roman', serif;
}
.diagram .sym.start {
  text-anchor: start;
  font-size: 15px;
}

/* Sorties */
.bar-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.45);
  stroke-width: 1.1;
}
.bar {
  fill: #fff;
}
.diagram .pct {
  fill: var(--muted);
  font: italic 13px Georgia, serif;
  text-anchor: end;
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
  animation: halo 2.8s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: center;
}

@keyframes halo {
  0%, 100% { opacity: 0.3; transform: scale(0.96); }
  50% { opacity: 1; transform: scale(1.06); }
}

@media (max-width: 560px) {
  .mlp-demo { padding: 13px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; }
}
</style>