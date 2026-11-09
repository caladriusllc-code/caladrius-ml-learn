<template>
  <div class="tlu">
    <svg
      viewBox="0 0 560 272"
      role="img"
      aria-label="Perceptron : trois entrées numériques et un biais, pondérés, sommés puis passés dans une fonction seuil"
    >
      <defs>
        <filter id="tlu-glow" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="3.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <!-- Connexions au repos : épaisseur = |poids|, pointillés si poids négatif -->
      <g class="base">
        <path
          v-for="(b, i) in branches"
          :key="'base' + i"
          :d="b.d"
          :stroke-width="b.width"
          :class="{ neg: b.neg }"
        />
        <line :x1="CAP_END + 4" :y1="CY" :x2="O.x - R_O - 2" :y2="CY" />
      </g>

      <!-- Poids affichés sur les connexions -->
      <text
        v-for="(l, i) in weightLabels"
        :key="'wl' + i"
        :x="l.x" :y="l.y"
        class="small"
      >{{ l.text }}</text>

      <!-- Projections : la connexion se colore au passage du signal -->
      <g filter="url(#tlu-glow)">
        <path
          v-for="(s, i) in strandViz"
          :key="'ov' + i"
          :d="s.d"
          pathLength="1"
          stroke-dasharray="1 1"
          :stroke-dashoffset="1 - s.prog"
          :stroke-width="s.width"
          :style="{ color: s.color, opacity: s.op }"
          class="overlay"
        />
        <line
          :x1="CAP_END + 4" :y1="CY" :x2="O.x - R_O - 2" :y2="CY"
          pathLength="1"
          stroke-dasharray="1 1"
          :stroke-dashoffset="1 - outProg"
          :style="{ color: 'var(--cc)', opacity: outOpacity }"
          stroke-width="3"
          class="overlay"
        />
      </g>

      <!-- Ondes et étincelles quand la TLU s'active -->
      <g>
        <circle
          v-for="(r, i) in ripples"
          :key="'rip' + i"
          :cx="FIRE_X" :cy="CY" :r="r.r"
          fill="none"
          stroke-width="2"
          :style="{ color: 'var(--cc)', stroke: 'currentColor', opacity: r.o }"
        />
        <circle
          v-for="(s, i) in sparkles"
          :key="'sp' + i"
          :cx="s.x" :cy="s.y" :r="s.r"
          fill="currentColor"
          :style="{ color: 'var(--cc)', opacity: s.o }"
        />
      </g>

      <!-- Impulsions : leur taille suit la valeur w·x -->
      <g filter="url(#tlu-glow)">
        <circle
          v-for="(p, i) in pulses"
          :key="'pu' + i"
          :cx="p.x" :cy="p.y" :r="p.r"
          fill="currentColor"
          :style="{ color: p.color, opacity: p.o }"
        />
      </g>

      <!-- Entrées -->
      <g v-for="n in inNodes" :key="n.label">
        <text :x="28" :y="n.y + 6" class="letter" :class="{ bias: n.bias }">{{ n.label }}</text>
        <circle
          :cx="IN_X" :cy="n.y" :r="R_IN"
          :fill="n.color"
          :fill-opacity="n.fillOp"
          :stroke="n.color"
          stroke-width="2.5"
          :stroke-dasharray="n.bias ? '4 4' : null"
        />
        <text :x="IN_X" :y="n.y + 6" class="value">{{ n.value }}</text>
      </g>

      <!-- La TLU : somme pondérée | fonction seuil -->
      <g>
        <path :d="leftHalf" :fill="zColor" :fill-opacity="zFillOp" />
        <path
          :d="rightHalf"
          class="right-half"
          :fill-opacity="0.06 + 0.84 * glow"
          :filter="glow > 0.1 ? 'url(#tlu-glow)' : null"
        />
        <rect :x="CAP_START" y="100" :width="CAP_END - CAP_START" height="75" rx="37.5" class="capsule" />
        <line x1="320" y1="100" x2="320" y2="175" class="divider" />

        <text x="280" y="127" class="sigma">Σ</text>
        <text x="280" y="154" class="zval">z = {{ zText }}</text>

        <!-- Mini courbe de la fonction seuil -->
        <g :style="{ color: glow > 0.5 ? '#fff' : 'currentColor' }">
          <line x1="331" y1="150" x2="379" y2="150" class="axis" />
          <line x1="355" y1="116" x2="355" y2="156" class="axis dashed" />
          <path d="M331 150 H355 V122 H379" class="step" />
          <circle :cx="dotX" :cy="dotY" r="4.2" class="dot" :style="{ opacity: dotOpacity }" />
        </g>

        <text x="280" y="196" class="small">somme</text>
        <text x="362" y="196" class="small">seuil h</text>
      </g>

      <!-- Sortie -->
      <g>
        <circle
          :cx="O.x" :cy="CY" :r="R_O"
          class="out-node"
          :fill-opacity="0.1 + 0.8 * yLevel"
          :filter="yLevel > 0.1 ? 'url(#tlu-glow)' : null"
        />
        <text
          :x="O.x" :y="CY + 6" class="value italic"
          :style="{ fill: yLevel > 0.5 ? '#fff' : 'currentColor' }"
        >y</text>
        <text :x="O.x" :y="CY + 46" class="small">sortie = {{ yLevel > 0.5 ? 1 : 0 }}</text>
      </g>

      <!-- Verdict -->
      <text
        :x="330" y="226" class="status"
        :style="{ opacity: statusOpacity, fill: fire ? 'var(--cc)' : 'currentColor' }"
      >
        {{ fire ? 'z ≥ 0 : la TLU s\u2019active' : 'z < 0 : la TLU reste à 0' }}
      </text>
    </svg>

    
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
// KaTeX est déjà embarqué par Slidev (sinon : npm i katex)
import katex from 'katex'

