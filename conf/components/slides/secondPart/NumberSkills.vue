<template>
  <section
    class="mini-net"
    aria-label="Réseau de neurones : une image en entrée, deux couches cachées, une sortie et une mesure d'erreur. Les notations apparaissent avec les clics de la diapositive."
  >
    <svg
      class="diagram"
      :viewBox="`0 0 ${VB_W} ${H}`"
      role="img"
      :aria-label="`Une image de chiffre est envoyée à travers deux neurones cachés puis un neurone de sortie. La sortie est comparée à l'étiquette réelle par une fonction de coût dont la valeur, entre 0 et 1, monte dans une jauge.`"
    >
      <defs>
        <filter id="mn-glow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <!-- Connexions au repos -->
      <g class="wires">
        <path v-for="(e, k) in WIRES" :key="'w' + k" :d="e.d" :stroke-opacity="e.o" />
      </g>

      <!-- Légendes des connexions (poids) -->
      <g v-if="SHOW_WEIGHTS">
        <text
          v-for="(e, k) in WIRES" :key="'wt' + k"
          v-show="e.text"
          class="weight-text" :x="e.mx" :y="CY - 10"
        >{{ e.text }}</text>
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

      <!-- Image d'entrée -->
      <g :opacity="imgOp">
        <rect
          class="img-frame"
          :x="IMG.x - 4" :y="IMG.y - 4" :width="IMG.size + 8" :height="IMG.size + 8" rx="2"
        />
        <rect
          v-for="(p, i) in PIXELS" :key="'px' + i"
          :x="p.x" :y="p.y" :width="IMG.s + 0.4" :height="IMG.s + 0.4"
          fill="#fff" :fill-opacity="p.o"
        />
      </g>

      <!-- Neurones : cachée 1, cachée 2, sortie -->
      <g v-for="n in NODES" :key="'n' + n.l">
        <circle
          v-if="flash[n.l] > 0.02"
          class="flash" :cx="n.x" :cy="CY" :r="R + 2 + flash[n.l] * 9"
          :opacity="flash[n.l] * 0.9" filter="url(#mn-glow)"
        />
        <circle
          class="ring" :cx="n.x" :cy="CY" :r="R + 2.5"
          :stroke="val(n) < -0.02 ? NEG : '#fff'"
          :stroke-dasharray="val(n) < -0.02 ? '3 3' : null"
        />
        <circle class="core" :cx="n.x" :cy="CY" :r="R" />
        <circle
          :cx="n.x" :cy="CY" :r="R" fill="#fff"
          :fill-opacity="clamp(Math.abs(val(n))) * 0.95"
        />
        <text
          class="node-text" :x="n.x" :y="CY + 4.7"
          :style="{ fill: Math.abs(val(n)) > 0.6 ? '#050505' : '#fff' }"
        >{{ fr(val(n), 2) }}</text>
      </g>

      <!-- Barre de sortie : ŷ de 0 à 1 -->
      <g>
        <rect class="bar-bg" :x="BAR.x" :y="CY - 5" :width="BAR.w" height="10" rx="5" />
        <rect
          class="bar" :x="BAR.x" :y="CY - 5"
          :width="Math.max(0, BAR.w * clamp(actsShown[2]))" height="10" rx="5"
          :filter="actsShown[2] > 0.05 ? 'url(#mn-glow)' : null"
        />
      </g>

      <!-- Étiquette réelle y : anneau épais, plein si y = 1 -->
      <g :opacity="0.4 + 0.6 * errOp">
        <circle
          v-if="flash[4] > 0.02"
          class="flash" :cx="X.e" :cy="CY" :r="19 + flash[4] * 9"
          :opacity="flash[4] * 0.9" filter="url(#mn-glow)"
        />
        <circle class="target" :cx="X.e" :cy="CY" r="22" :opacity="errOp" />
        <circle class="core" :cx="X.e" :cy="CY" r="17" />
        <circle
          :cx="X.e" :cy="CY" r="17" fill="#fff"
          :fill-opacity="LABEL === 1 ? errOp * 0.95 : 0"
        />
        <text
          class="node-text" :x="X.e" :y="CY + 4.7"
          :style="{ fill: LABEL === 1 && errOp > 0.5 ? '#050505' : '#fff' }"
        >{{ errOp > 0.5 ? LABEL : 0 }}</text>
      </g>

      <!-- Coût : jauge de 0 (vide) à 1 (pleine) -->
      <g>
        <line
          class="link" :x1="X.e + 26" :x2="GAUGE.x" :y1="CY" :y2="CY"
          :opacity="gaugeP"
        />
        <rect class="gauge-bg" :x="GAUGE.x" :y="GAUGE.y" :width="GAUGE.w" :height="GAUGE.h" rx="4" />
        <rect
          class="gauge" :x="GAUGE.x" :width="GAUGE.w" rx="4"
          :y="GAUGE.y + GAUGE.h - gaugeH" :height="gaugeH"
          :filter="gaugeH > 2 ? 'url(#mn-glow)' : null"
        />
        <text class="tick" :x="GAUGE.x - 8" :y="GAUGE.y + 4">1</text>
        <text class="tick" :x="GAUGE.x - 8" :y="GAUGE.y + GAUGE.h + 4">0</text>
        <text
          class="gauge-value"
          :x="GAUGE.x + GAUGE.w + 8" :y="gaugeValueY"
          :opacity="gaugeP"
        >{{ fr(loss * gaugeP, 2) }}</text>
      </g>

      <!-- Noms des colonnes -->
      <g>
        <text v-for="(c, i) in COLUMN_LABELS" :key="'lab' + i" class="layer-label" :x="c.x" :y="H - 28">
          {{ c.text }}
        </text>
      </g>

      <!-- Notations qui apparaissent au clic (voir MATHS dans le script) -->
      <g class="maths">
        <text
          v-for="(m, i) in MATHS" :key="'m' + i"
          :class="m.cls" :x="m.x" :y="m.y"
          :style="{ opacity: shown(m) ? 1 : 0 }"
        >
          <tspan v-for="(s, j) in m.segs" :key="j" :dy="s.dy" :class="{ sup: s.sup }">{{ s.t }}</tspan>
        </text>
      </g>

    </svg>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useSlideContext } from '@slidev/client'

