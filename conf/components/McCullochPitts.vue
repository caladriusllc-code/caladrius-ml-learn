<template>
  <div class="mcp">
    <svg
      viewBox="0 0 560 330"
      role="img"
      :aria-label="`Neurone logique de McCulloch et Pitts : porte ${gate.name}`"
    >
      <defs>
        <filter id="mcp-glow" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="3.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <!-- Opération logique en cours -->
      <text :x="280" y="28" class="title" :style="{ opacity: titleOpacity }">{{ gate.name }}</text>

      <!-- Branches au repos (pointillées si le poids est négatif) -->
      <g class="base">
        <path
          v-for="(s, i) in strands"
          :key="'base' + i"
          :d="s.d"
          :class="{ neg: s.neg }"
        />
        <line :x1="C.x + R_RING + 4" :y1="C.y" :x2="O.x - R_O - 2" :y2="O.y" />
      </g>

      <!-- Barre d'inhibition au bout des branches négatives -->
      <line
        v-for="(b, i) in bars"
        :key="'bar' + i"
        :x1="b.x1" :y1="b.y1" :x2="b.x2" :y2="b.y2"
        class="bar"
      />

      <!-- Projections : la branche se colore au passage du signal -->
      <g filter="url(#mcp-glow)">
        <path
          v-for="(s, i) in strandViz"
          :key="'ov' + i"
          :d="s.d"
          pathLength="1"
          stroke-dasharray="1 1"
          :stroke-dashoffset="1 - s.prog"
          :style="{ color: s.color, opacity: s.op }"
          class="overlay"
        />
        <line
          :x1="C.x + R_RING + 4" :y1="C.y" :x2="O.x - R_O - 2" :y2="O.y"
          pathLength="1"
          stroke-dasharray="1 1"
          :stroke-dashoffset="1 - outProg"
          :style="{ color: 'var(--cc)', opacity: outOpacity }"
          class="overlay"
        />
      </g>

      <!-- Ondes (vers l'extérieur : C s'active, vers l'intérieur : C est freiné) et étincelles -->
      <g>
        <circle
          v-for="(r, i) in ripples"
          :key="'rip' + i"
          :cx="C.x" :cy="C.y" :r="r.r"
          fill="none"
          stroke-width="2"
          :style="{ color: r.color, stroke: 'currentColor', opacity: r.o }"
        />
        <circle
          v-for="(s, i) in sparkles"
          :key="'sp' + i"
          :cx="s.x" :cy="s.y" :r="s.r"
          fill="currentColor"
          :style="{ color: 'var(--cc)', opacity: s.o }"
        />
      </g>

      <!-- Impulsions qui voyagent -->
      <g filter="url(#mcp-glow)">
        <circle
          v-for="(p, i) in pulses"
          :key="'pu' + i"
          :cx="p.x" :cy="p.y" :r="p.r"
          fill="currentColor"
          :style="{ color: p.color, opacity: p.o }"
        />
      </g>

      <!-- Entrées A et B -->
      <g v-for="inp in inputNodes" :key="inp.name">
        <text :x="inp.x" :y="inp.y - 36" class="letter">{{ inp.name }}</text>
        <circle
          :cx="inp.x" :cy="inp.y" :r="R_IN"
          :fill="inp.color"
          :fill-opacity="inp.lit ? 0.9 : 0"
          :stroke="inp.color"
          stroke-width="2.5"
          :filter="inp.lit ? 'url(#mcp-glow)' : null"
        />
        <text
          :x="inp.x" :y="inp.y + 7"
          class="digit"
          :style="{ fill: inp.lit ? '#fff' : 'currentColor' }"
        >{{ inp.value }}</text>
        <text :x="inp.x + 42" :y="inp.wy" class="small">poids w = {{ fmt(inp.weight) }}</text>
      </g>

      <!-- Neurone C -->
      <g :transform="`translate(${shake} 0)`">
        <circle :cx="C.x" :cy="C.y" :r="R_RING" class="ring-track" />
        <circle
          :cx="C.x" :cy="C.y" :r="R_RING"
          pathLength="1"
          stroke-dasharray="1 1"
          :stroke-dashoffset="1 - ringProg"
          :transform="`rotate(-90 ${C.x} ${C.y})`"
          class="ring"
        />
        <circle
          :cx="C.x" :cy="C.y" :r="R_C"
          :fill-opacity="0.08 + 0.82 * glow"
          class="soma"
          :filter="glow > 0.1 ? 'url(#mcp-glow)' : null"
        />
        <text
          :x="C.x" :y="C.y - 6" class="sigma"
          :style="{ fill: glow > 0.5 ? '#fff' : 'currentColor' }"
        >Σ</text>
        <text
          :x="C.x" :y="C.y + 20" class="digit"
          :style="{ fill: glow > 0.5 ? '#fff' : 'currentColor' }"
        >{{ fmt(arrived) }}</text>
        <text :x="C.x" :y="C.y - 60" class="letter">C</text>
        <text :x="C.x" :y="C.y + 76" class="small">seuil θ = {{ theta }}</text>
      </g>

      <!-- Sortie -->
      <g>
        <circle
          :cx="O.x" :cy="O.y" :r="R_O"
          class="out-node"
          :fill-opacity="0.1 + 0.8 * yLevel"
          :filter="yLevel > 0.1 ? 'url(#mcp-glow)' : null"
        />
        <text
          :x="O.x" :y="O.y + 6" class="digit small-digit"
          :style="{ fill: yLevel > 0.5 ? '#fff' : 'currentColor' }"
        >y</text>
        <text :x="O.x" :y="O.y + 44" class="small">sortie = {{ yLevel > 0.5 ? 1 : 0 }}</text>
      </g>

      <!-- Verdict -->
      <text
        :x="C.x" :y="C.y + 104" class="status"
        :style="{ opacity: statusOpacity, fill: fire ? 'var(--cc)' : 'currentColor' }"
      >
        {{ fire ? 'Σ ≥ θ : C s\u2019active' : 'Σ < θ : C reste silencieux' }}
      </text>

      <!-- Table de vérité de la porte -->
      <g>
        <g v-for="(c, i) in CASES" :key="'chip' + i">
          <rect
            :x="50 + i * 118" y="292" width="106" height="30" rx="8"
            class="chip"
            :class="{ active: i === caseIdx }"
          />
          <text
            :x="50 + i * 118 + 53" y="312"
            class="chip-text"
            :class="{ active: i === caseIdx }"
          >A={{ c[0] }} B={{ c[1] }} → {{ outcome(c) }}</text>
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* ---------- Portes logiques ----------
   Un neurone de McCulloch et Pitts reçoit des entrées binaires pondérées
   et s'active (y = 1) quand la somme pondérée atteint le seuil θ.
   Un poids négatif est une entrée inhibitrice.

   Prop `gate` : 'et' | 'ou' | 'a-non-b' pour figer une porte.
   Sans prop, le composant les enchaîne toutes. */
const GATES = [
  { key: 'et', name: 'A ET B', w: [1, 1], theta: 2 },
  { key: 'ou', name: 'A OU B', w: [1, 1], theta: 1 },
  { key: 'a-non-b', name: 'A ET NON B', w: [1, -1], theta: 1 },
]

const props = defineProps({
  gate: { type: String, default: null },
})

const CASES = [[0, 0], [1, 0], [0, 1], [1, 1]]
const CYCLE = 4400 // durée d'un cas en ms

/* ---------- Géométrie ---------- */
const A = { x: 70, y: 80 }
const B = { x: 70, y: 220 }
const C = { x: 340, y: 150 }
const O = { x: 500, y: 150 }
const R_IN = 24
const R_C = 38
const R_RING = 46
const R_O = 20
const END_R = R_RING + 3

const COLOR_A = 'var(--ca)'
const COLOR_B = 'var(--cb)'
const COLOR_INHIB = 'var(--ci)'

const clamp = (v) => Math.min(1, Math.max(0, v))
const ease = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2)
const rad = (d) => (d * Math.PI) / 180
const fmt = (n) => (n < 0 ? '\u2212' + Math.abs(n) : String(n))

