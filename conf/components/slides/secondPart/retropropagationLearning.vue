<template>
  <section class="mlp-forward" aria-label="Entraînement d'un réseau de neurones et minimisation de la fonction de coût">
    <svg
      class="diagram"
      viewBox="0 0 1000 562"
      role="img"
      aria-label="Réseau de neurones 784, 16, 16, 10 avec courbe de minimisation de la fonction de coût en dessous."
    >
      <defs>
        <filter id="fw-glow" x="-120%" y="-120%" width="340%" height="340%">
          <feGaussianBlur stdDeviation="3.2" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <clipPath id="fw-strip-clip">
          <rect :x="STRIP.x" :y="STRIP.y" :width="STRIP.w" :height="STRIP.h * scan" />
        </clipPath>
        <linearGradient id="loss-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#67e8f9" stop-opacity="0.32" />
          <stop offset="100%" stop-color="#67e8f9" stop-opacity="0.0" />
        </linearGradient>
      </defs>

      <!-- ============ En-têtes ============ -->
      <g v-for="(H, i) in HEADERS" :key="'hd' + i" :opacity="hdrOp[i]">
        <text class="hd" :x="H.x" y="22">{{ H.name }}</text>
        <text class="hd-sub" :x="H.x" y="38">{{ H.sub }}</text>
      </g>

      <!-- ============ Galerie des 10 images ============ -->
      <g v-if="ready">
        <g v-for="k in IDX" :key="'g' + k" :opacity="k === stepIdx ? 1 : 0.35">
          <image class="px" :href="imgs[k]" :x="GAL.x" :y="galY(k)" :width="GAL.s" :height="GAL.s" />
          <rect class="frame" :x="GAL.x" :y="galY(k)" :width="GAL.s" :height="GAL.s" />
        </g>
        <rect
          class="sel" rx="3"
          :x="GAL.x - 3" :y="galY(stepIdx) - 3"
          :width="GAL.s + 6" :height="GAL.s + 6"
        />

        <!-- Image courante -->
        <g>
          <image
            class="px" :href="imgs[stepIdx]"
            :x="bigPos.x" :y="bigPos.y" :width="bigPos.s" :height="bigPos.s"
          />
          <rect class="frame big" :x="bigPos.x" :y="bigPos.y" :width="bigPos.s" :height="bigPos.s" />
          <line
            v-if="scan > 0 && scan < 1" class="scan"
            :x1="BIG.x - 6" :x2="BIG.x + BIG.s + 6"
            :y1="BIG.y + BIG.s * scan" :y2="BIG.y + BIG.s * scan"
            filter="url(#fw-glow)"
          />
        </g>

        <!-- Flèche image → vecteur -->
        <path
          class="arrow"
          :opacity="clamp((t - 380) / 280)"
          d="M 196 225 L 210 225 M 205 220 L 210 225 L 205 230"
        />

        <!-- Vecteur x (784 pixels) -->
        <g>
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

      <!-- ============ Connexions ============ -->
      <g class="wires" shape-rendering="optimizeSpeed">
        <path v-for="(e, k) in WIRES" :key="'w' + k" :d="e.d" :stroke-opacity="e.o" />
      </g>

      <g class="overlays">
        <path
          v-for="(o, k) in active.ov" :key="'ov' + k"
          :d="o.d"
          :stroke-dasharray="`${o.len} ${o.len + 10}`"
          :stroke-dashoffset="o.len * (1 - o.prog)"
          :stroke="o.c" :stroke-width="o.w"
          :opacity="o.op"
        />
      </g>

      <g class="back-overlays">
        <path
          v-for="(o, k) in active.bov" :key="'bov' + k"
          :d="o.d"
          :stroke-dasharray="`${o.len} ${o.len + 10}`"
          :stroke-dashoffset="o.len * (1 - o.prog)"
          :stroke="o.c" :stroke-width="o.w"
          :opacity="o.op"
        />
      </g>

      <g class="particles">
        <circle v-for="(p, i) in active.pu" :key="'pu' + i" :cx="p.x" :cy="p.y" :r="p.r" :fill="p.c" />
        <circle v-for="(p, i) in active.bpu" :key="'bpu' + i" :cx="p.x" :cy="p.y" :r="p.r" :fill="p.c" />
      </g>

      <!-- ============ Neurones ============ -->
      <g v-for="n in NODES" :key="'n' + n.l + '-' + n.k">
        <circle
          v-if="flash[n.l - 1] > 0.02"
          class="flash" :cx="n.x" :cy="n.y" :r="n.r + 2 + flash[n.l - 1] * 7"
          :opacity="flash[n.l - 1] * 0.85"
        />
        <circle
          v-if="backFlash[n.l - 1] > 0.02"
          class="back-flash" :cx="n.x" :cy="n.y" :r="n.r + 2 + backFlash[n.l - 1] * 8"
          :opacity="backFlash[n.l - 1] * 0.85"
        />
        <circle
          class="ring" :cx="n.x" :cy="n.y" :r="n.r + 2"
          :stroke="val(n) < -0.02 ? NEG : '#fff'"
          :stroke-dasharray="val(n) < -0.02 ? '2.5 2.5' : null"
        />
        <circle class="core" :cx="n.x" :cy="n.y" :r="n.r" />
        <circle
          :cx="n.x" :cy="n.y" :r="n.r" fill="#fff"
          :fill-opacity="clamp(Math.abs(val(n))) * 0.95"
        />
        <text
          v-if="n.l < 3" class="node-text" :x="n.x" :y="n.y + 2.8"
          :style="{ fill: Math.abs(val(n)) > 0.6 ? '#050505' : '#fff' }"
        >{{ fr(val(n), 1) }}</text>
      </g>

      <!-- ============ Sortie ============ -->
      <g v-if="ready">
        <g v-for="k in IDX" :key="'out' + k">
          <image
            class="px" :href="imgs[k]"
            :x="OUT.thumbX" :y="outY(k) - 11" width="22" height="22"
            :opacity="lerp(0.75, k === stepIdx || k === win ? 1 : 0.3, winOp)"
          />
          <rect
            class="frame" :x="OUT.thumbX" :y="outY(k) - 11" width="22" height="22"
            :opacity="lerp(0.75, k === stepIdx || k === win ? 1 : 0.3, winOp)"
          />
          <rect class="bar-bg" :x="OUT.barX" :y="outY(k) - 4" :width="OUT.barW" height="8" rx="4" />
          <rect
            class="bar" :x="OUT.barX" :y="outY(k) - 4"
            :width="Math.max(0, OUT.barW * outShown[k])" height="8" rx="4"
            :style="{ fill: k === stepIdx ? '#67e8f9' : '#ffffff' }"
            :filter="k === win && winOp > 0.1 ? 'url(#fw-glow)' : null"
          />
          <text class="pct" :x="OUT.barX + OUT.barW + 6" :y="outY(k) + 3.5" :opacity="rev[2]">
            {{ fr(outShown[k] * 100, 0) }} %
          </text>
        </g>

        <g :opacity="winOp">
          <circle
            class="winner" :cx="OUT.x" :cy="outY(win)" r="17"
            :style="{ stroke: win === stepIdx ? '#67e8f9' : '#fb923c' }"
            filter="url(#fw-glow)"
          />
          <rect
            class="winner-box" :x="OUT.thumbX - 2.5" :y="outY(stepIdx) - 13.5" width="27" height="27" rx="3"
            style="stroke: #67e8f9"
          />
        </g>
      </g>

      <!-- Légende étape -->
      <text class="cap" x="500" y="416">{{ caption }}</text>

      <!-- =====================================================================
           COURBE DE MINIMISATION DE LA FONCTION DE COÛT (SOUS LE RÉSEAU)
           ===================================================================== -->
      <g class="loss-section">
        <line x1="22" y1="428" x2="978" y2="428" stroke="rgba(255,255,255,0.14)" stroke-width="1" />

        <!-- Résumé mathématique à gauche -->
        <g transform="translate(24, 442)">
          <text class="loss-hd" x="0" y="13">Minimisation de la fonction de coût</text>
          <text class="loss-eq" x="0" y="34">ℒ(ŷ, y) = − ∑ yᵢ log(ŷᵢ)</text>

          <g transform="translate(0, 46)">
            <rect x="0" y="0" width="232" height="36" rx="7" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.12)" />
            <text class="m-lbl" x="10" y="13">Coût ℒ</text>
            <text
              class="m-val" x="10" y="29"
              :style="{ fill: thresholdReached ? '#34d399' : '#67e8f9' }"
            >{{ fr(displayedLoss, 2) }}</text>

            <line x1="82" y1="6" x2="82" y2="30" stroke="rgba(255,255,255,0.12)" />
            <text class="m-lbl" x="92" y="13">Seuil ε</text>
            <text class="m-val" x="92" y="29" fill="#34d399">{{ fr(THRESHOLD, 2) }}</text>

            <line x1="162" y1="6" x2="162" y2="30" stroke="rgba(255,255,255,0.12)" />
            <text class="m-lbl" x="172" y="13">Étape</text>
            <text class="m-val" x="172" y="29" fill="#fff">{{ stepIdx + 1 }}/10</text>
          </g>

          <text
            class="loss-state" x="0" y="99"
            :fill="thresholdReached ? '#34d399' : '#f472b6'"
          >
            {{ thresholdReached ? '● Seuil atteint — réinitialisation du cycle' : '● Descente de gradient : w ← w − η ∇ℒ' }}
          </text>
        </g>

        <!-- Graphique avec courbe lisse à droite -->
        <g class="chart">
          <!-- Repères horizontaux -->
          <g v-for="tick in [0, 1.2, 2.4]" :key="'yt' + tick">
            <line
              :x1="CHART.x" :x2="CHART.x + CHART.w"
              :y1="lossY(tick)" :y2="lossY(tick)"
              stroke="rgba(255,255,255,0.08)" stroke-width="1"
            />
            <text class="ax-lbl" :x="CHART.x - 8" :y="lossY(tick) + 3.5" text-anchor="end">
              {{ fr(tick, 1) }}
            </text>
          </g>

          <!-- Zone & ligne du seuil -->
          <rect
            :x="CHART.x" :y="lossY(THRESHOLD)"
            :width="CHART.w" :height="CHART.y + CHART.h - lossY(THRESHOLD)"
            fill="rgba(52, 211, 153, 0.09)"
          />
          <line
            :x1="CHART.x" :x2="CHART.x + CHART.w"
            :y1="lossY(THRESHOLD)" :y2="lossY(THRESHOLD)"
            stroke="#34d399" stroke-width="1.2" stroke-dasharray="5 4"
          />
          <text class="thresh-txt" :x="CHART.x + CHART.w - 4" :y="lossY(THRESHOLD) - 4" text-anchor="end">
            Seuil de convergence (ε = {{ fr(THRESHOLD, 2) }})
          </text>

          <!-- Axes -->
          <line :x1="CHART.x" :y1="CHART.y" :x2="CHART.x" :y2="CHART.y + CHART.h" stroke="rgba(255,255,255,0.3)" />
          <line :x1="CHART.x" :y1="CHART.y + CHART.h" :x2="CHART.x + CHART.w" :y2="CHART.y + CHART.h" stroke="rgba(255,255,255,0.3)" />

          <!-- Graduations X -->
          <g v-for="k in IDX" :key="'xt' + k">
            <text
              class="ax-lbl" :x="iterX(k)" :y="CHART.y + CHART.h + 14"
              text-anchor="middle"
              :style="{ fill: k === stepIdx ? '#67e8f9' : 'rgba(255,255,255,0.5)', fontWeight: k === stepIdx ? '700' : '400' }"
            >
              t{{ k + 1 }}
            </text>
          </g>

          <!-- Trajectoire complète fantôme (guide visuel de la descente) -->
          <path
            :d="fullSmoothPath"
            fill="none" stroke="rgba(103, 232, 249, 0.16)" stroke-width="1.8" stroke-dasharray="3 3"
          />

          <!-- Aire sous la courbe parcourue -->
          <path v-if="activeAreaPath" :d="activeAreaPath" fill="url(#loss-fill)" />

          <!-- Courbe lisse parcourue -->
          <path
            v-if="activeSmoothPath" :d="activeSmoothPath"
            fill="none" stroke="#67e8f9" stroke-width="2.6"
            stroke-linecap="round"
          />

          <!-- Points validés -->
          <circle
            v-for="pt in pastPoints" :key="'pt' + pt.k"
            :cx="pt.x" :cy="pt.y" r="3.2"
            fill="#050505" stroke="#67e8f9" stroke-width="1.8"
          />

          <!-- Bille active qui descend la courbe -->
          <g v-if="activePoint">
            <circle
              :cx="activePoint.x" :cy="activePoint.y" r="9.5"
              :fill="thresholdReached ? 'rgba(52, 211, 153, 0.25)' : 'rgba(103, 232, 249, 0.25)'"
            />
            <circle
              :cx="activePoint.x" :cy="activePoint.y" r="4.8"
              :fill="thresholdReached ? '#34d399' : '#67e8f9'"
              stroke="#050505" stroke-width="1.4"
              filter="url(#fw-glow)"
            />
            <text
              class="pt-badge"
              :x="activePoint.x"
              :y="Math.max(CHART.y + 11, activePoint.y - 10)"
              text-anchor="middle"
              :fill="thresholdReached ? '#34d399' : '#fff'"
            >
              {{ fr(displayedLoss, 2) }}
            </text>
          </g>
        </g>
      </g>
    </svg>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* =====================================================================