/* =====================================================================
   ★ 1. CONFIGURATION — c'est ici que tu modifies l'exemple ★
   ===================================================================== */

// Image donnée au réseau (0 à 9)
const DIGIT = 7

// Question posée à la sortie : « est-ce un <TARGET_DIGIT> ? »
// L'étiquette réelle vaut 1 si DIGIT === TARGET_DIGIT, sinon 0.
// Ici l'image est un 7, mais le réseau répond à la question « est-ce un 1 ? ».
const TARGET_DIGIT = 1

// Forme que le premier neurone caché cherche dans l'image (ses 784 poids en dérivent)
const TEMPLATE_DIGIT = 7
// Valeur de z (avant activation) quand l'image ressemble exactement au modèle
const IMAGE_GAIN = 2.5

// Poids et biais du reste du réseau (un seul neurone par couche)
const B1 = 0       // biais du neurone caché 1
const W2 = 1.1     // poids caché 1 → caché 2
const B2 = 0       // biais du neurone caché 2
const W3 = 1.2     // poids caché 2 → sortie
const B3 = -0.4    // biais de la sortie

// Activation des couches cachées : 'tanh', 'sigmoid' ou 'relu'.
// La sortie est toujours une sigmoïde : ŷ reste entre 0 et 1, donc le coût aussi.
const HIDDEN_ACT = 'tanh'

// Fonction de coût, toujours comprise entre 0 et 1 :
//   'squared'  → C = (ŷ − y)²
//   'absolute' → C = |ŷ − y|
const COST = 'squared'

// Affichage
const SHOW_WEIGHTS = true

// Rythme de l'animation (ms)
const STEP_DELAY = 1300         // délai entre deux étapes
const PULSE_DURATION = 650      // durée d'une impulsion
const HOLD = 1800               // pause une fois le coût affiché

// Couleurs
const POS = '#67e8f9'           // contribution positive
const NEG = '#fb923c'           // contribution négative

// Noms sous les colonnes
const TEXTS = {
  image: 'Image 28 × 28',
  h1: 'Cachée 1',
  h2: 'Cachée 2',
  out: 'Sortie ŷ',
  label: 'Étiquette y',
  cost: 'Coût',
}

/* =====================================================================
   ★ 1 bis. ÉTAPES AU CLIC — les notations qui s'ajoutent une à une ★

   Chaque ligne a :
     from  : l'étape (numéro de clic) où elle apparaît
     until : l'étape où elle disparaît, remplacée par une autre (facultatif)
     row   : 0 = ligne la plus proche, 1 = juste en dessous, etc.
     text  : le texte. Écris un exposant ainsi : a^{(1)}  →  a⁽¹⁾

   Pour ajouter une étape, ajoute simplement des lignes avec un `from`
   plus grand (par exemple 5 pour la dérivée du coût) : le nombre de clics
   se règle tout seul.
   ===================================================================== */
const LAST = 0 // exposant de la sortie ; les exposants décroissent vers elle

