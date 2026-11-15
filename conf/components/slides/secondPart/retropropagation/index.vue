<template>
  <section
    class="chain"
    aria-label="Dérivée en chaîne de la fonction de coût par rapport aux paramètres de la dernière couche, puis mise à jour de ces paramètres. Les étapes apparaissent avec les clics de la diapositive."
  >
    <svg
      class="diagram"
      :viewBox="`0 0 ${VB_W} ${H}`"
      role="img"
      aria-label="Réseau de neurones : une image traverse deux neurones cachés puis un neurone de sortie, comparé à l'étiquette réelle par une fonction de coût. Le signal d'erreur remonte vers les paramètres de la dernière couche."
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
          v-show="weightText[k]"
          class="weight-text" :x="e.mx" :y="CY - 10"
        >{{ weightText[k] }}</text>
      </g>

      <!-- Dernière couche : ses paramètres w et b (valeurs en direct) -->
      <g>
        <rect
          class="frame"
          :x="FRAME.x1" :y="FRAME.y1" :width="FRAME.x2 - FRAME.x1" :height="FRAME.y2 - FRAME.y1" rx="8"
        />
        <text class="param-tag" :x="FRAME.x1" :y="FRAME.y1 - 8">
          <tspan v-for="(s, j) in paramTag" :key="j" :dy="s.dy" :class="{ sup: s.sup }">{{ s.t }}</tspan>
        </text>
      </g>

      <!-- Connexions illuminées -->
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
      <g>
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
          class="node-text" :x="n.x" :y="CY + 4.5"
          :style="{ fill: Math.abs(val(n)) > 0.6 ? '#050505' : '#fff' }"
        >{{ fr(val(n), 2) }}</text>
      </g>

      <!-- Éclats du signal d'erreur sur les neurones -->
      <g>
        <circle
          v-for="(f, i) in active.fl" :key="'fl' + i"
          class="flash" :cx="f.x" :cy="CY" :r="R + 2 + f.f * 9"
          :stroke="f.c" :opacity="f.f * 0.9" filter="url(#mn-glow)"
        />
      </g>

      <!-- Barre de sortie : a de 0 à 1 -->
      <g>
        <rect class="bar-bg" :x="BAR.x" :y="CY - 5" :width="BAR.w" height="10" rx="5" />
        <rect
          class="bar" :x="BAR.x" :y="CY - 5"
          :width="Math.max(0, BAR.w * clamp(yCur))" height="10" rx="5"
          :filter="yCur > 0.05 ? 'url(#mn-glow)' : null"
        />
      </g>

      <!-- Étiquette réelle y -->
      <g>
        <circle class="target" :cx="X.e" :cy="CY" r="20" />
        <circle class="core" :cx="X.e" :cy="CY" r="15" />
        <circle :cx="X.e" :cy="CY" r="15" fill="#fff" :fill-opacity="LABEL === 1 ? 0.95 : 0" />
        <text
          class="node-text" :x="X.e" :y="CY + 4.5"
          :style="{ fill: LABEL === 1 ? '#050505' : '#fff' }"
        >{{ LABEL }}</text>
      </g>

      <!-- Coût : jauge de 0 (vide) à 1 (pleine) -->
      <g>
        <line class="link" :x1="X.e + 24" :x2="GAUGE.x" :y1="CY" :y2="CY" />
        <rect class="gauge-bg" :x="GAUGE.x" :y="GAUGE.y" :width="GAUGE.w" :height="GAUGE.h" rx="4" />
        <rect
          class="gauge" :x="GAUGE.x" :width="GAUGE.w" rx="4"
          :y="GAUGE.y + GAUGE.h - gaugeH" :height="gaugeH"
          :filter="gaugeH > 2 ? 'url(#mn-glow)' : null"
        />
        <text class="tick" :x="GAUGE.x - 8" :y="GAUGE.y + 4">1</text>
        <text class="tick" :x="GAUGE.x - 8" :y="GAUGE.y + GAUGE.h + 4">0</text>
        <text class="gauge-value" :x="GAUGE.x + GAUGE.w + 8" :y="gaugeValueY">{{ fr(lossCur, 2) }}</text>
      </g>

      <!-- Noms des colonnes -->
      <g>
        <text v-for="(c, i) in COLUMN_LABELS" :key="'lab' + i" class="layer-label" :x="c.x" :y="H - 30">
          {{ c.text }}
        </text>
      </g>

      <!-- Notations (fixes ou apparaissant au clic) -->
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

    <!-- Dérivation, ligne après ligne -->
    <div class="deriv">
      <div v-for="(row, r) in ROWS" :key="r" class="drow" :style="{ gridTemplateColumns: row.cols }">
        <div v-for="(cell, c) in row.cells" :key="c" class="dcell">
          <div v-for="(it, i) in cell" :key="i" class="dline" :style="lineStyle(it)" v-html="it.html" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useSlideContext } from '@slidev/client'

