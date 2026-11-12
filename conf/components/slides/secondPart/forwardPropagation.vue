<template>
  <section class="mlp-forward" aria-label="Propagation avant dans un réseau 784, 16, 16, 10">
    <svg
      class="diagram"
      viewBox="0 0 1000 560"
      role="img"
      aria-label="Dix images de chiffres, de 0 à 9, sont envoyées une à une dans un réseau de neurones 784, 16, 16, 10. Le signal se propage couche après couche et la sortie la plus forte désigne le chiffre prédit."
    >
      <defs>
        <filter id="fw-glow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <clipPath id="fw-strip-clip">
          <rect :x="STRIP.x" :y="STRIP.y" :width="STRIP.w" :height="STRIP.h * scan" />
        </clipPath>
      </defs>

      <!-- ============ En-têtes ============ -->
      <g v-for="(H, i) in HEADERS" :key="'hd' + i" :opacity="hdrOp[i]">
        <text class="hd" :x="H.x" y="28">{{ H.name }}</text>
        <text class="hd-sub" :x="H.x" y="47">{{ H.sub }}</text>
      </g>

      <!-- ============ Galerie des 10 images ============ -->
      <g v-if="ready">
        <g v-for="k in IDX" :key="'g' + k" :opacity="k === stepIdx ? 1 : 0.38">
          <image class="px" :href="imgs[k]" :x="GAL.x" :y="galY(k)" :width="GAL.s" :height="GAL.s" />
          <rect class="frame" :x="GAL.x" :y="galY(k)" :width="GAL.s" :height="GAL.s" />
        </g>
        <rect
          class="sel" rx="4"
          :x="GAL.x - 4" :y="galY(stepIdx) - 4"
          :width="GAL.s + 8" :height="GAL.s + 8"
        />

        <!-- Image courante : sort de la galerie, puis est balayée ligne par ligne -->
        <g :opacity="endFade">
          <image
            class="px" :href="imgs[stepIdx]"
            :x="bigPos.x" :y="bigPos.y" :width="bigPos.s" :height="bigPos.s"
          />
          <rect
            class="dim"
            :x="BIG.x" :y="BIG.y" :width="BIG.s" :height="BIG.s * scan"
          />
          <rect class="frame big" :x="bigPos.x" :y="bigPos.y" :width="bigPos.s" :height="bigPos.s" />
          <line
            v-if="scan > 0 && scan < 1" class="scan"
            :x1="BIG.x - 8" :x2="BIG.x + BIG.s + 8"
            :y1="BIG.y + BIG.s * scan" :y2="BIG.y + BIG.s * scan"
            filter="url(#fw-glow)"
          />
        </g>

        <!-- Flèche image → vecteur -->
        <path class="arrow" :opacity="clamp((t - 400) / 300) * endFade" d="M 224 300 L 238 300 M 233 295 L 238 300 L 233 305" />

        <!-- Vecteur x : les 784 valeurs, lues ligne par ligne -->
        <g :opacity="endFade">
          <rect class="strip-bg" :x="STRIP.x" :y="STRIP.y" :width="STRIP.w" :height="STRIP.h" />
          <image
            class="px" :href="strips[stepIdx]"
            :x="STRIP.x" :y="STRIP.y" :width="STRIP.w" :height="STRIP.h"
            preserveAspectRatio="none" clip-path="url(#fw-strip-clip)"
          />
          <rect
            v-if="scan > 0 && scan < 1" class="band"
            :x="STRIP.x - 3" :width="STRIP.w + 6"
            :y="STRIP.y + STRIP.h * scan - STRIP.h / 28" :height="STRIP.h / 28"
          />
          <rect class="frame" :x="STRIP.x" :y="STRIP.y" :width="STRIP.w" :height="STRIP.h" />
        </g>
      </g>

      <!-- ============ Connexions au repos ============ -->
      <g class="wires">
        <path
          v-for="(e, k) in WIRES" :key="'w' + k"
          :d="e.d" :stroke-opacity="e.o"
        />
      </g>

      <!-- Connexions illuminées au passage du signal (cyan = contribution positive, orange = négative) -->
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

      <!-- ============ Neurones des couches 1 à 3 ============ -->
      <g v-for="n in NODES" :key="'n' + n.l + '-' + n.k">
        <circle
          v-if="flash[n.l - 1] > 0.02"
          class="flash" :cx="n.x" :cy="n.y" :r="n.r + 2 + flash[n.l - 1] * 9"
          :opacity="flash[n.l - 1] * 0.9" filter="url(#fw-glow)"
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
          v-if="n.l < 3" class="node-text" :x="n.x" :y="n.y + 3.2"
          :style="{ fill: Math.abs(val(n)) > 0.6 ? '#050505' : '#fff' }"
        >{{ fr(val(n), 1) }}</text>
      </g>

      <!-- ============ Sortie : images 0 à 9, probabilités, gagnant ============ -->
      <g v-if="ready">
        <g v-for="k in IDX" :key="'out' + k">
          <image
            class="px" :href="imgs[k]"
            :x="OUT.thumbX" :y="outY(k) - 14" width="28" height="28"
            :opacity="lerp(0.75, k === win ? 1 : 0.3, winOp)"
          />
          <rect class="frame" :x="OUT.thumbX" :y="outY(k) - 14" width="28" height="28" :opacity="lerp(0.75, k === win ? 1 : 0.3, winOp)" />
          <rect class="bar-bg" :x="OUT.barX" :y="outY(k) - 5" :width="OUT.barW" height="10" rx="5" />
          <rect
            class="bar" :x="OUT.barX" :y="outY(k) - 5"
            :width="Math.max(0, OUT.barW * outShown[k])" height="10" rx="5"
            :filter="k === win && winOp > 0.1 ? 'url(#fw-glow)' : null"
          />
          <text class="pct" :x="OUT.barX + OUT.barW + 7" :y="outY(k) + 4" :opacity="rev[2]">
            {{ fr(outShown[k] * 100, 0) }} %
          </text>
        </g>
        <g :opacity="winOp">
          <circle class="halo" :cx="OUT.x" :cy="outY(win)" r="26" />
          <circle class="winner" :cx="OUT.x" :cy="outY(win)" r="22" filter="url(#fw-glow)" />
          <rect class="winner-box" :x="OUT.thumbX - 3" :y="outY(win) - 17" width="34" height="34" rx="3" />
        </g>
      </g>

      <!-- Légende de l'étape en cours -->
      <text class="cap" x="500" y="548">{{ caption }}</text>
    </svg>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* =====================================================================
   1. Les dix images (28 × 28, valeurs dans [0, 1])
   ===================================================================== */
