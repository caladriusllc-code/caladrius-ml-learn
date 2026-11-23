
<template>
  <section class="mlp-params" aria-label="Vecteur des paramètres optimaux du réseau">
    <svg
      class="diagram"
      viewBox="0 0 880 560"
      role="img"
      aria-label="Vecteur colonne des paramètres optimisés du réseau de neurones."
    >
      <defs>
        <filter id="op-glow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <!-- Titre -->
      <text class="title" x="440" y="40">Les paramètres optimaux</text>
      <text class="sub" x="440" y="62">θ* = argmin L(θ)</text>

      <!-- Crochets du vecteur -->
      <g :opacity="0.5 + 0.5 * done" :filter="done > 0.3 ? 'url(#op-glow)' : null">
        <path
          class="bracket"
          :d="`M ${BX.l + 12} ${TOP} H ${BX.l} V ${BOT} H ${BX.l + 12}`"
        />
        <path
          class="bracket"
          :d="`M ${BX.r - 12} ${TOP} H ${BX.r} V ${BOT} H ${BX.r - 12}`"
        />
      </g>

      <text class="theta" :x="BX.l - 22" :y="(TOP + BOT) / 2 + 12">θ* =</text>

      <!-- Axe zéro -->
      <line class="axis" :x1="AX" :x2="AX" :y1="TOP + 6" :y2="BOT - 6" />

      <!-- Lignes du vecteur -->
      <g v-for="(r, n) in ROWS" :key="'r' + n">
        <template v-if="r.dots">
          <text class="dots" :x="AX" :y="rowY(n) + 6">⋮</text>
        </template>

        <template v-else>
          <circle
            v-if="flash(n) > 0.02"
            class="flash"
            :cx="AX + shown(n) * HW"
            :cy="rowY(n)"
            :r="4 + flash(n) * 10"
            :opacity="flash(n) * 0.9"
            filter="url(#op-glow)"
          />

          <text class="idx" :x="BX.l + 22" :y="rowY(n) + 6">
            θ{{ sub(r.i) }}
          </text>

          <text
            class="val"
            :x="BX.l + 152"
            :y="rowY(n) + 7"
            :opacity="settled(n) ? 1 : 0.45"
          >
            {{ fr(shown(n), 2) }}
          </text>

          <rect
            class="bar-bg"
            :x="AX - HW"
            :y="rowY(n) - 4"
            :width="2 * HW"
            height="8"
            rx="4"
          />

          <rect
            :x="shown(n) >= 0 ? AX : AX + shown(n) * HW"
            :y="rowY(n) - 4"
            :width="Math.abs(shown(n)) * HW"
            height="8"
            rx="4"
            :fill="shown(n) >= 0 ? POS : NEG"
            :opacity="settled(n) ? 1 : 0.4"
          />
        </template>
      </g>

      <!-- Nombre total de paramètres -->
      <g :opacity="clamp(t / 400) * endFade">
        <text class="big" x="772" y="190">{{ NTXT }}</text>
        <text class="big-sub" x="772" y="216">paramètres</text>
      </g>

      <!-- Légende -->
      <g :opacity="0.85">
        <circle :cx="690" :cy="270" r="5" :fill="POS" />
        <text class="leg" x="704" y="274">valeur positive</text>

        <circle :cx="690" :cy="294" r="5" :fill="NEG" />
        <text class="leg" x="704" y="298">valeur négative</text>
      </g>

      <!-- Légende de l'étape -->
      <text class="cap" x="440" y="540">{{ caption }}</text>
    </svg>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* =====================================================================
   1. Architecture du réseau : 784 → 16 → 16 → 10

      784 × 16 + 16 × 16 + 16 × 10 + 10 = 12 970 paramètres

   Les valeurs sont fictives, fixes et illustrent un réseau entraîné.
   Elles ne représentent pas les poids d'un entraînement réel.
   ===================================================================== */

const N = 784 * 16 + 16 * 16 + 16 * 10 + 10
const NTXT = N.toLocaleString('fr-FR')

// Valeurs optimales fictives
const OPTIMAL_VALUES = [
  0.82, -0.47, 0.31, -0.96, 0.64,
  0.18, -0.73, 0.55, -0.24, 0.91,
  -0.38, 0.76, -0.12
]

const IDS = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
  N - 2, N - 1, N
]

const ROWS = IDS.map((i, index) => ({
  i,
  v: OPTIMAL_VALUES[index]
}))

/* =====================================================================
   2. Géométrie
   ===================================================================== */

const TOP = 88
const BOT = 506
const BX = { l: 240, r: 640 }
const AX = 520
const HW = 100

const rowY = (n) =>
  TOP + 18 + n * ((BOT - TOP - 36) / (ROWS.length - 1))

/* =====================================================================
   3. Outils
   ===================================================================== */

const POS = '#67e8f9'
const NEG = '#fb923c'

const clamp = (v) => Math.min(1, Math.max(0, v))

const ease = (u) =>
  u < 0.5
    ? 4 * u * u * u
    : 1 - Math.pow(-2 * u + 2, 3) / 2