/* =====================================================================
   ★ 1. CONFIGURATION — c'est ici que tu modifies l'exemple ★
   ===================================================================== */

// Même réseau que la diapositive précédente
const DIGIT = 7
const TARGET_DIGIT = 1          // étiquette y = 1 si DIGIT === TARGET_DIGIT, sinon 0
const TEMPLATE_DIGIT = 7
const IMAGE_GAIN = 2.5

const B1 = 0
const W2 = 1.1
const B2 = 0
const W3 = 1.2                  // w de la dernière couche
const B3 = -0.4                 // b de la dernière couche

const HIDDEN_ACT = 'tanh'       // 'tanh' | 'sigmoid' | 'relu' (la sortie reste une sigmoïde)
const COST = 'squared'          // 'squared' → (a − y)²   |   'absolute' → |a − y|

// Pas de la descente de gradient (η)
const ETA = 1.5

// Affichage
const SHOW_WEIGHTS = true

// Exposants : on compte depuis la sortie.
// sortie = 0, cachée 2 = 1, cachée 1 = 2, image = 3
const LAST = 0

// Animation (ms)
const PULSE_DURATION = 650      // durée d'une impulsion
const HOLD_LINE = 800           // temps pendant lequel la ligne reste allumée
const UPD_DELAY = 500           // délai avant que les paramètres bougent (clic 5)
const UPD_DURATION = 1200       // durée du changement des paramètres

// Couleurs
const POS = '#67e8f9'           // signal avant, contribution positive
const NEG = '#fb923c'           // signal avant, contribution négative
const GRAD = '#fbbf24'          // signal d'erreur qui remonte (dérivées)

// Noms sous les colonnes
const TEXTS = {
  image: 'Image 28 × 28',
  h1: 'Cachée 1',
  h2: 'Cachée 2',
  out: 'Sortie',
  label: 'Étiquette y',
  cost: 'Coût',
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
   3. Réseau, puis dérivées de la dernière couche
      z = w·a⁽¹⁾ + b     a = σ(z)     C = coût(a, y)
      ∂C/∂w = ∂z/∂w · ∂a/∂z · ∂C/∂a        ∂C/∂b = ∂z/∂b · ∂a/∂z · ∂C/∂a
   ===================================================================== */
const ACTS = {
  tanh: Math.tanh,
  sigmoid: (z) => 1 / (1 + Math.exp(-z)),
  relu: (z) => Math.min(1, Math.max(0, z)),
}
const sigmoid = ACTS.sigmoid
const hiddenAct = ACTS[HIDDEN_ACT]

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

// Passe avant
const zImg = W1.reduce((s, w, i) => s + w * IMAGE[i], 0)
const h1 = hiddenAct(zImg + B1)
const h2 = hiddenAct(W2 * h1 + B2)
const yHat = sigmoid(W3 * h2 + B3)

// Les trois facteurs de la chaîne
const dCda = COST === 'squared' ? 2 * (yHat - LABEL) : Math.sign(yHat - LABEL)  // ∂C/∂a
const dadz = yHat * (1 - yHat)                                                  // ∂a/∂z = σ′(z)
const dzdw = h2                                                                 // ∂z/∂w
const dzdb = 1                                                                  // ∂z/∂b

// Gradient et mise à jour
const dCdw = dzdw * dadz * dCda
const dCdb = dzdb * dadz * dCda
const W3new = W3 - ETA * dCdw
const B3new = B3 - ETA * dCdb
const yNew = sigmoid(W3new * h2 + B3new)

/* =====================================================================
   4. Géométrie
   ===================================================================== */
const VB_W = 940
const H = 250
const CY = 118
const R = 20

const IMG = { x: 30, y: CY - 56, s: 4, size: 112 }
const X = { h1: 260, h2: 385, o: 510, e: 715 }
const BAR = { x: 548, w: 80 }
const GAUGE = { x: 830, y: CY - 85, w: 24, h: 170 }
const FRAME = { x1: X.h2 + R + 8, x2: X.o + R + 8, y1: CY - R - 34, y2: CY + R + 14 }

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

// Connexions : 0 image → h¹, 1 h¹ → h², 2 h² → sortie, 3 sortie → étiquette
function line(x1, x2, extra) {
  const third = (x2 - x1) / 3
  const pts = [[x1, CY], [x1 + third, CY], [x1 + 2 * third, CY], [x2, CY]]
  return {
    pts,
    rpts: pts.slice().reverse(),
    d: `M ${x1} ${CY} L ${x2} ${CY}`,
    rd: `M ${x2} ${CY} L ${x1} ${CY}`,   // sens inverse, pour le signal d'erreur
    mx: (x1 + x2) / 2,
    ...extra,
  }
}
const EDGES = [
  line(IMG.x + IMG.size + 8, X.h1 - R - 3, { o: 0.3 }),
  line(X.h1 + R + 3, X.h2 - R - 3, { o: 0.3 }),
  line(X.h2 + R + 3, X.o - R - 3, { o: 0.3 }),
  line(BAR.x + BAR.w + 8, X.e - 24, { o: 0.22 }),
]
const WIRES = EDGES

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

// SVG : découpe « a^{(1)} = σ(z^{(1)}) » en morceaux normaux / exposants pour <tspan>
function tex(str) {
  const out = []
  let last = 0
  for (const m of str.matchAll(/\^\{([^}]*)\}/g)) {
    if (m.index > last) out.push({ t: str.slice(last, m.index), sup: false })
    out.push({ t: m[1], sup: true })
    last = m.index + m[0].length
  }
  if (last < str.length) out.push({ t: str.slice(last), sup: false })
  return out.map((s, i) => ({ ...s, dy: s.sup ? -5 : out[i - 1]?.sup ? 5 : 0 }))
}