1. Les dix images (28 × 28)
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
2. Simulation d'apprentissage par descente de gradient (10 itérations)
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

const HIDDEN_CACHE = DIGITS.map(hidden)
const HM = HIDDEN_CACHE.map(({ h2 }) => [...h2, 1])

function forwardWithW3(k, w3) {
  const px = DIGITS[k]
  const { h1, h2 } = HIDDEN_CACHE[k]
  const z = IDX.map((j) => h2.reduce((s, h, i) => s + h * w3[i][j], w3[16][j]))
  const m = Math.max(...z)
  const e = z.map((v) => Math.exp(v - m))
  const s = e.reduce((a, v) => a + v, 0)
  const y = e.map((v) => v / s)
  const loss = -Math.log(Math.max(y[k], 1e-6))
  return { px, h1, h2, y, loss, w3: w3.map((r) => [...r]) }
}

let curW3 = Array.from({ length: 17 }, () =>
  Array.from({ length: 10 }, () => (rand() * 2 - 1) * 0.14)
)

const LR = 0.72
const NET = IDX.map((k) => {
  const state = forwardWithW3(k, curW3)
  const probsAll = IDX.map((n) => forwardWithW3(n, curW3).y)
  const grad = Array.from({ length: 17 }, () => new Array(10).fill(0))
  for (let n = 0; n < 10; n++) {
    for (let j = 0; j < 10; j++) {
      const err = probsAll[n][j] - (n === j ? 1 : 0)
      for (let i = 0; i < 17; i++) grad[i][j] += HM[n][i] * err
    }
  }
  for (let i = 0; i < 17; i++) {
    for (let j = 0; j < 10; j++) curW3[i][j] -= LR * grad[i][j]
  }
  return state
})