const PI = Math.PI
const arc = (cx, cy, rx, ry, a0, a1, n = 32) =>
  Array.from({ length: n + 1 }, (_, i) => {
    const a = a0 + ((a1 - a0) * i) / n
    return [cx + rx * Math.cos(a), cy + ry * Math.sin(a)]
  })

// Tracés des chiffres, en coordonnées de la grille 28 × 28
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
   2. Le réseau 784 → 16 → 16 → 10 : calcul réel de la propagation avant
      h¹ = tanh(W¹x)   h² = tanh(W²h¹)   ŷ = softmax(W³h² + b)
   Poids W¹ et W² aléatoires (graine fixe). W³ est calculée en forme close
   sur ces dix images pour que la démo aboutisse à la bonne classe.
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

// Ajustement de la dernière couche (régression ridge) : logit visé = 5 pour la bonne classe
const HM = DIGITS.map((px) => [...hidden(px).h2, 1])
const K = HM.map((a, i) => HM.map((b, j) => dot(a, b) + (i === j ? 1e-3 : 0)))
const TARGET = IDX.map((i) => IDX.map((j) => (i === j ? 5 : 0)))
const ALPHA = solve(K, TARGET)
const W3 = Array.from({ length: 17 }, (_, i) =>
  Array.from({ length: 10 }, (_, j) => HM.reduce((s, row, n) => s + row[i] * ALPHA[n][j], 0))
)

