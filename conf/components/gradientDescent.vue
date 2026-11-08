<!--
  GradientDescent : deux repères liés par le même paramètre θ₁.
    - En haut : le nuage de points et la droite y = θ₁·(x − x̄) + ȳ, avec les écarts
      (traits verticaux) entre chaque point et la droite.
    - En bas : la fonction de coût J(θ₁), une parabole, et une bille qui descend
      dedans. Le score J est affiché et baisse quand la droite s'ajuste.

  Pourquoi une parabole ?
    La droite passe toujours par le centre du nuage (x̄, ȳ), ce qui revient à garder
    θ₀ à sa valeur optimale. Il ne reste alors que θ₁, et
        J(θ₁) = 1/(2n) · Σ ( y_t − f(x_t ; θ) )²
    est exactement une parabole en θ₁.

  Animation (boucle)
    mauvais paramètre → descente de gradient pas à pas → bon paramètre → retour au départ.
    Chaque pas est un vrai pas de gradient : θ₁ ← θ₁ − η · dJ/dθ₁.

  Props
    running    Lance / arrête la boucle (défaut true). À l'arrêt, le composant revient
               au mauvais paramètre. Ex. dans Slidev : :running="clicks >= 1"
    offset     Départ = θ₁ optimal + offset (défaut -1.3, doit rester dans ]-1.6 ; 1.6[)
    steps      Nombre de pas de gradient par boucle (défaut 14)
    lr         Pas d'apprentissage η. 0 (défaut) = automatique : η = 0.25 / courbure,
               donc l'écart au minimum est réduit de 25 % à chaque pas.
    stepMs     Durée du déplacement d'un pas (défaut 450)
    pauseMs    Pause entre deux pas (défaut 140)
    holdBadMs  Pause sur le mauvais paramètre avant de descendre (défaut 1400)
    holdGoodMs Pause sur le bon paramètre avant de recommencer (défaut 2400)
    n, seed    Nuage de points (mêmes défauts que regressionplot.vue)
    amplitude  Flottement des points (défaut 2.5)
    grid       Grille discrète du repère du haut (défaut true)