// Chaque entrée envoie un faisceau de trois branches vers C
function makeStrands(src, startAngles, endAngles, dy1, dy2, input, color) {
  return startAngles.map((sa, i) => {
    const sx = src.x + (R_IN + 1) * Math.cos(rad(sa))
    const sy = src.y + (R_IN + 1) * Math.sin(rad(sa))
    const ex = C.x + END_R * Math.cos(rad(endAngles[i]))
    const ey = C.y + END_R * Math.sin(rad(endAngles[i]))
    const pts = [
      [sx, sy],
      [sx + 100, sy + dy1[i]],
      [ex - 80, ey + dy2[i]],
      [ex, ey],
    ]
    const f = (n) => n.toFixed(1)
    return {
      pts,
      input,
      color,
      delay: i * 110,
      d: `M${f(pts[0][0])} ${f(pts[0][1])} C${f(pts[1][0])} ${f(pts[1][1])}, ${f(pts[2][0])} ${f(pts[2][1])}, ${f(pts[3][0])} ${f(pts[3][1])}`,
    }
  })
}

const baseStrands = [
  ...makeStrands(A, [-30, 0, 30], [215, 200, 185], [-26, 0, 22], [-18, 0, 14], 0, COLOR_A),
  ...makeStrands(B, [-30, 0, 30], [175, 160, 145], [-22, 0, 26], [-14, 0, 18], 1, COLOR_B),
]