/* ---------- Paramètres de la TLU ----------
   Props facultatives : weights (3 poids), bias, examples (liste de [x1, x2, x3]).
   Le composant déroule les exemples en boucle. */
const props = defineProps({
  weights: { type: Array, default: () => [0.8, -0.5, 0.3] },
  bias: { type: Number, default: -0.2 },
  examples: {
    type: Array,
    default: () => [
      [1.0, 0.4, 2.0],
      [0.2, 1.5, 0.5],
      [-0.5, -1.0, 1.0],
      [0.5, 2.0, -1.0],
    ],
  },
})

const CYCLE = 5200 // durée d'un exemple en ms

/* ---------- Géométrie ---------- */
const IN_X = 82
const YS = [40, 105, 170, 235]
const R_IN = 22
const CY = 137.5
const CAP_START = 240
const CAP_END = 400
const CAP_CX_L = 277.5
const END_R = 40.5
const ANGLES = [220, 200, 160, 140]
const O = { x: 505 }
const R_O = 24
const FIRE_X = 360

const clamp = (v) => Math.min(1, Math.max(0, v))
const ease = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2)
const rad = (d) => (d * Math.PI) / 180
const round = (n, d) => Number(n.toFixed(d))

// Formats français pour le SVG : virgule décimale, vrai signe moins
const frFixed = (n, d) => {
  const v = Math.abs(n) < 0.5 * Math.pow(10, -d) ? 0 : n
  const s = Math.abs(v).toFixed(d).replace('.', ',')
  return v < 0 ? '\u2212' + s : s
}

function bez(pts, u) {
  const m = 1 - u
  const [p0, p1, p2, p3] = pts
  return [
    m * m * m * p0[0] + 3 * m * m * u * p1[0] + 3 * m * u * u * p2[0] + u * u * u * p3[0],
    m * m * m * p0[1] + 3 * m * m * u * p1[1] + 3 * m * u * u * p2[1] + u * u * u * p3[1],
  ]
}