-->
<template>
  <svg
    class="gd"
    :viewBox="`0 0 ${W} ${H}`"
    role="img"
    aria-label="Une droite qui s'ajuste à un nuage de points, et le coût associé qui descend le long d'une parabole"
  >
    <defs>
      <marker
        id="gd-arrow"
        viewBox="0 0 10 10"
        refX="8"
        refY="5"
        markerWidth="7"
        markerHeight="7"
        orient="auto-start-reverse"
      >
        <path d="M 0 1 L 9 5 L 0 9 z" fill="currentColor" />
      </marker>
      <clipPath id="gd-clip-data">
        <rect :x="sx(0)" :y="sy(10)" :width="sx(10) - sx(0)" :height="sy(0) - sy(10)" />
      </clipPath>
      <clipPath id="gd-clip-cost">
        <rect :x="C.ox" :y="C.top - 6" :width="C.right - C.ox + 4" :height="C.oy - C.top + 6" />
      </clipPath>
    </defs>

    <!-- ============ Haut : régression ============ -->
    <g v-if="grid" class="grid">
      <line v-for="t in ticks" :key="`gx${t}`" :x1="sx(t)" :y1="sy(0)" :x2="sx(t)" :y2="sy(10)" />
      <line v-for="t in ticks" :key="`gy${t}`" :x1="sx(0)" :y1="sy(t)" :x2="sx(10)" :y2="sy(t)" />
    </g>

    <g class="axes">
      <line :x1="sx(0)" :y1="sy(0)" :x2="sx(10) + 14" :y2="sy(0)" marker-end="url(#gd-arrow)" />
      <line :x1="sx(0)" :y1="sy(0)" :x2="sx(0)" :y2="sy(10) - 14" marker-end="url(#gd-arrow)" />
    </g>
    <text class="label" :x="sx(10) + 8" :y="sy(0) + 28">x</text>
    <text class="label" :x="sx(0) - 24" :y="sy(10) - 10">y</text>

    <g clip-path="url(#gd-clip-data)">
      <g class="residuals">
        <line
          v-for="p in points"
          :key="p.id"
          :x1="sx(p.x)" :y1="sy(p.y)"
          :x2="sx(p.x)" :y2="sy(yhat(p.x))"
        />
      </g>
      <line
        class="fit"
        :x1="sx(0)" :y1="sy(yhat(0))"
        :x2="sx(10)" :y2="sy(yhat(10))"
      />
    </g>

    <g class="points">
      <circle
        v-for="p in points"
        :key="p.id"
        class="dot"
        :cx="sx(p.x)"
        :cy="sy(p.y)"
        r="5.5"
        :style="p.style"
      />
    </g>

    <!-- ============ Bas : fonction de coût ============ -->
    <g class="axes">
      <line :x1="C.ox" :y1="C.oy" :x2="C.right + 12" :y2="C.oy" marker-end="url(#gd-arrow)" />
      <line :x1="C.ox" :y1="C.oy" :x2="C.ox" :y2="C.top - 14" marker-end="url(#gd-arrow)" />
    </g>
    <text class="label" :x="C.right + 8" :y="C.oy + 28">
      θ<tspan class="sub" dy="5">1</tspan>
    </text>
    <text class="label" :x="C.ox - 26" :y="C.top - 8">J</text>

    <!-- Position du minimum -->
    <line
      class="optimum"
      :x1="xc(stats.wStar)" :y1="yc(cost(stats.wStar))"
      :x2="xc(stats.wStar)" :y2="C.oy"
    />

    <path class="curve" :d="curvePath" />

    <!-- Pas déjà parcourus -->
    <g class="trail">
      <circle
        v-for="(tw, i) in trail"
        :key="i"
        :cx="xc(tw)"
        :cy="yc(cost(tw))"
        r="4.5"
      />
    </g>

    <!-- Valeur courante de θ₁ sur l'axe, et tangente (= gradient) -->
    <line class="drop" :x1="ball.x" :y1="ball.y" :x2="ball.x" :y2="C.oy" />
    <circle class="mark" :cx="ball.x" :cy="C.oy" r="4" />
    <line class="tangent" clip-path="url(#gd-clip-cost)"
      :x1="tangent.x1" :y1="tangent.y1" :x2="tangent.x2" :y2="tangent.y2" />
    <circle class="ball" :cx="ball.x" :cy="ball.y" r="9" />

    <!-- Score -->
    <text class="score" :x="xc(stats.wStar)" :y="C.top + 34" text-anchor="middle">
      <tspan class="sym">J</tspan> = {{ fmt(cost(w)) }}
    </text>
    <text class="param" :x="xc(stats.wStar)" :y="C.top + 62" text-anchor="middle">
      <tspan class="sym">θ</tspan><tspan class="sub" dy="5">1</tspan><tspan dy="-5"> = {{ fmt(w) }}</tspan>
    </text>
  </svg>
</template>

<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  running: { type: Boolean, default: true },
  offset: { type: Number, default: -1.3 },
  steps: { type: Number, default: 14 },
  lr: { type: Number, default: 0 },
  stepMs: { type: Number, default: 450 },
  pauseMs: { type: Number, default: 140 },
  holdBadMs: { type: Number, default: 1400 },
  holdGoodMs: { type: Number, default: 2400 },
  n: { type: Number, default: 40 },
  seed: { type: Number, default: 7 },
  amplitude: { type: Number, default: 2.5 },
  grid: { type: Boolean, default: true }
})

// ---------- Géométrie ----------
const W = 600
const H = 664
const ticks = [2, 4, 6, 8, 10]

// Haut : repère des données (domaine 0..10 sur x et y)
const P1 = { ox: 60, oy: 300, ux: 50, uy: 27 }
const sx = (x) => P1.ox + x * P1.ux
const sy = (y) => P1.oy - y * P1.uy

// Bas : repère du coût. On affiche θ₁ dans [θ* − HALF ; θ* + HALF].
const C = { ox: 60, oy: 624, right: 560, top: 392 }
const HALF = 1.6
const CURVE_X0 = 76
const CURVE_X1 = 556
const KX = (CURVE_X1 - CURVE_X0) / (2 * HALF) // px par unité de θ₁