const fr = (n, d) => {
  const v = Math.abs(n) < 0.5 * Math.pow(10, -d) ? 0 : n
  const s = Math.abs(v).toFixed(d).replace('.', ',')
  return v < 0 ? '\u2212' + s : s
}

const SUB = '₀₁₂₃₄₅₆₇₈₉'

const sub = (n) =>
  String(n).split('').map((c) => SUB[+c]).join('')

// Bruit pseudo-aléatoire déterministe
const noise = (n, tick) => {
  const x = Math.sin((n + 1) * 12.9898 + tick * 78.233) * 43758.5453
  return (x - Math.floor(x)) * 2 - 1
}

/* =====================================================================
   4. Horloge : boucle d'animation
   ===================================================================== */

const DUR = 7600
const t = ref(0)

let raf = 0
let t0 = 0

function frame(ts) {
  if (!t0) t0 = ts

  t.value = (ts - t0) % DUR

  raf = requestAnimationFrame(frame)
}

onMounted(() => {
  const reduce = window.matchMedia?.(
    '(prefers-reduced-motion: reduce)'
  ).matches

  if (reduce) {
    t.value = 6000
  } else {
    raf = requestAnimationFrame(frame)
  }
})

onBeforeUnmount(() => cancelAnimationFrame(raf))

/* =====================================================================
   5. Chronologie : recherche puis fixation de haut en bas
   ===================================================================== */

const SETTLE0 = 1500
const SETTLE_GAP = 210
const END = 7000

const tSettle = (n) => SETTLE0 + n * SETTLE_GAP

const endFade = computed(() =>
  1 - clamp((t.value - END) / 600)
)

const settled = (n) =>
  t.value >= tSettle(n)

// Valeur affichée pendant l'apprentissage
const shown = (n) => {
  const r = ROWS[n]
  const T = t.value
  const tick = Math.floor(T / 90)

  // Les valeurs fluctuent avant de converger
  const search = noise(n, tick) * 1.2

  // Progression vers la valeur optimale
  const p = ease(clamp((T - tSettle(n)) / 260))

  const v = search + (r.v - search) * p

  return v * clamp(T / 300) * endFade.value
}

// Flash lumineux à la fixation de chaque paramètre
const flash = (n) => {
  const d = t.value - tSettle(n)

  return (
    clamp(d / 150) *
    (1 - clamp((d - 150) / 500)) *
    endFade.value
  )
}

const lastSettle = tSettle(ROWS.length - 1)

const done = computed(() =>
  ease(clamp((t.value - lastSettle) / 500)) *
  endFade.value
)

// Texte explicatif
const caption = computed(() => {
  const T = t.value

  if (T < SETTLE0) {
    return 'Apprentissage : les paramètres θ sont ajustés pour réduire L(θ)'
  }

  if (T < lastSettle) {
    return 'Chaque paramètre converge vers sa valeur optimale'
  }

  return `θ* : ${NTXT} paramètres optimisés après apprentissage`
})
</script>

<style scoped>
.mlp-params {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  color: #fff;
  background: #050505;
  display: flex;
  justify-content: center;
  align-items: center;
}

.diagram {
  display: block;
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
}

.diagram text {
  text-anchor: middle;
}

/* Textes */
.title {
  fill: #fff;
  font: 600 20px Inter, ui-sans-serif, system-ui, sans-serif;
}

.sub {
  fill: rgba(255, 255, 255, 0.65);
  font: italic 15px Georgia, 'Times New Roman', serif;
}

.theta {
  text-anchor: end;
  fill: #fff;
  font: italic 26px Georgia, 'Times New Roman', serif;
}

.idx {
  text-anchor: start;
  fill: rgba(255, 255, 255, 0.75);
  font: italic 18px Georgia, 'Times New Roman', serif;
}

.val {
  text-anchor: end;
  fill: #fff;
  font: italic 22px Georgia, 'Times New Roman', serif;
}

.big {
  fill: #fff;
  font: italic 40px Georgia, 'Times New Roman', serif;
}

.big-sub {
  fill: rgba(255, 255, 255, 0.65);
  font: italic 16px Georgia, 'Times New Roman', serif;
}

.dots {
  fill: rgba(255, 255, 255, 0.6);
  font: 20px Georgia, serif;
}

.leg {
  text-anchor: start;
  fill: rgba(255, 255, 255, 0.75);
  font: italic 15px Georgia, 'Times New Roman', serif;
}

.cap {
  fill: rgba(255, 255, 255, 0.85);
  font: italic 17px Georgia, 'Times New Roman', serif;
}

/* Vecteur */
.bracket {
  fill: none;
  stroke: #fff;
  stroke-width: 1.8;
  stroke-linejoin: round;
}

.axis {
  stroke: rgba(255, 255, 255, 0.35);
  stroke-width: 1;
  stroke-dasharray: 2 4;
}

.bar-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.25);
  stroke-width: 1;
}

.flash {
  fill: none;
  stroke: #fff;
  stroke-width: 1.2;
}
</style>