function forward(px) {
  const { h1, h2 } = hidden(px)
  const z = IDX.map((j) => h2.reduce((s, h, i) => s + h * W3[i][j], W3[16][j]))
  const m = Math.max(...z)
  const e = z.map((v) => Math.exp(v - m))
  const s = e.reduce((a, v) => a + v, 0)
  return { px, h1, h2, y: e.map((v) => v / s) }
}
const NET = DIGITS.map(forward)

/* =====================================================================
   3. Géométrie
   ===================================================================== */
const GAL = { x: 22, s: 38 }
const galY = (k) => 78 + k * 44
const BIG = { x: 92, y: 240, s: 120 }
const STRIP = { x: 246, y: 80, w: 24, h: 440 }
const XS = [null, 470, 640]
const OUT = { x: 790, thumbX: 818, barX: 858, barW: 88 }
const CY = 300
const yHid = (k) => CY + (k - 7.5) * 27.5
const outY = (k) => CY + (k - 4.5) * 44
const yRow = (r) => STRIP.y + ((r + 0.5) / 28) * STRIP.h

const NODES = [
  ...Array.from({ length: 16 }, (_, k) => ({ l: 1, k, x: XS[1], y: yHid(k), r: 10.5 })),
  ...Array.from({ length: 16 }, (_, k) => ({ l: 2, k, x: XS[2], y: yHid(k), r: 10.5 })),
  ...IDX.map((k) => ({ l: 3, k, x: OUT.x, y: outY(k), r: 14 })),
]

const HEADERS = [
  { x: 41, name: 'Images', sub: '0 à 9' },
  { x: 152, name: 'Image', sub: '28 × 28' },
  { x: 258, name: 'Entrée', sub: 'x ∈ ℝ⁷⁸⁴' },
  { x: XS[1], name: 'Cachée 1', sub: 'h¹ ∈ ℝ¹⁶' },
  { x: XS[2], name: 'Cachée 2', sub: 'h² ∈ ℝ¹⁶' },
  { x: OUT.x, name: 'Sortie', sub: 'ŷ ∈ ℝ¹⁰' },
  { x: OUT.barX + OUT.barW / 2, name: 'Probabilité', sub: 'softmax' },
]

// Connexions : couche 0 = 28 « lignes » de l'image → h¹ ; puis h¹ → h² ; h² → sortie
const SRC_N = [28, 16, 16]
const DST_N = [16, 16, 10]
const EDGES = [0, 1, 2].map((l) => {
  const list = []
  for (let j = 0; j < DST_N[l]; j++) {
    for (let s = 0; s < SRC_N[l]; s++) {
      const x1 = l === 0 ? STRIP.x + STRIP.w : XS[l] + 12
      const y1 = l === 0 ? yRow(s) : yHid(s)
      const x2 = (l === 2 ? OUT.x - 14 : XS[l + 1] - 12) - 2
      const y2 = l === 2 ? outY(j) : yHid(j)
      const xm = (x1 + x2) / 2
      list.push({
        l, s, j,
        pts: [[x1, y1], [xm, y1], [xm, y2], [x2, y2]],
        d: `M ${x1} ${y1} C ${xm} ${y1}, ${xm} ${y2}, ${x2} ${y2}`,
      })
    }
  }
  return list
})

// Opacité au repos : proportionnelle à la norme du poids
const wNorm = [
  (j, s) => Math.hypot(...W1[j].slice(s * 28, s * 28 + 28)),
  (j, s) => Math.abs(W2[j][s]),
  (j, s) => Math.abs(W3[s][j]),
]
EDGES.forEach((E, l) => {
  const raw = E.map((e) => wNorm[l](e.j, e.s))
  const m = Math.max(...raw)
  E.forEach((e, n) => { e.o = Number((0.05 + 0.2 * (raw[n] / m)).toFixed(3)) })
})
const WIRES = EDGES.flat()