// ---------- Données (même génération que regressionplot.vue) ----------
function mulberry32(a) {
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v))

const points = computed(() => {
  const rand = mulberry32(props.seed)
  const gauss = () =>
    Math.sqrt(-2 * Math.log(1 - rand())) * Math.cos(2 * Math.PI * rand())

  // L'ordre des appels à rand() doit rester identique à regressionplot.vue
  // pour obtenir exactement le même nuage.
  return Array.from({ length: props.n }, (_, i) => {
    const x = 0.8 + rand() * 8.4
    const y = clamp(0.7 * x + 1.5 + gauss() * 0.9, 0.4, 9.6)
    const a = props.amplitude * (0.5 + rand() * 0.5)
    const angle = rand() * Math.PI * 2
    return {
      id: i,
      x,
      y,
      style: {
        '--dx': `${(Math.cos(angle) * a).toFixed(2)}px`,
        '--dy': `${(Math.sin(angle) * a).toFixed(2)}px`,
        '--dur': `${(3.5 + rand() * 3).toFixed(2)}s`,
        '--delay': `${(-rand() * 6).toFixed(2)}s`
      }
    }
  })
})

// ---------- Modèle, coût, gradient ----------
// Modèle : ŷ = ȳ + θ₁ (x − x̄)   (θ₀ = ȳ − θ₁ x̄ est son optimum pour tout θ₁)
const stats = computed(() => {
  const P = points.value
  const m = P.length
  const xb = P.reduce((s, p) => s + p.x, 0) / m
  const yb = P.reduce((s, p) => s + p.y, 0) / m
  let sxx = 0
  let sxy = 0
  for (const p of P) {
    sxx += (p.x - xb) ** 2
    sxy += (p.x - xb) * (p.y - yb)
  }
  return { m, xb, yb, sxx, sxy, curv: sxx / m, wStar: sxy / sxx }
})

const yhat = (x) => stats.value.yb + w.value * (x - stats.value.xb)

// J(θ₁) = 1/(2n) Σ (y_t − ŷ_t)²
const cost = (theta) => {
  const { m, xb, yb } = stats.value
  let s = 0
  for (const p of points.value) {
    const r = p.y - yb - theta * (p.x - xb)
    s += r * r
  }
  return s / (2 * m)
}

// dJ/dθ₁
const grad = (theta) => {
  const { m, sxx, sxy } = stats.value
  return -(sxy - theta * sxx) / m
}

const lrEff = computed(() => (props.lr > 0 ? props.lr : 0.25 / stats.value.curv))
const start = computed(() => stats.value.wStar + props.offset)

// Trajectoire complète de la descente de gradient
const path = computed(() => {
  const out = [start.value]
  for (let k = 0; k < props.steps; k++) {
    out.push(out[k] - lrEff.value * grad(out[k]))
  }
  return out
})

// ---------- Repère du coût ----------
const xc = (theta) => CURVE_X0 + (theta - (stats.value.wStar - HALF)) * KX
const jMax = computed(() => cost(stats.value.wStar - HALF))
const kY = computed(() => (C.oy - C.top) / jMax.value)
const yc = (j) => C.oy - j * kY.value

const curvePath = computed(() => {
  const N = 60
  const t0 = stats.value.wStar - HALF
  let d = ''
  for (let i = 0; i <= N; i++) {
    const t = t0 + (i / N) * 2 * HALF
    d += `${i === 0 ? 'M' : 'L'}${xc(t).toFixed(1)} ${yc(cost(t)).toFixed(1)} `
  }
  return d
})

// ---------- État animé ----------
const w = ref(start.value) // θ₁ courant : tout le reste en dérive
const trail = ref([])

const ball = computed(() => ({ x: xc(w.value), y: yc(cost(w.value)) }))

const tangent = computed(() => {
  const slope = (-kY.value * grad(w.value)) / KX // pente en pixels
  const L = 55
  const { x, y } = ball.value
  return { x1: x - L, y1: y - slope * L, x2: x + L, y2: y + slope * L }
})

const fmt = (v) => v.toFixed(2).replace('-', '\u2212')