// HTML : petit « LaTeX » pour le panneau de dérivées
//   \frac{haut}{bas}   a^{(1)}   \num{…} (dérivée, ambre)   \new{…} (nouvelle valeur, cyan)
function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') }
function group(s, i) {
  let depth = 0
  let j = i
  for (; j < s.length; j++) {
    if (s[j] === '{') depth++
    else if (s[j] === '}' && --depth === 0) break
  }
  return [s.slice(i + 1, j), j + 1]
}
function toHtml(s) {
  let out = ''
  let i = 0
  while (i < s.length) {
    if (s.startsWith('\\frac', i)) {
      const [n, i1] = group(s, i + 5)
      const [d, i2] = group(s, i1)
      out += `<span class="fr"><span class="fr-n">${toHtml(n)}</span><span class="fr-d">${toHtml(d)}</span></span>`
      i = i2
    } else if (s.startsWith('\\num', i)) {
      const [v, i1] = group(s, i + 4)
      out += `<span class="val">${toHtml(v)}</span>`
      i = i1
    } else if (s.startsWith('\\new', i)) {
      const [v, i1] = group(s, i + 4)
      out += `<span class="val new">${toHtml(v)}</span>`
      i = i1
    } else if (s[i] === '^' && s[i + 1] === '{') {
      const [v, i1] = group(s, i + 1)
      out += `<sup>${toHtml(v)}</sup>`
      i = i1
    } else {
      out += esc(s[i])
      i++
    }
  }
  return out
}

/* =====================================================================
   ★ 6. LES CINQ CLICS ★
   Chaque ligne a un `from` : le clic où elle apparaît. Le texte s'écrit
   en mini-LaTeX (voir toHtml ci-dessus).
   ===================================================================== */
const a0 = `a^{(${LAST})}`        // sortie
const a1 = `a^{(${LAST + 1})}`    // cachée 2
const z0 = `z^{(${LAST})}`
const w0 = `w^{(${LAST})}`
const b0 = `b^{(${LAST})}`

const item = (from, tex_) => ({ from, html: toHtml(tex_) })

// Clic 1 : ∂C/∂a
const d1 = item(1, COST === 'squared'
  ? `\\frac{∂C}{∂${a0}} = 2(${a0} − y) = \\num{${fr(dCda, 2)}}`
  : `\\frac{∂C}{∂${a0}} = signe(${a0} − y) = \\num{${fr(dCda, 2)}}`)