// Contribution de chaque connexion pour chaque image, normalisée par couche dans [−1, 1]
const CONTR = NET.map(({ px, h1, h2 }) => {
  const raw = [new Array(28 * 16), new Array(16 * 16), new Array(16 * 10)]
  for (let j = 0; j < 16; j++) {
    for (let r = 0; r < 28; r++) {
      let s = 0
      for (let c = 0; c < 28; c++) s += px[r * 28 + c] * W1[j][r * 28 + c]
      raw[0][j * 28 + r] = s
    }
    for (let i = 0; i < 16; i++) raw[1][j * 16 + i] = h1[i] * W2[j][i]
  }
  for (let j = 0; j < 10; j++) for (let i = 0; i < 16; i++) raw[2][j * 16 + i] = h2[i] * W3[i][j]
  return raw.map((a) => {
    const m = Math.max(...a.map(Math.abs)) || 1
    return a.map((v) => v / m)
  })
})

/* =====================================================================
   4. Outils
   ===================================================================== */
const POS = '#67e8f9'
const NEG = '#fb923c'
const clamp = (v) => Math.min(1, Math.max(0, v))
const ease = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2)
const lerp = (a, b, k) => a + (b - a) * k

function bez(pts, u) {
  const m = 1 - u
  const [p0, p1, p2, p3] = pts
  return [
    m * m * m * p0[0] + 3 * m * m * u * p1[0] + 3 * m * u * u * p2[0] + u * u * u * p3[0],
    m * m * m * p0[1] + 3 * m * m * u * p1[1] + 3 * m * u * u * p2[1] + u * u * u * p3[1],
  ]
}

const fr = (n, d) => {
  const v = Math.abs(n) < 0.5 * Math.pow(10, -d) ? 0 : n
  const s = Math.abs(v).toFixed(d).replace('.', ',')
  return v < 0 ? '\u2212' + s : s
}

/* =====================================================================
   5. Images sous forme de data-URL (canvas) : 10 vignettes + 10 « codes-barres » du vecteur
   ===================================================================== */
const ready = ref(false)
const imgs = ref([])
const strips = ref([])

function toURL(w, h, get) {
  const c = document.createElement('canvas')
  c.width = w
  c.height = h
  const ctx = c.getContext('2d')
  const im = ctx.createImageData(w, h)
  for (let i = 0; i < w * h; i++) {
    const g = Math.round(get(i) * 255)
    im.data[i * 4] = g
    im.data[i * 4 + 1] = g
    im.data[i * 4 + 2] = g
    im.data[i * 4 + 3] = 255
  }
  ctx.putImageData(im, 0, 0)
  return c.toDataURL()
}

/* =====================================================================
   6. Horloge : un chiffre toutes les DUR ms, en boucle
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
  imgs.value = DIGITS.map((px) => toURL(28, 28, (i) => px[i]))
  strips.value = DIGITS.map((px) =>
    toURL(1, STRIP.h, (y) => {
      const a = Math.floor((y * 784) / STRIP.h)
      const b = Math.max(a + 1, Math.floor(((y + 1) * 784) / STRIP.h))
      return Math.max(...px.slice(a, b))
    })
  )
  ready.value = true

  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    t.value = 5800 // image fixe : propagation terminée, classe prédite visible
  } else {
    raf = requestAnimationFrame(frame)
  }
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* =====================================================================
   7. Chronologie d'un exemple (ms)
   ===================================================================== */
const S = [1800, 3250, 4450]        // départ des impulsions couche l → l+1
const STAG = [22, 26, 26]           // décalage entre sources
const DRAW = 650                    // durée d'une impulsion
const REV = [3080, 4320, 5520]      // instant où h¹, h², ŷ prennent leur valeur
const WIN = [[0, 1e9], [0, 1900], [500, 2000], [1800, 3400], [3250, 4500], [4450, 6000], [4450, 6000]]
const ACT_WIN = [0, 1, 2].map((l) => [S[l], REV[l] + 750])

const step = computed(() => NET[stepIdx.value])
const endFade = computed(() => 1 - clamp((t.value - (DUR - 300)) / 300))
const rev = computed(() => REV.map((r) => ease(clamp((t.value - r) / 300))))
const scan = computed(() => clamp((t.value - 500) / 1200))

const bigPos = computed(() => {
  const e = ease(clamp(t.value / 500))
  const k = stepIdx.value
  return { x: lerp(GAL.x, BIG.x, e), y: lerp(galY(k), BIG.y, e), s: lerp(GAL.s, BIG.s, e) }
})