// ---------- Boucle d'animation ----------
let runId = 0
let reduceMotion = false

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const ease = (k) => -(Math.cos(Math.PI * k) - 1) / 2

function tween(from, to, ms) {
  return new Promise((resolve) => {
    const id = runId
    if (ms <= 0 || reduceMotion) {
      w.value = to
      resolve()
      return
    }
    const t0 = performance.now()
    const tick = (t) => {
      if (id !== runId) return resolve()
      const k = Math.min(1, (t - t0) / ms)
      w.value = from + (to - from) * ease(k)
      if (k < 1) requestAnimationFrame(tick)
      else resolve()
    }
    requestAnimationFrame(tick)
  })
}

async function cycle(id) {
  while (id === runId) {
    const ws = path.value
    trail.value = [ws[0]]
    w.value = ws[0]
    await sleep(props.holdBadMs)
    for (let k = 0; k < ws.length - 1; k++) {
      if (id !== runId) return
      await tween(ws[k], ws[k + 1], props.stepMs)
      if (id !== runId) return
      trail.value = [...trail.value, ws[k + 1]]
      await sleep(props.pauseMs)
    }
    if (id !== runId) return
    await sleep(props.holdGoodMs)
    if (id !== runId) return
    trail.value = []
    await tween(w.value, ws[0], 900)
  }
}

function play() {
  cycle(++runId)
}

function reset() {
  runId++
  w.value = start.value
  trail.value = [start.value]
}

watch(
  () => props.running,
  (on) => (on ? play() : reset())
)

onMounted(() => {
  reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
  if (props.running) play()
  else reset()
})

onBeforeUnmount(() => {
  runId++
})
</script>

<style scoped>
.gd {
  --point: #1d4ed8;
  --fit: #ea580c;
  width: 100%;
  height: 100%;
  color: currentColor;
  overflow: visible;
}

/* ---------- Repères ---------- */
.grid line {
  stroke: currentColor;
  stroke-opacity: 0.1;
  stroke-width: 1;
}

.axes line {
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}

.label {
  fill: currentColor;
  font-family: KaTeX_Math, 'Times New Roman', serif;
  font-style: italic;
  font-size: 22px;
}

.sub {
  font-size: 0.65em;
}

/* ---------- Régression ---------- */
.residuals line {
  stroke: var(--fit);
  stroke-opacity: 0.35;
  stroke-width: 1.5;
}

.fit {
  stroke: var(--fit);
  stroke-width: 3.5;
  stroke-linecap: round;
}

.dot {
  fill: var(--point);
  fill-opacity: 0.85;
  stroke: #ffffff;
  stroke-width: 1.5;
  animation: float var(--dur) ease-in-out var(--delay) infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(var(--dx), var(--dy));
  }
}

/* ---------- Coût ---------- */
.curve {
  fill: none;
  stroke: currentColor;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.optimum {
  stroke: currentColor;
  stroke-opacity: 0.3;
  stroke-width: 1.5;
  stroke-dasharray: 4 6;
}

.trail circle {
  fill: none;
  stroke: var(--fit);
  stroke-width: 2;
  stroke-opacity: 0.55;
}

.drop {
  stroke: var(--fit);
  stroke-opacity: 0.5;
  stroke-width: 1.5;
  stroke-dasharray: 3 5;
}

.mark {
  fill: var(--fit);
}

.tangent {
  stroke: var(--fit);
  stroke-opacity: 0.8;
  stroke-width: 2;
  stroke-linecap: round;
}

.ball {
  fill: var(--fit);
  stroke: #ffffff;
  stroke-width: 2.5;
}

.score {
  fill: var(--fit);
  font-family: KaTeX_Main, 'Times New Roman', serif;
  font-size: 28px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.param {
  fill: currentColor;
  fill-opacity: 0.75;
  font-family: KaTeX_Main, 'Times New Roman', serif;
  font-size: 20px;
  font-variant-numeric: tabular-nums;
}

.sym {
  font-family: KaTeX_Math, 'Times New Roman', serif;
  font-style: italic;
}

@media (prefers-reduced-motion: reduce) {
  .dot {
    animation: none;
  }
}
</style>