// Clic 2 : ∂a/∂z
const d2 = item(2, `\\frac{∂${a0}}{∂${z0}} = σ′(${z0}) = ${a0}(1 − ${a0}) = \\num{${fr(dadz, 2)}}`)

// Clic 3 : ∂z/∂w et ∂z/∂b
const d3a = item(3, `\\frac{∂${z0}}{∂${w0}} = ${a1} = \\num{${fr(dzdw, 2)}}`)
const d3b = item(3, `\\frac{∂${z0}}{∂${b0}} = \\num{${fr(dzdb, 0)}}`)

// Clic 4 : la chaîne
const chain = (p) => `\\frac{∂${z0}}{∂${p}} · \\frac{∂${a0}}{∂${z0}} · \\frac{∂C}{∂${a0}}`
const cw = item(4, `\\frac{∂C}{∂${w0}} = ${chain(w0)} = \\num{${fr(dCdw, 2)}}`)
const cb = item(4, `\\frac{∂C}{∂${b0}} = ${chain(b0)} = \\num{${fr(dCdb, 2)}}`)

// Clic 5 : on modifie les paramètres
const uw = item(5, `${w0} ← ${w0} − η \\frac{∂C}{∂${w0}} = ${fr(W3, 2)} − ${fr(ETA, 2)} × ${fr(dCdw, 2)} = \\new{${fr(W3new, 2)}}`)
const ub = item(5, `${b0} ← ${b0} − η \\frac{∂C}{∂${b0}} = ${fr(B3, 2)} − ${fr(ETA, 2)} × ${fr(dCdb, 2)} = \\new{${fr(B3new, 2)}}`)
const note = item(5, `η = ${fr(ETA, 2)} : le pas de la descente. Le coût passe de \\num{${fr(COSTS[COST](yHat, LABEL), 2)}} à \\new{${fr(COSTS[COST](yNew, LABEL), 2)}}.`)

const ROWS = [
  { cols: '0.9fr 1.3fr 0.9fr', cells: [[d1], [d2], [d3a, d3b]] },
  { cols: '1fr 1fr', cells: [[cw], [cb]] },
  { cols: '1fr 1fr', cells: [[uw], [ub]] },
  { cols: '1fr', cells: [[note]] },
]

// Notations sur le schéma : fixes (from: 0) ou liées à un clic.
// Les lignes en ambre sont les dérivées, posées sur la partie du réseau concernée.
const ROW_GAP = 20
const SCHEMA_GRAD = [
  // clic 1 : sur la liaison sortie → coût
  { from: 1, x: EDGES[3].mx, y: CY - 12, text: `∂C/∂${a0}` },
  // clic 2 : au-dessus du neurone de sortie
  { from: 2, x: X.o, y: CY - R - 12, text: `∂${a0}/∂${z0}` },
  // clic 3 : sur la connexion qui porte w, puis, au clic 4, ∂C/∂w
  { from: 3, until: 4, x: EDGES[2].mx, y: CY + 18, text: `∂${z0}/∂${w0} = ${a1}` },
  { from: 4, x: EDGES[2].mx, y: CY + 18, text: `∂C/∂${w0}` },
]

const MATHS = [
  // image
  { from: 0, x: IMG.x + IMG.size / 2, y: IMG.y + IMG.size + 26, cls: 'math', text: `a^{(${LAST + 3})} = x` },
  // neurones
  ...NODES.flatMap((n) => {
    const e = LAST + 3 - n.l
    return [
      { from: 0, x: n.x, y: CY + R + 28, cls: 'math', text: `a^{(${e})} = σ(z^{(${e})})` },
      { from: 0, x: n.x, y: CY + R + 28 + ROW_GAP, cls: 'math sub', text: `z^{(${e})} = w^{(${e})}a^{(${e + 1})} + b^{(${e})}` },
    ]
  }),
  // coût
  {
    from: 0, x: GAUGE.x + GAUGE.w / 2, y: H - 12, cls: 'formula',
    text: COST === 'squared' ? `C = (${a0} − y)^{2}` : `C = |${a0} − y|`,
  },
  // dérivées sur le schéma
  ...SCHEMA_GRAD.map((m) => ({ ...m, cls: 'grad-label' })),
].map((m) => ({ ...m, segs: tex(m.text) }))