// Quatre connexions : x₁, x₂, x₃ et le biais
const geo = YS.map((y, i) => {
  const sx = IN_X + R_IN + 2
  const ex = CAP_CX_L + END_R * Math.cos(rad(ANGLES[i]))
  const ey = CY + END_R * Math.sin(rad(ANGLES[i]))
  const pts = [[sx, y], [sx + 80, y], [ex - 60, ey], [ex, ey]]
  const f = (n) => n.toFixed(1)
  return {
    pts,
    d: `M${f(pts[0][0])} ${f(pts[0][1])} C${f(pts[1][0])} ${f(pts[1][1])}, ${f(pts[2][0])} ${f(pts[2][1])}, ${f(pts[3][0])} ${f(pts[3][1])}`,
  }
})

// Demi-capsules de la TLU
const leftHalf = 'M320 100 H277.5 A37.5 37.5 0 0 0 277.5 175 H320 Z'
const rightHalf = 'M320 100 H362.5 A37.5 37.5 0 0 1 362.5 175 H320 Z'

/* ---------- Horloge ---------- */
const t = ref(0)
const idx = ref(0)
let raf = 0
let t0 = 0

function frame(ts) {
  if (!t0) t0 = ts
  const e = ts - t0
  idx.value = Math.floor(e / CYCLE) % props.examples.length
  t.value = e % CYCLE
  raf = requestAnimationFrame(frame)
}