// De l'image vers la sortie, les exposants sont 3, 2, 1, 0.
const LAYER_LINES = (l) => [
  { from: 1, until: 2, row: 0, text: `a^{(${l})}` },                                    // clic 1
  { from: 2, row: 0, text: `a^{(${l})} = σ(z^{(${l})})` },                              // clic 2
  { from: 3, row: 1, text: `z^{(${l})} = w^{(${l})}a^{(${l + 1})} + b^{(${l})}` },      // clic 3
]

// L'image porte l'exposant immédiatement supérieur à celui de la première couche.
const IMAGE_LINES = [
  { from: 1, row: 0, text: `a^{(${LAST + 3})} = x` },
]

// Sous la jauge : la formule du coût, réécrite avec a⁽³⁾ au clic 4
const COST_LINES = {
  squared: [
    { from: 0, until: 4, text: 'C = (ŷ − y)^{2}' },
    { from: 4, text: `C = (a^{(${LAST})} − y)^{2}` },
  ],
  absolute: [
    { from: 0, until: 4, text: 'C = |ŷ − y|' },
    { from: 4, text: `C = |a^{(${LAST})} − y|` },
  ],
}

/* =====================================================================
   2. Les dix images (28 × 28), dessinées à partir de tracés
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

const DIGITS = STROKES.map(renderDigit)

/* =====================================================================
   3. Réseau : image (784) → 1 → 1 → 1, puis coût
      z¹ = W¹·x + b¹    h¹ = f(z¹)
      z² = w²·h¹ + b²   h² = f(z²)
      z³ = w³·h² + b³   ŷ  = sigmoïde(z³)       C = coût(ŷ, y)
   ===================================================================== */
const ACTS = {
  tanh: Math.tanh,
  sigmoid: (z) => 1 / (1 + Math.exp(-z)),
  relu: (z) => Math.min(1, Math.max(0, z)),
}
const sigmoid = ACTS.sigmoid
const hiddenAct = ACTS[HIDDEN_ACT]

// Les 784 poids de W¹ : le modèle choisi, recentré, puis mis à l'échelle
const tpl = DIGITS[TEMPLATE_DIGIT]
const tplMean = tpl.reduce((s, v) => s + v, 0) / tpl.length
const tplNorm = tpl.reduce((s, v) => s + (v - tplMean) * v, 0) || 1
const W1 = tpl.map((v) => ((v - tplMean) * IMAGE_GAIN) / tplNorm)

const COSTS = {
  squared: (y, target) => (y - target) * (y - target),
  absolute: (y, target) => Math.abs(y - target),
}

const IMAGE = DIGITS[DIGIT]
const LABEL = DIGIT === TARGET_DIGIT ? 1 : 0

const zImg = W1.reduce((s, w, i) => s + w * IMAGE[i], 0)  // contribution de l'image
const h1 = hiddenAct(zImg + B1)
const h2 = hiddenAct(W2 * h1 + B2)
const yHat = sigmoid(W3 * h2 + B3)
const ACT_VALUES = [h1, h2, yHat]                          // valeurs des trois neurones
const LOSS = COSTS[COST](yHat, LABEL)                      // entre 0 et 1

/* =====================================================================
   4. Géométrie
   ===================================================================== */
const VB_W = 940
const H = 400
const CY = 185
const R = 24

const IMG = { x: 30, y: CY - 77, s: 5.5, size: 154 }
const X = { h1: 300, h2: 430, o: 560, e: 770 }
const BAR = { x: 600, w: 90 }
const GAUGE = { x: 850, y: CY - 130, w: 28, h: 260 }

const PIXELS = IMAGE
  .map((v, idx) => ({
    x: IMG.x + (idx % 28) * IMG.s,
    y: IMG.y + Math.floor(idx / 28) * IMG.s,
    o: Number(v.toFixed(2)),
  }))
  .filter((p) => p.o > 0.03)

const NODES = [
  { l: 1, x: X.h1 },
  { l: 2, x: X.h2 },
  { l: 3, x: X.o },
]

const COLUMN_LABELS = [
  { x: IMG.x + IMG.size / 2, text: TEXTS.image },
  { x: X.h1, text: TEXTS.h1 },
  { x: X.h2, text: TEXTS.h2 },
  { x: X.o + 20, text: TEXTS.out },
  { x: X.e, text: TEXTS.label },
  { x: GAUGE.x + GAUGE.w / 2, text: TEXTS.cost },
]