const MAX_STAGE = Math.max(...MATHS.map((m) => m.from), ...ROWS.flatMap((r) => r.cells.flat().map((i) => i.from)))
const UPDATE_STAGE = 5          // à partir de ce clic, les paramètres changent

const { $clicks } = useSlideContext()
const stage = computed(() => Math.max(0, Math.min($clicks.value, MAX_STAGE)))
const shown = (m) => stage.value >= m.from && (m.until == null || stage.value < m.until)

// Ligne du panneau : invisible avant son clic, pleine à son clic, atténuée ensuite
function lineStyle(it) {
  const s = stage.value
  return {
    opacity: s < it.from ? 0 : s === it.from ? 1 : 0.5,
    transform: s < it.from ? 'translateY(6px)' : 'none',
  }
}

/* =====================================================================
   7. Signal d'erreur : ce qui se passe sur le schéma à chaque clic
      edge  : connexion parcourue (0 à 3)      dir : -1 = remonte, +1 = avance
      node  : éclat sur le neurone (1 à 3)     delay : en ms après le clic
   ===================================================================== */
const PULSES = {
  1: [{ edge: 3, dir: -1, delay: 0 }],
  2: [{ node: 3, delay: 0 }],
  3: [{ edge: 2, dir: -1, delay: 0 }],
  4: [
    { edge: 3, dir: -1, delay: 0 },
    { node: 3, delay: 650 },
    { edge: 2, dir: -1, delay: 900 },
  ],
  // Clic 5 : les paramètres changent, puis le signal repart vers l'avant
  5: [
    { edge: 2, dir: 1, delay: 1700, fwd: true },
    { node: 3, delay: 2350 },
    { edge: 3, dir: 1, delay: 2600, fwd: true },
  ],
}
const FWD_REL = { 2: h2 * W3new, 3: yNew }  // signe du signal avant après la mise à jour

/* =====================================================================
   8. Horloge et paramètres animés
   ===================================================================== */
const reduce = typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

const now = ref(0)
const upd = ref(0)              // 0 = paramètres d'origine, 1 = paramètres mis à jour
let raf = 0
let stageT0 = 0
let updFrom = 0
let updTarget = 0
let updT0 = 0

function retarget(s) {
  stageT0 = performance.now()
  const target = s >= UPDATE_STAGE ? 1 : 0
  if (target !== updTarget) {
    updFrom = upd.value
    updTarget = target
    updT0 = stageT0 + (target === 1 ? UPD_DELAY : 0)
  }
  if (reduce) { upd.value = target; updFrom = target }
}

function frame() {
  const n = performance.now()
  now.value = n
  if (upd.value !== updTarget) {
    const u = ease(clamp((n - updT0) / UPD_DURATION))
    upd.value = u >= 1 ? updTarget : updFrom + (updTarget - updFrom) * u
  }
  raf = requestAnimationFrame(frame)
}

watch(stage, (s) => retarget(s))