onMounted(() => {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    // Image fixe : premier exemple, TLU activée
    idx.value = 0
    t.value = 3600
  } else {
    raf = requestAnimationFrame(frame)
  }
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* ---------- Calculs ---------- */
const nEx = computed(() => props.examples.length)
const xs = computed(() => props.examples[idx.value % nEx.value])
const prevXs = computed(() => props.examples[(idx.value - 1 + nEx.value) % nEx.value])

// Contribution de chaque connexion : w_i · x_i, puis le biais
const contribs = computed(() => [
  ...xs.value.map((x, i) => round(x * props.weights[i], 4)),
  props.bias,
])
const zFinal = computed(() => round(contribs.value.reduce((s, c) => s + c, 0), 2))
const fire = computed(() => zFinal.value >= 0)

const T_SEND = 500
const TRAVEL = 1300
const T_FIRE = 2400

const decayLate = computed(() => 1 - clamp((t.value - 4300) / 600))
const decayZ = computed(() => 1 - clamp((t.value - 4700) / 500))

// Valeurs d'entrée affichées : elles glissent de l'exemple précédent au nouveau
const shownXs = computed(() => {
  const k = ease(clamp(t.value / 450))
  return xs.value.map((x, i) => prevXs.value[i] + (x - prevXs.value[i]) * k)
})

// La somme se construit au fur et à mesure que les signaux arrivent
const zShown = computed(
  () =>
    contribs.value.reduce(
      (s, c, i) => s + c * ease(clamp((t.value - (1500 + i * 100)) / 400)),
      0
    ) * decayZ.value
)
const zText = computed(() => frFixed(zShown.value, 2))
const zColor = computed(() => (zShown.value >= 0 ? 'var(--cp)' : 'var(--cn)'))
const zFillOp = computed(() => 0.05 + 0.22 * clamp(Math.abs(zShown.value) / 1.5))

const glow = computed(() =>
  fire.value ? clamp((t.value - T_FIRE) / 200) * (1 - clamp((t.value - 4300) / 500)) : 0
)
const yLevel = computed(() =>
  fire.value ? clamp((t.value - 3000) / 300) * (1 - clamp((t.value - 4500) / 400)) : 0
)
const statusOpacity = computed(
  () => clamp((t.value - 2300) / 250) * (1 - clamp((t.value - 4500) / 400))
)
const panelOpacity = computed(
  () => clamp((t.value - 2100) / 300) * (1 - clamp((t.value - 4600) / 400))
)

// Marqueur sur la courbe seuil
const dotX = computed(() => 355 + (Math.max(-2, Math.min(2, zShown.value)) / 2) * 22)
const dotY = computed(() => (zShown.value >= 0 ? 122 : 150))
const dotOpacity = computed(() => clamp((t.value - 1500) / 200) * decayZ.value)

/* ---------- Éléments du dessin ---------- */
const inNodes = computed(() => [
  ...shownXs.value.map((v, i) => ({
    label: 'x' + '\u2081\u2082\u2083'[i],
    y: YS[i],
    value: frFixed(v, 1),
    color: '#fff',
    fillOp: 0.1 + 0.45 * clamp(Math.abs(v) / 2),
    bias: false,
  })),
  {
    label: 'biais',
    y: YS[3],
    value: '1',
    color: 'var(--cp)',
    fillOp: 0.1,
    bias: true,
  },
])

const allWeights = computed(() => [...props.weights, props.bias])

const branches = computed(() =>
  geo.map((g, i) => ({
    d: g.d,
    neg: allWeights.value[i] < 0,
    width: 1.2 + Math.abs(allWeights.value[i]) * 3.2,
  }))
)

const weightLabels = computed(() =>
  geo.map((g, i) => {
    const [x, y] = bez(g.pts, 0.3)
    const name = i < 3 ? 'w' + '\u2081\u2082\u2083'[i] : 'b'
    return { x, y: y - 9, text: `${name} = ${frFixed(allWeights.value[i], 1)}` }
  })
)

const strandViz = computed(() =>
  geo.map((g, i) => {
    const c = contribs.value[i]
    return {
      d: g.d,
      width: 2 + Math.abs(allWeights.value[i]) * 3,
      color: '#fff',
      prog: ease(clamp((t.value - T_SEND - i * 100) / TRAVEL)),
      op: decayLate.value,
    }
  })
)

const pulses = computed(() => {
  const out = []
  contribs.value.forEach((c, i) => {
    if (Math.abs(c) < 0.005) return
    const u0 = (t.value - T_SEND - i * 100) / TRAVEL
    if (u0 <= 0 || u0 >= 1) return
    const color = '#fff'
    const rBase = 3.2 + 2.4 * clamp(Math.abs(c) / 1.2)
    for (let k = 0; k < 5; k++) {
      const [x, y] = bez(geo[i].pts, ease(clamp(u0 - k * 0.04)))
      out.push({ x, y, r: Math.max(rBase - k * 0.7, 0.8), o: 1 - k * 0.2, color })
    }
  })
  // Impulsion de sortie
  if (fire.value) {
    const u = (t.value - 2550) / 700
    if (u > 0 && u < 1) {
      for (let k = 0; k < 5; k++) {
        const v = ease(clamp(u - k * 0.05))
        const x0 = CAP_END + 4
        const x1 = O.x - R_O - 2
        out.push({ x: x0 + (x1 - x0) * v, y: CY, r: 4.6 - k * 0.75, o: 1 - k * 0.2, color: 'var(--cc)' })
      }
    }
  }
  return out
})

const outProg = computed(() => (fire.value ? ease(clamp((t.value - 2550) / 700)) : 0))
const outOpacity = computed(() => (fire.value ? decayLate.value : 0))

const ripples = computed(() => {
  if (!fire.value) return []
  const out = []
  for (let k = 0; k < 3; k++) {
    const dt = t.value - T_FIRE - k * 180
    if (dt > 0 && dt < 1100) {
      out.push({ r: 40 + ease(dt / 1100) * 62, o: (1 - dt / 1100) * 0.6 })
    }
  }
  return out
})

const sparkles = computed(() => {
  const dt = t.value - T_FIRE
  if (!fire.value || dt < 0 || dt > 1000) return []
  return Array.from({ length: 12 }, (_, i) => {
    const a = rad(i * 30 + (i % 2) * 9)
    const dist = 44 + ease(dt / 1000) * (36 + (i % 3) * 14)
    return {
      x: FIRE_X + dist * Math.cos(a),
      y: CY + dist * Math.sin(a),
      r: 3 - (dt / 1000) * 2,
      o: 1 - dt / 1000,
    }
  })
})

/* ---------- Formules LaTeX ---------- */
const render = (tex) =>
  katex.renderToString(tex, { displayMode: true, throwOnError: false, strict: false })

const texNum = (n) => String(round(n, 2)).replace('.', '{,}')
const texParen = (n) => (n < 0 ? `(${texNum(n)})` : texNum(n))
const texColor = (_c, s) => s

// Formules générales, calculées une seule fois
const texZ = render(String.raw`z = \sum_{i=1}^{3} w_i x_i + b = \mathbf{w}^{\top}\mathbf{x} + b`)
const texH = render(
  String.raw`h(z) = \begin{cases} 1 & \text{si } z \geq 0 \\ 0 & \text{si } z < 0 \end{cases}`
)

// Application numérique : ne change qu'avec l'exemple
const texLive1 = computed(() => {
  const terms = xs.value.map((x, i) =>
    texColor(contribs.value[i], `${texParen(props.weights[i])} \\times ${texParen(x)}`)
  )
  terms.push(texColor(props.bias, texParen(props.bias)))
  return render(`z = ${terms.join(' + ')} = ${texNum(zFinal.value)}`)
})

const texLive2 = computed(() =>
  render(
    `y = h(${texNum(zFinal.value)}) = ${fire.value ? '1' : '0'}`
  )
)
</script>

<style scoped>
.tlu {
  background: #000;
  color: #fff;
  padding: 1.25rem;
  border-radius: 1rem;
  --cp: #fff; /* monochrome */
  --cn: #fff; /* monochrome */
  --cc: #fff; /* monochrome */

  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
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

.base path,
.base line {
  fill: none;
  stroke: currentColor;
  opacity: 0.22;
  stroke-linecap: round;
}

.base line {
  stroke-width: 2;
}

.base path.neg {
  stroke: #fff;
  stroke-dasharray: 6 5;
  opacity: 0.5;
}

.overlay {
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
}

.letter {
  font-size: 18px;
  font-style: italic;
}

.letter.bias {
  font-size: 13px;
  font-style: normal;
  opacity: 0.7;
}

.value {
  font-size: 15px;
  font-weight: 700;
}

.italic {
  font-style: italic;
  font-size: 18px;
}

.small {
  font-size: 13px;
  opacity: 0.7;
}

.capsule {
  fill: none;
  stroke: #fff;
  stroke-width: 2.5;
}

.divider {
  stroke: #fff;
  stroke-width: 1.5;
  opacity: 0.5;
}

.right-half {
  fill: #fff;
}

.sigma {
  font-size: 20px;
  font-weight: 700;
}

.zval {
  font-size: 14px;
  font-weight: 600;
}

.axis {
  stroke: currentColor;
  stroke-width: 1.2;
  opacity: 0.45;
}

.axis.dashed {
  stroke-dasharray: 3 3;
}

.step {
  fill: none;
  stroke: currentColor;
  stroke-width: 2.4;
  stroke-linejoin: round;
}

.dot {
  fill: #fff;
  stroke: #000;
  stroke-width: 1.5;
}

.out-node {
  fill: #fff;
  stroke: #fff;
  stroke-width: 2.5;
}

.status {
  font-size: 15px;
  font-weight: 600;
}

/* Formules */
.formulas {
  width: 100%;
  color: #fff;
  font-size: 0.85rem;
}

.general {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0 1.5rem;
}

.live {
  min-height: 4.2em;
}

.formulas :deep(.katex-display) {
  margin: 0.2em 0;
  overflow-x: auto;
  overflow-y: hidden;
}
</style>