function bez(pts, u) {
  const m = 1 - u
  const [p0, p1, p2, p3] = pts
  return [
    m * m * m * p0[0] + 3 * m * m * u * p1[0] + 3 * m * u * u * p2[0] + u * u * u * p3[0],
    m * m * m * p0[1] + 3 * m * m * u * p1[1] + 3 * m * u * u * p2[1] + u * u * u * p3[1],
  ]
}

/* ---------- Porte active ---------- */
const activeGates = computed(() => {
  const list = props.gate ? GATES.filter((g) => g.key === props.gate) : GATES
  return list.length ? list : GATES
})

/* ---------- Horloge ---------- */
const t = ref(0)
const idx = ref(0) // indice global du cas, toutes portes confondues
let raf = 0
let t0 = 0

const gateIdx = computed(() => Math.floor(idx.value / CASES.length) % activeGates.value.length)
const caseIdx = computed(() => idx.value % CASES.length)
const gate = computed(() => activeGates.value[gateIdx.value])
const theta = computed(() => gate.value.theta)

const potential = (c) => c[0] * gate.value.w[0] + c[1] * gate.value.w[1]
const outcome = (c) => (potential(c) >= theta.value ? 1 : 0)

function frame(ts) {
  if (!t0) t0 = ts
  const e = ts - t0
  idx.value = Math.floor(e / CYCLE) % (activeGates.value.length * CASES.length)
  t.value = e % CYCLE
  raf = requestAnimationFrame(frame)
}