onMounted(() => {
  updTarget = stage.value >= UPDATE_STAGE ? 1 : 0
  upd.value = updTarget
  updFrom = updTarget
  stageT0 = performance.now()
  if (!reduce) raf = requestAnimationFrame(frame)
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* =====================================================================
   9. États réactifs
   ===================================================================== */
const Wcur = computed(() => W3 + (W3new - W3) * upd.value)
const Bcur = computed(() => B3 + (B3new - B3) * upd.value)
const yCur = computed(() => sigmoid(Wcur.value * h2 + Bcur.value))
const lossCur = computed(() => COSTS[COST](yCur.value, LABEL))
const valuesCur = computed(() => [h1, h2, yCur.value])
const val = (n) => valuesCur.value[n.l - 1]

const weightText = computed(() => ['784 poids', fr(W2, 2), fr(Wcur.value, 2), ''])
const paramTag = computed(() => tex(`${w0} = ${fr(Wcur.value, 2)} · ${b0} = ${fr(Bcur.value, 2)}`))

const gaugeH = computed(() => GAUGE.h * clamp(lossCur.value))
const gaugeValueY = computed(() =>
  Math.min(GAUGE.y + GAUGE.h - 4, Math.max(GAUGE.y + 12, GAUGE.y + GAUGE.h - gaugeH.value + 5))
)

const active = computed(() => {
  const res = { ov: [], pu: [], fl: [] }
  if (reduce) return res
  const T = now.value - stageT0
  for (const p of PULSES[stage.value] || []) {
    const since = T - p.delay
    if (since < 0) continue

    if (p.edge != null) {
      const fade = 1 - clamp((since - PULSE_DURATION - HOLD_LINE) / 500)
      if (fade <= 0) continue
      const e = EDGES[p.edge]
      const u = since / PULSE_DURATION
      const prog = ease(clamp(u))
      const rel = FWD_REL[p.edge] ?? 1
      const c = p.fwd ? (rel > 0 ? POS : NEG) : GRAD
      const w = p.fwd ? 1.4 + 2.6 * clamp(Math.abs(rel)) : 3
      res.ov.push({ d: p.dir < 0 ? e.rd : e.d, prog, w, op: fade * 0.9, c })
      if (u > 0 && u < 1) {
        const [x, y] = bez(p.dir < 0 ? e.rpts : e.pts, prog)
        res.pu.push({ x, y, r: 3.6, c })
      }
    }

    if (p.node != null) {
      const f = clamp(since / 200) * (1 - clamp((since - 200) / 600))
      if (f > 0.02) res.fl.push({ x: NODES[p.node - 1].x, f, c: stage.value >= UPDATE_STAGE ? POS : GRAD })
    }
  }
  return res
})
</script>

<style scoped>
.chain {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  color: #fff;
  background: #050505;
  user-select: none;
}

.diagram {
  display: block;
  width: 100%;
  height: auto;
  flex: none;
}

/* ---- Schéma ---- */
.img-frame {
  fill: none;
  stroke: rgba(255, 255, 255, 0.45);
  stroke-width: 1;
}
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
.frame {
  fill: none;
  stroke: rgba(255, 255, 255, 0.35);
  stroke-width: 1;
  stroke-dasharray: 4 4;
}
.param-tag {
  text-anchor: start;
  font: italic 12px Georgia, 'Times New Roman', serif;
  fill: rgba(255, 255, 255, 0.85);
}

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
  stroke-width: 1.4;
}
.node-text {
  text-anchor: middle;
  font: italic 12px Georgia, 'Times New Roman', serif;
  pointer-events: none;
}

.bar-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.4);
  stroke-width: 1;
}
.bar {
  fill: #fff;
}

.target {
  fill: none;
  stroke: #fff;
  stroke-width: 2.2;
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
  font: italic 14px Georgia, 'Times New Roman', serif;
  fill: #fff;
}

.layer-label {
  text-anchor: middle;
  font: italic 12px Georgia, 'Times New Roman', serif;
  fill: rgba(255, 255, 255, 0.6);
}

/* Notations sur le schéma */
.math,
.formula,
.grad-label {
  text-anchor: middle;
  font: italic 12px Georgia, 'Times New Roman', serif;
  pointer-events: none;
  transition: opacity 0.45s ease;
}
.math {
  fill: rgba(255, 255, 255, 0.9);
}
.math.sub {
  font-size: 11px;
  fill: rgba(255, 255, 255, 0.6);
}
.formula {
  fill: rgba(255, 255, 255, 0.55);
}
.grad-label {
  font-size: 10.5px;
  fill: #fbbf24;
}
.sup {
  font-size: 70%;
}

/* ---- Panneau de dérivées ---- */
.deriv {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  padding: 4px 28px 14px;
  min-height: 0;
}
.drow {
  display: grid;
  column-gap: 20px;
}
.dcell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
}
.dline {
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  font: italic 15px/1.2 Georgia, 'Times New Roman', serif;
  transition: opacity 0.45s ease, transform 0.45s ease;
}
.dline :deep(sup) {
  font-size: 0.7em;
  line-height: 0;
  vertical-align: super;
}
.dline :deep(.fr) {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  vertical-align: middle;
  margin: 0 0.25em;
  line-height: 1.25;
}
.dline :deep(.fr-n) {
  padding: 0 0.25em 0.1em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.85);
}
.dline :deep(.fr-d) {
  padding: 0.1em 0.25em 0;
}
.dline :deep(.val) {
  margin-left: 0.3em;
  color: #fbbf24;
}
.dline :deep(.val.new) {
  color: #67e8f9;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>