const hdrOp = computed(() =>
  WIN.map(([a, b]) => 0.45 + 0.55 * clamp((t.value - a) / 250) * (1 - clamp((t.value - b) / 300)))
)

// Valeurs affichées dans les neurones : h¹, h², ŷ
const actsShown = computed(() =>
  [step.value.h1, step.value.h2, step.value.y].map((a, l) => a.map((v) => v * rev.value[l] * endFade.value))
)
const outShown = computed(() => actsShown.value[2])
const val = (n) => actsShown.value[n.l - 1][n.k]

const flash = computed(() =>
  REV.map((r) => clamp((t.value - r) / 200) * (1 - clamp((t.value - r - 200) / 500)))
)

/* Connexions illuminées et impulsions de la couche en cours */
const active = computed(() => {
  const T = t.value
  const d = stepIdx.value
  const res = { ov: [], pu: [] }
  for (let l = 0; l < 3; l++) {
    if (T < ACT_WIN[l][0] || T > ACT_WIN[l][1]) continue
    const fade = 1 - clamp((T - REV[l] - 200) / 500)
    const E = EDGES[l]
    const C = CONTR[d][l]
    for (let n = 0; n < E.length; n++) {
      const rel = C[n]
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
const win = computed(() => {
  const y = step.value.y
  return y.indexOf(Math.max(...y))
})
const winOp = computed(() => clamp((t.value - 5600) / 300) * endFade.value)

const caption = computed(() => {
  const T = t.value
  if (T < 500) return `Image n° ${stepIdx.value} · 28 × 28 = 784 pixels`
  if (T < 1800) return 'Aplatissement : lecture ligne par ligne → vecteur x de 784 valeurs'
  if (T < 3250) return 'Couche cachée 1 :  h¹ = tanh(W¹ x)'
  if (T < 4450) return 'Couche cachée 2 :  h² = tanh(W² h¹)'
  if (T < 5600) return 'Sortie :  ŷ = softmax(W³ h²)'
  const p = step.value.y[win.value]
  return `Prédiction : ${win.value}   ·   probabilité ${fr(p * 100, 0)} %`
})
</script>

<style scoped>
.mlp-forward {
  box-sizing: border-box;
  width: 100%;
  color: #fff;
  background: #050505;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

.diagram {
  display: block;
  width: 100%;
  height: auto;
}
.diagram text {
  text-anchor: middle;
}

/* En-têtes */
.hd {
  fill: #fff;
  font: italic 16px Georgia, 'Times New Roman', serif;
}
.hd-sub {
  fill: rgba(255, 255, 255, 0.58);
  font: italic 13px Georgia, 'Times New Roman', serif;
}
.cap {
  fill: rgba(255, 255, 255, 0.85);
  font: italic 17px Georgia, 'Times New Roman', serif;
}

/* Images */
.px {
  image-rendering: pixelated;
}
.frame {
  fill: none;
  stroke: rgba(255, 255, 255, 0.45);
  stroke-width: 1;
}
.frame.big {
  stroke: rgba(255, 255, 255, 0.8);
  stroke-width: 1.4;
}
.sel {
  fill: none;
  stroke: #fff;
  stroke-width: 1.6;
}
.dim {
  fill: rgba(5, 5, 5, 0.62);
}
.scan {
  stroke: #67e8f9;
  stroke-width: 2;
}
.band {
  fill: rgba(103, 232, 249, 0.45);
}
.strip-bg {
  fill: #000;
}
.arrow {
  fill: none;
  stroke: rgba(255, 255, 255, 0.7);
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
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
.node-text {
  font: italic 9px Georgia, serif;
}
.flash {
  fill: none;
  stroke: #fff;
  stroke-width: 1.2;
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
.diagram .pct {
  text-anchor: start;
  fill: rgba(255, 255, 255, 0.7);
  font: 11px ui-monospace, monospace;
}
.winner {
  fill: none;
  stroke: #fff;
  stroke-width: 1.8;
}
.winner-box {
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

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; }
}
</style>