// Quatre connexions horizontales : image → h¹, h¹ → h², h² → ŷ, ŷ → étiquette
function line(x1, x2, extra) {
  const third = (x2 - x1) / 3
  return {
    pts: [[x1, CY], [x1 + third, CY], [x1 + 2 * third, CY], [x2, CY]],
    d: `M ${x1} ${CY} L ${x2} ${CY}`,
    mx: (x1 + x2) / 2,
    ...extra,
  }
}
const EDGES = [
  line(IMG.x + IMG.size + 8, X.h1 - R - 3, { o: 0.3, text: '784 poids' }),
  line(X.h1 + R + 3, X.h2 - R - 3, { o: 0.3, text: fr(W2, 2) }),
  line(X.h2 + R + 3, X.o - R - 3, { o: 0.3, text: fr(W3, 2) }),
  line(BAR.x + BAR.w + 8, X.e - 26, { o: 0.22, text: '' }),
]
const WIRES = EDGES

// Contribution de chaque connexion (signe → couleur, intensité → épaisseur)
const CONTRIB = [zImg, h1 * W2, h2 * W3, yHat]

/* =====================================================================
   5. Outils
   ===================================================================== */
function clamp(v) { return Math.min(1, Math.max(0, v)) }
function ease(u) { return u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2 }

function bez(pts, u) {
  const m = 1 - u
  const [p0, p1, p2, p3] = pts
  return [
    m * m * m * p0[0] + 3 * m * m * u * p1[0] + 3 * m * u * u * p2[0] + u * u * u * p3[0],
    m * m * m * p0[1] + 3 * m * m * u * p1[1] + 3 * m * u * u * p2[1] + u * u * u * p3[1],
  ]
}

// Nombre au format français (virgule, vrai signe moins)
function fr(n, d) {
  const v = Math.abs(n) < 0.5 * Math.pow(10, -d) ? 0 : n
  const s = Math.abs(v).toFixed(d).replace('.', ',')
  return v < 0 ? '\u2212' + s : s
}

// Découpe « a^{(1)} = σ(z^{(1)}) » en morceaux normaux / exposants pour <tspan>
function tex(str) {
  const out = []
  let last = 0
  for (const m of str.matchAll(/\^\{([^}]*)\}/g)) {
    if (m.index > last) out.push({ t: str.slice(last, m.index), sup: false })
    out.push({ t: m[1], sup: true })
    last = m.index + m[0].length
  }
  if (last < str.length) out.push({ t: str.slice(last), sup: false })
  // dy : on monte pour l'exposant, on redescend juste après
  return out.map((s, i) => ({ ...s, dy: s.sup ? -5 : out[i - 1]?.sup ? 5 : 0 }))
}

/* =====================================================================
   6. Notations affichées au clic
   ===================================================================== */
const ROW_GAP = 24
const MATHS = [
  // image : a⁽⁰⁾ = x, sous l'image
  ...IMAGE_LINES.map((m) => ({
    ...m, x: IMG.x + IMG.size / 2, y: IMG.y + IMG.size + 30 + m.row * ROW_GAP,
    cls: m.row ? 'math sub' : 'math',
  })),
  // neurones : sous chaque cercle
  ...NODES.flatMap((n) =>
    LAYER_LINES(LAST + 3 - n.l).map((m) => ({
      ...m, x: n.x, y: CY + R + 34 + m.row * ROW_GAP,
      cls: m.row ? 'math sub' : 'math',
    }))
  ),
  // coût : sous la jauge
  ...COST_LINES[COST].map((m) => ({ ...m, x: GAUGE.x + GAUGE.w / 2, y: H - 10, cls: 'formula' })),
].map((m) => ({ ...m, segs: tex(m.text) }))

const MAX_STAGE = Math.max(...MATHS.map((m) => m.from))
const { $clicks } = useSlideContext()
const stage = computed(() => Math.max(0, Math.min($clicks.value, MAX_STAGE)))
const shown = (m) => stage.value >= m.from && (m.until == null || stage.value < m.until)
const hint = computed(() =>
  stage.value >= MAX_STAGE
    ? 'Dernière étape — clic suivant : diapositive suivante'
    : `Clique pour continuer (${stage.value}/${MAX_STAGE})`
)

/* =====================================================================
   7. Chronologie (ms)
   Étapes : 0 image · 1 cachée 1 · 2 cachée 2 · 3 sortie · 4 étiquette + coût
   ===================================================================== */
const S = EDGES.map((_, l) => 700 + l * STEP_DELAY)       // départ de chaque impulsion
const REV = [300, ...S.map((s) => s + PULSE_DURATION + 400)] // moment où chaque étape est « connue »
const ACT_WIN = S.map((s, l) => [s, REV[l + 1] + 750])
const DUR = REV[4] + HOLD

const t = ref(0)
let raf = 0
let t0 = 0
const FINAL_TIME = REV[4] + 800