onMounted(() => {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    // Image fixe : un cas où C s'active
    const firing = CASES.findIndex((c) => outcome(c) === 1)
    idx.value = firing === -1 ? 0 : firing
    t.value = 3000
  } else {
    raf = requestAnimationFrame(frame)
  }
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* ---------- États dérivés ---------- */
const inputs = computed(() => CASES[caseIdx.value])
const total = computed(() => potential(inputs.value))
const anyActive = computed(() => inputs.value[0] + inputs.value[1] > 0)
const fire = computed(() => total.value >= theta.value)

const arrived = computed(() => (t.value > 1650 ? total.value : 0))
const decay = computed(() => 1 - clamp((t.value - 3700) / 500))

// L'anneau monte avec les entrées excitatrices et redescend avec les inhibitrices
const ringProg = computed(() => {
  const w = gate.value.w
  const a = inputs.value
  let plus = 0
  let minus = 0
  for (let i = 0; i < 2; i++) {
    if (!a[i]) continue
    if (w[i] > 0) plus += w[i]
    else minus += -w[i]
  }
  const kPlus = clamp((t.value - 1100) / 550)
  const kMinus = clamp((t.value - 1500) / 450)
  return clamp(((plus * kPlus - minus * kMinus) / theta.value)) * decay.value
})

const glow = computed(() =>
  fire.value ? clamp((t.value - 1750) / 200) * (1 - clamp((t.value - 3500) / 600)) : 0
)

const yLevel = computed(() =>
  fire.value ? clamp((t.value - 2500) / 300) * (1 - clamp((t.value - 3800) / 400)) : 0
)

const statusOpacity = computed(() =>
  anyActive.value ? clamp((t.value - 1750) / 250) * (1 - clamp((t.value - 3700) / 400)) : 0
)

// Changement de porte : le titre apparaît en fondu
const titleOpacity = computed(() => (caseIdx.value === 0 ? clamp(t.value / 500) : 1))

const shake = computed(() => {
  const dt = t.value - 1750
  if (fire.value || !anyActive.value || dt < 0 || dt > 500) return 0
  return Math.sin(dt / 18) * 2.4 * (1 - dt / 500)
})

const inputNodes = computed(() => [
  {
    name: 'A', x: A.x, y: A.y, value: inputs.value[0], lit: inputs.value[0] === 1,
    color: COLOR_A, wy: A.y - 30, weight: gate.value.w[0],
  },
  {
    name: 'B', x: B.x, y: B.y, value: inputs.value[1], lit: inputs.value[1] === 1,
    color: COLOR_B, wy: B.y + 44, weight: gate.value.w[1],
  },
])

// Branches colorées selon le poids : rose pour une entrée inhibitrice
const strands = computed(() =>
  baseStrands.map((s) => {
    const neg = gate.value.w[s.input] < 0
    return { ...s, neg, color: neg ? COLOR_INHIB : s.color }
  })
)

// Petite barre qui « bloque » le bout des branches inhibitrices
const bars = computed(() => {
  const out = []
  strands.value.forEach((s, i) => {
    if (!s.neg || i % 3 !== 1) return
    const [, , p2, p3] = s.pts
    const dx = p3[0] - p2[0]
    const dy = p3[1] - p2[1]
    const len = Math.hypot(dx, dy) || 1
    const nx = -dy / len
    const ny = dx / len
    out.push({
      x1: p3[0] + nx * 9, y1: p3[1] + ny * 9,
      x2: p3[0] - nx * 9, y2: p3[1] - ny * 9,
    })
  })
  return out
})

// Branches : la couleur progresse le long de la courbe
const strandViz = computed(() =>
  strands.value.map((s) => {
    const active = inputs.value[s.input] === 1
    const u = clamp((t.value - 350 - s.delay) / 1300)
    return {
      d: s.d,
      color: s.color,
      prog: active ? ease(u) : 0,
      op: active ? 1 - clamp((t.value - 3500) / 700) : 0,
    }
  })
)

// Impulsions lumineuses avec traînée
const pulses = computed(() => {
  const out = []
  for (const s of strands.value) {
    if (inputs.value[s.input] !== 1) continue
    const u0 = (t.value - 350 - s.delay) / 1300
    if (u0 <= 0 || u0 >= 1) continue
    for (let k = 0; k < 5; k++) {
      const [x, y] = bez(s.pts, ease(clamp(u0 - k * 0.04)))
      out.push({ x, y, r: 4.2 - k * 0.7, o: 1 - k * 0.2, color: s.color })
    }
  }
  // Impulsion de sortie
  if (fire.value) {
    const u = (t.value - 1900) / 700
    if (u > 0 && u < 1) {
      for (let k = 0; k < 5; k++) {
        const v = ease(clamp(u - k * 0.05))
        const x0 = C.x + R_RING + 4
        const x1 = O.x - R_O - 2
        out.push({ x: x0 + (x1 - x0) * v, y: C.y, r: 4.6 - k * 0.75, o: 1 - k * 0.2, color: 'var(--cc)' })
      }
    }
  }
  return out
})

const outProg = computed(() => (fire.value ? ease(clamp((t.value - 1900) / 700)) : 0))
const outOpacity = computed(() => (fire.value ? 1 - clamp((t.value - 3500) / 700) : 0))

// Ondes : vers l'extérieur quand C s'active, vers l'intérieur quand un signal inhibiteur arrive
const ripples = computed(() => {
  const out = []
  if (fire.value) {
    for (let k = 0; k < 3; k++) {
      const dt = t.value - 1750 - k * 180
      if (dt > 0 && dt < 1100) {
        out.push({ r: R_RING + ease(dt / 1100) * 66, o: (1 - dt / 1100) * 0.6, color: 'var(--cc)' })
      }
    }
  }
  const inhibited = inputs.value.some((v, i) => v === 1 && gate.value.w[i] < 0)
  if (inhibited) {
    for (let k = 0; k < 2; k++) {
      const dt = t.value - 1600 - k * 200
      if (dt > 0 && dt < 900) {
        out.push({ r: R_RING + (1 - ease(dt / 900)) * 44, o: (1 - dt / 900) * 0.75, color: COLOR_INHIB })
      }
    }
  }
  return out
})

// Étincelles
const sparkles = computed(() => {
  const dt = t.value - 1750
  if (!fire.value || dt < 0 || dt > 1000) return []
  return Array.from({ length: 14 }, (_, i) => {
    const a = rad(i * (360 / 14) + (i % 2) * 9)
    const dist = R_RING + 6 + ease(dt / 1000) * (44 + (i % 3) * 16)
    return {
      x: C.x + dist * Math.cos(a),
      y: C.y + dist * Math.sin(a),
      r: 3 - (dt / 1000) * 2,
      o: 1 - dt / 1000,
    }
  })
})
</script>

<style scoped>
.mcp {
  --ca: #3b82c4;
  --cb: #e8a33d;
  --cc: #1fa38a;
  --ci: #d6456b;

  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

svg {
  width: 100%;
  height: auto;
  display: block;
  overflow: visible;
}

text {
  text-anchor: middle;
  fill: currentColor;
}

.title {
  font-size: 22px;
  font-weight: 700;
}

.base path,
.base line {
  fill: none;
  stroke: currentColor;
  stroke-width: 1.6;
  opacity: 0.2;
  stroke-linecap: round;
}

.base path.neg {
  stroke: var(--ci);
  stroke-dasharray: 5 5;
  opacity: 0.45;
}

.bar {
  stroke: var(--ci);
  stroke-width: 3.5;
  stroke-linecap: round;
}

.overlay {
  fill: none;
  stroke: currentColor;
  stroke-width: 2.6;
  stroke-linecap: round;
}

.letter {
  font-size: 20px;
  font-weight: 700;
}

.digit {
  font-size: 22px;
  font-weight: 700;
}

.small-digit {
  font-size: 18px;
  font-style: italic;
}

.sigma {
  font-size: 15px;
  opacity: 0.8;
}

.small {
  font-size: 13px;
  opacity: 0.65;
}

.status {
  font-size: 15px;
  font-weight: 600;
}

.ring-track {
  fill: none;
  stroke: currentColor;
  stroke-width: 3;
  opacity: 0.12;
}

.ring {
  fill: none;
  stroke: var(--cc);
  stroke-width: 3.5;
  stroke-linecap: round;
}

.soma {
  fill: var(--cc);
  stroke: var(--cc);
  stroke-width: 2.5;
}

.out-node {
  fill: var(--cc);
  stroke: var(--cc);
  stroke-width: 2.5;
}

.chip {
  fill: transparent;
  stroke: currentColor;
  stroke-opacity: 0.25;
  stroke-width: 1.5;
}

.chip.active {
  fill: var(--cc);
  fill-opacity: 0.14;
  stroke: var(--cc);
  stroke-opacity: 1;
}

.chip-text {
  font-size: 13px;
  opacity: 0.6;
}

.chip-text.active {
  opacity: 1;
  font-weight: 600;
}
</style>