const FINAL_LOSS = forwardWithW3(9, curW3).loss
const THRESHOLD = 0.08

/* =====================================================================
3. Outils mathématiques et courbes lisses
   ===================================================================== */
const POS = '#67e8f9'
const NEG = '#fb923c'
const BP_POS = '#f472b6'
const BP_NEG = '#c084fc'
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

function bezLen(pts, steps = 16) {
  let len = 0
  let prev = pts[0]
  for (let i = 1; i <= steps; i++) {
    const cur = bez(pts, i / steps)
    len += Math.hypot(cur[0] - prev[0], cur[1] - prev[1])
    prev = cur
  }
  return Number(len.toFixed(1))
}

// Génère un chemin SVG lisse (Catmull-Rom → Bézier cubique) passant par tous les points
function smoothSvgPath(pts) {
  if (pts.length === 0) return ''
  if (pts.length === 1) return `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i === 0 ? i : i - 1]
    const p1 = pts[i]
    const p2 = pts[i + 1]
    const p3 = pts[i + 2 < pts.length ? i + 2 : i + 1]
    const cp1x = p1.x + (p2.x - p0.x) / 6
    const cp1y = p1.y + (p2.y - p0.y) / 6
    const cp2x = p2.x - (p3.x - p1.x) / 6
    const cp2y = p2.y - (p3.y - p1.y) / 6
    d += ` C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`
  }
  return d
}

const fr = (n, d) => {
  const v = Math.abs(n) < 0.5 * Math.pow(10, -d) ? 0 : n
  const s = Math.abs(v).toFixed(d).replace('.', ',')
  return v < 0 ? '\u2212' + s : s
}

/* =====================================================================
4. Géométrie compacte 16:9 (réseau en haut, courbe en bas)
   ===================================================================== */
const GAL = { x: 22, s: 28 }
const galY = (k) => 56 + k * 34
const BIG = { x: 84, y: 173, s: 104 }
const STRIP = { x: 220, y: 58, w: 22, h: 334 }
const XS = [null, 445, 625]
const OUT = { x: 785, thumbX: 812, barX: 848, barW: 92 }
const CY = 225
const yHid = (k) => CY + (k - 7.5) * 21
const outY = (k) => CY + (k - 4.5) * 34
const yRow = (r) => STRIP.y + ((r + 0.5) / 28) * STRIP.h

const CHART = { x: 308, y: 444, w: 662, h: 88, maxLoss: 2.5 }
const iterX = (k) => CHART.x + (k / 9) * CHART.w
const lossY = (val) => CHART.y + CHART.h - clamp(val / CHART.maxLoss) * CHART.h

const NODES = [
  ...Array.from({ length: 16 }, (_, k) => ({ l: 1, k, x: XS[1], y: yHid(k), r: 8.5 })),
  ...Array.from({ length: 16 }, (_, k) => ({ l: 2, k, x: XS[2], y: yHid(k), r: 8.5 })),
  ...IDX.map((k) => ({ l: 3, k, x: OUT.x, y: outY(k), r: 12 })),
]

const HEADERS = [
  { x: 36, name: 'Images', sub: '0 à 9' },
  { x: 136, name: 'Image', sub: '28 × 28' },
  { x: 231, name: 'Entrée', sub: 'x ∈ ℝ⁷⁸⁴' },
  { x: XS[1], name: 'Cachée 1', sub: 'h¹ ∈ ℝ¹⁶' },
  { x: XS[2], name: 'Cachée 2', sub: 'h² ∈ ℝ¹⁶' },
  { x: OUT.x, name: 'Sortie', sub: 'ŷ ∈ ℝ¹⁰' },
  { x: OUT.barX + OUT.barW / 2, name: 'Probabilité', sub: 'softmax' },
]

const SRC_N = [28, 16, 16]
const DST_N = [16, 16, 10]
const EDGES = [0, 1, 2].map((l) => {
  const list = []
  for (let j = 0; j < DST_N[l]; j++) {
    for (let s = 0; s < SRC_N[l]; s++) {
      const x1 = l === 0 ? STRIP.x + STRIP.w : XS[l] + 10
      const y1 = l === 0 ? yRow(s) : yHid(s)
      const x2 = (l === 2 ? OUT.x - 12 : XS[l + 1] - 10) - 2
      const y2 = l === 2 ? outY(j) : yHid(j)
      const xm = (x1 + x2) / 2
      const pts = [[x1, y1], [xm, y1], [xm, y2], [x2, y2]]
      list.push({
        l, s, j,
        pts,
        len: bezLen(pts),
        d: `M ${x1} ${y1} C ${xm} ${y1}, ${xm} ${y2}, ${x2} ${y2}`,
        dr: `M ${x2} ${y2} C ${xm} ${y2}, ${xm} ${y1}, ${x1} ${y1}`,
        rpts: [[x2, y2], [xm, y2], [xm, y1], [x1, y1]],
      })
    }
  }
  return list
})

EDGES.forEach((E, l) => {
  const raw = E.map((e) => {
    if (l === 0) return Math.hypot(...W1[e.j].slice(e.s * 28, e.s * 28 + 28))
    if (l === 1) return Math.abs(W2[e.j][e.s])
    return 0.45
  })
  const m = Math.max(...raw) || 1
  E.forEach((e, n) => { e.o = Number((0.05 + 0.18 * (raw[n] / m)).toFixed(3)) })
})
const WIRES = EDGES.flat()

const CONTR = NET.map(({ px, h1, h2, w3 }) => {
  const raw = [new Array(28 * 16), new Array(16 * 16), new Array(16 * 10)]
  for (let j = 0; j < 16; j++) {
    for (let r = 0; r < 28; r++) {
      let s = 0
      for (let c = 0; c < 28; c++) s += px[r * 28 + c] * W1[j][r * 28 + c]
      raw[0][j * 28 + r] = s
    }
    for (let i = 0; i < 16; i++) raw[1][j * 16 + i] = h1[i] * W2[j][i]
  }
  for (let j = 0; j < 10; j++) for (let i = 0; i < 16; i++) raw[2][j * 16 + i] = h2[i] * w3[i][j]
  return raw.map((a) => {
    const m = Math.max(...a.map(Math.abs)) || 1
    return a.map((v) => v / m)
  })
})

function backprop(px, h1, h2, y, w3, target) {
  const deltaOut = y.map((v, k) => v - (k === target ? 1 : 0))
  const delta2 = h2.map((v, i) =>
    w3[i].reduce((sum, w, j) => sum + w * deltaOut[j], 0) * (1 - v * v)
  )
  const delta1 = h1.map((v, i) =>
    W2.reduce((sum, row, j) => sum + row[i] * delta2[j], 0) * (1 - v * v)
  )
  const raw = [new Array(28 * 16), new Array(16 * 16), new Array(16 * 10)]
  for (let j = 0; j < 16; j++) {
    for (let r = 0; r < 28; r++) {
      let contribution = 0
      for (let c = 0; c < 28; c++) contribution += px[r * 28 + c] * W1[j][r * 28 + c]
      raw[0][j * 28 + r] = delta1[j] * contribution
    }
    for (let i = 0; i < 16; i++) raw[1][j * 16 + i] = delta2[j] * h1[i]
  }
  for (let j = 0; j < 10; j++) {
    for (let i = 0; i < 16; i++) raw[2][j * 16 + i] = deltaOut[j] * h2[i]
  }
  return raw.map((a) => {
    const m = Math.max(...a.map(Math.abs)) || 1
    return a.map((v) => v / m)
  })
}
const BACK_CONTR = NET.map(({ px, h1, h2, y, w3 }, k) => backprop(px, h1, h2, y, w3, k))

/* =====================================================================
5. Images canvas
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
6. Horloge d'animation
   ===================================================================== */
const DUR = 8800
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
    stepIdx.value = 9
    t.value = 8400
  } else {
    raf = requestAnimationFrame(frame)
  }
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* =====================================================================
7. Chronologie & Courbe de coût
   ===================================================================== */
const S = [1500, 2800, 3950]
const STAG = [19, 22, 22]
const DRAW = 580
const BACK_START = [5750, 6400, 7050]
const BACK_STAG = [20, 19, 19]
const BACK_DRAW = 540
const BACK_PULSE = [7050, 6400, 5650]
const REV = [2650, 3820, 4950]
const WIN = [[0, 1e9], [0, 1600], [420, 1700], [1500, 2950], [2800, 4050], [3950, 5400], [3950, 5400]]

const step = computed(() => NET[stepIdx.value])
const endFade = computed(() => 1 - ease(clamp((t.value - (DUR - 450)) / 450)))
const rev = computed(() => REV.map((r) => ease(clamp((t.value - r) / 260))))
const scan = computed(() => clamp((t.value - 420) / 1050))

const bigPos = computed(() => {
  const e = ease(clamp(t.value / 420))
  const k = stepIdx.value
  return { x: lerp(GAL.x, BIG.x, e), y: lerp(galY(k), BIG.y, e), s: lerp(GAL.s, BIG.s, e) }
})

const hdrOp = computed(() =>
  WIN.map(([a, b]) => 0.45 + 0.55 * clamp((t.value - a) / 240) * (1 - clamp((t.value - b) / 280)))
)

const actsShown = computed(() =>
  [step.value.h1, step.value.h2, step.value.y].map((a, l) => a.map((v) => v * rev.value[l] * endFade.value))
)
const outShown = computed(() => actsShown.value[2])
const val = (n) => actsShown.value[n.l - 1][n.k]

const flash = computed(() =>
  REV.map((r) => clamp((t.value - r) / 190) * (1 - clamp((t.value - r - 190) / 450)))
)
const backFlash = computed(() =>
  BACK_PULSE.map((r) => clamp((t.value - r) / 170) * (1 - ease(clamp((t.value - r - 170) / 460))))
)

const active = computed(() => {
  const T = t.value
  const d = stepIdx.value
  const res = { ov: [], pu: [], bov: [], bpu: [] }

  for (let l = 0; l < 3; l++) {
    const start = S[l]
    const maxEnd = start + (SRC_N[l] - 1) * STAG[l] + DRAW * 1.75
    if (T < start || T > maxEnd) continue
    const E = EDGES[l]
    const C = CONTR[d][l]
    for (let n = 0; n < E.length; n++) {
      const rel = C[n]
      const a = Math.abs(rel)
      if (a < 0.12) continue
      const e = E[n]
      const u = (T - start - e.s * STAG[l]) / DRAW
      if (u <= 0 || u >= 1.75) continue
      const prog = ease(clamp(u))
      const edgeFade = u <= 0.85 ? 1 : 1 - ease(clamp((u - 0.85) / 0.9))
      const c = rel > 0 ? POS : NEG
      res.ov.push({ d: e.d, len: e.len, prog, w: 0.8 + 2.1 * a, op: edgeFade * (0.3 + 0.7 * a), c })
      if (u < 1) {
        const [x, y] = bez(e.pts, prog)
        res.pu.push({ x, y, r: 1.5 + 2.1 * a, c })
      }
    }
  }

  for (let stage = 0; stage < 3; stage++) {
    const l = 2 - stage
    const start = BACK_START[stage]
    const maxEnd = start + (DST_N[l] - 1) * BACK_STAG[stage] + BACK_DRAW * 1.75
    if (T < start || T > maxEnd) continue
    const E = EDGES[l]
    const C = BACK_CONTR[d][l]
    for (let n = 0; n < E.length; n++) {
      const rel = C[n]
      const a = Math.abs(rel)
      if (a < 0.11) continue
      const e = E[n]
      const u = (T - start - e.j * BACK_STAG[stage]) / BACK_DRAW
      if (u <= 0 || u >= 1.75) continue
      const prog = ease(clamp(u))
      const edgeFade = u <= 0.85 ? 1 : 1 - ease(clamp((u - 0.85) / 0.9))
      const c = rel >= 0 ? BP_POS : BP_NEG
      res.bov.push({ d: e.dr, len: e.len, prog, w: 1.0 + 2.2 * a, op: edgeFade * (0.35 + 0.65 * a), c })
      if (u < 1) {
        const [x, y] = bez(e.rpts, prog)
        res.bpu.push({ x, y, r: 1.7 + 2.1 * a, c })
      }
    }
  }
  return res
})

const win = computed(() => {
  const y = step.value.y
  return y.indexOf(Math.max(...y))
})
const winOp = computed(() => clamp((t.value - 5050) / 280) * endFade.value)

/* Courbe lisse de descente du coût */
const ALL_POINTS = IDX.map((k) => ({ k, x: iterX(k), y: lossY(NET[k].loss), loss: NET[k].loss }))
const fullSmoothPath = smoothSvgPath(ALL_POINTS)

const updateEase = computed(() => ease(clamp((t.value - 7750) / 650)))

const displayedLoss = computed(() => {
  const k = stepIdx.value
  const cur = NET[k].loss
  const next = k < 9 ? NET[k + 1].loss : FINAL_LOSS
  return lerp(cur, next, updateEase.value)
})

const thresholdReached = computed(() => displayedLoss.value <= THRESHOLD)

const pastPoints = computed(() => ALL_POINTS.slice(0, stepIdx.value))

const activePoint = computed(() => ({
  x: iterX(stepIdx.value),
  y: lossY(displayedLoss.value),
}))

const activeSmoothPath = computed(() =>
  smoothSvgPath([...pastPoints.value, activePoint.value])
)

const activeAreaPath = computed(() => {
  const pts = [...pastPoints.value, activePoint.value]
  if (pts.length < 2) return ''
  const base = CHART.y + CHART.h
  return `${activeSmoothPath.value} L ${pts[pts.length - 1].x.toFixed(1)} ${base} L ${pts[0].x.toFixed(1)} ${base} Z`
})

const caption = computed(() => {
  const T = t.value
  if (T < 420) return `Itération ${stepIdx.value + 1}/10 · Image du chiffre ${stepIdx.value} (28 × 28)`
  if (T < 1500) return 'Aplatissement : lecture ligne par ligne → vecteur x ∈ ℝ⁷⁸⁴'
  if (T < 2800) return 'Couche cachée 1 :  h¹ = tanh(W¹ x)'
  if (T < 3950) return 'Couche cachée 2 :  h² = tanh(W² h¹)'
  if (T < 5050) return 'Sortie :  ŷ = softmax(W³ h²)'
  if (T < 5750) {
    const p = step.value.y[stepIdx.value]
    return `Évaluation : probabilité cible ${fr(p * 100, 0)} %   ·   Coût ℒ = ${fr(step.value.loss, 2)}`
  }
  if (T < 7750) return 'Rétropropagation du gradient ∂ℒ/∂W de la sortie vers l’entrée'
  if (thresholdReached.value && stepIdx.value === 9) {
    return 'Seuil de convergence atteint (ℒ ≤ 0,08) · Réinitialisation des poids'
  }
  return `Mise à jour des poids : W ← W − η ∇ℒ  ·  Coût minimisé à ${fr(displayedLoss.value, 2)}`
})
</script>

<style scoped>
.mlp-forward {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: #050505;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  overflow: hidden;
}

.diagram {
  display: block;
  width: 100%;
  height: 100%;
  max-height: 100%;
}
.diagram text {
  text-anchor: middle;
}

.hd {
  fill: #fff;
  font-size: 13px;
}
.hd-sub {
  fill: rgba(255, 255, 255, 0.58);
  font: italic 11.5px Georgia, 'Times New Roman', serif;
}
.cap {
  fill: rgba(255, 255, 255, 0.85);
  font: italic 14.5px Georgia, 'Times New Roman', serif;
}

.px {
  image-rendering: pixelated;
  color: #fff;
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
  stroke-width: 1.5;
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
  stroke-width: 1.4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.wires path {
  fill: none;
  stroke: #fff;
  stroke-width: 0.55;
}
.overlays path,
.back-overlays path {
  fill: none;
  stroke-linecap: round;
}

.ring {
  fill: none;
  stroke-width: 1.1;
}
.core {
  fill: #050505;
  stroke: #fff;
  stroke-width: 1.3;
}
.node-text {
  font: italic 8px Georgia, serif;
}
.flash {
  fill: none;
  stroke: #fff;
  stroke-width: 1.1;
}
.back-flash {
  fill: none;
  stroke: #f472b6;
  stroke-width: 1.3;
}

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
  font: 10px ui-monospace, monospace;
}
.winner {
  fill: none;
  stroke-width: 1.6;
}
.winner-box {
  fill: none;
  stroke-width: 1.6;
}

/* Panneau de la courbe de coût */
.loss-section text {
  text-anchor: start;
}
.loss-hd {
  fill: #fff;
  font-size: 13px;
  font-weight: 600;
}
.loss-eq {
  fill: rgba(255, 255, 255, 0.75);
  font: italic 13px Georgia, 'Times New Roman', serif;
}
.m-lbl {
  fill: rgba(255, 255, 255, 0.55);
  font-size: 9.5px;
}
.m-val {
  font-family: ui-monospace, monospace;
  font-size: 13px;
  font-weight: 700;
}
.loss-state {
  font-size: 10.5px;
  font-weight: 500;
}
.chart text {
  text-anchor: unset;
}
.ax-lbl {
  fill: rgba(255, 255, 255, 0.55);
  font: 10px ui-monospace, monospace;
}
.thresh-txt {
  fill: #34d399;
  font: 600 10px ui-monospace, monospace;
}
.pt-badge {
  font: 700 10.5px ui-monospace, monospace;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; }
}
</style>