function frame(ts) {
  if (!t0) t0 = ts
  t.value = Math.min(ts - t0, FINAL_TIME)
  if (t.value >= FINAL_TIME) return
  raf = requestAnimationFrame(frame)
}

onMounted(() => {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) t.value = REV[4] + 1000 // image fixe : tout est calculé
  else raf = requestAnimationFrame(frame)
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* =====================================================================
   8. États réactifs
   ===================================================================== */
const endFade = computed(() => 1 - clamp((t.value - (DUR - 300)) / 300))
const rev = computed(() => REV.map((r) => ease(clamp((t.value - r) / 300))))

const imgOp = computed(() => rev.value[0] * endFade.value)
const actsShown = computed(() => ACT_VALUES.map((v, i) => v * rev.value[i + 1] * endFade.value))
const val = (n) => actsShown.value[n.l - 1]

const flash = computed(() =>
  REV.map((r) => clamp((t.value - r) / 200) * (1 - clamp((t.value - r - 200) / 500)))
)

const active = computed(() => {
  const T = t.value
  const res = { ov: [], pu: [] }
  for (let l = 0; l < EDGES.length; l++) {
    if (T < ACT_WIN[l][0] || T > ACT_WIN[l][1]) continue
    const fade = 1 - clamp((T - REV[l + 1] - 200) / 500)
    const rel = CONTRIB[l]
    const a = clamp(Math.abs(rel))
    if (a < 0.05) continue
    const u = (T - S[l]) / PULSE_DURATION
    const prog = ease(clamp(u))
    const c = rel > 0 ? POS : NEG
    res.ov.push({ d: EDGES[l].d, prog, w: 1.4 + 2.6 * a, op: fade * (0.35 + 0.65 * a), c })
    if (u > 0 && u < 1) {
      const [x, y] = bez(EDGES[l].pts, prog)
      res.pu.push({ x, y, r: 2.2 + 2.6 * a, c })
    }
  }
  return res
})

/* Étiquette et coût */
const loss = LOSS
const errOp = computed(() => rev.value[4] * endFade.value)
const gaugeP = computed(() => ease(clamp((t.value - REV[4] - 100) / 700)) * endFade.value)
const gaugeH = computed(() => GAUGE.h * clamp(loss) * gaugeP.value)
const gaugeValueY = computed(() =>
  Math.min(GAUGE.y + GAUGE.h - 4, Math.max(GAUGE.y + 12, GAUGE.y + GAUGE.h - gaugeH.value + 5))
)
</script>

<style scoped>
.mini-net {
  box-sizing: border-box;
  width: 100%;
  color: #fff;
  background: #050505;
  display: flex;
  justify-content: center;
  align-items: center;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.diagram {
  display: flex;
  width: 100%;
  height: 100vh;
}

/* Image */
.img-frame {
  fill: none;
  stroke: rgba(255, 255, 255, 0.45);
  stroke-width: 1;
}

/* Connexions */
.wires path {
  fill: none;
  stroke: #fff;
  stroke-width: 0.8;
}
.overlays path {
  fill: none;
  stroke-linecap: round;
}
.weight-text {
  text-anchor: middle;
  font: italic 11px Georgia, 'Times New Roman', serif;
  fill: rgba(255, 255, 255, 0.55);
  pointer-events: none;
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
  font: italic 13px Georgia, 'Times New Roman', serif;
  pointer-events: none;
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

/* Étiquette et coût */
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
.tick {
  text-anchor: end;
  font: italic 11px Georgia, 'Times New Roman', serif;
  fill: rgba(255, 255, 255, 0.5);
}
.gauge-value {
  text-anchor: start;
  font: italic 15px Georgia, 'Times New Roman', serif;
  fill: #fff;
}

/* Légendes */
.layer-label {
  text-anchor: middle;
  font: italic 12px Georgia, 'Times New Roman', serif;
  fill: rgba(255, 255, 255, 0.6);
}

/* Notations au clic */
.math,
.formula {
  text-anchor: middle;
  font: italic 13px Georgia, 'Times New Roman', serif;
  pointer-events: none;
  transition: opacity 0.45s ease;
}
.math {
  fill: #fff;
}
.math.sub {
  font-size: 12px;
  fill: rgba(255, 255, 255, 0.7);
}
.formula {
  font-size: 12px;
  fill: rgba(255, 255, 255, 0.55);
}
.sup {
  font-size: 70%;
}

.hint {
  text-anchor: start;
  font: italic 11px Georgia, 'Times New Roman', serif;
  fill: rgba(255, 255, 255, 0.4);
  pointer-events: none;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>