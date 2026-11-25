<template>
  <section
    class="param-vector"
    aria-label="Vecteur des paramètres du modèle convergeant vers ses valeurs optimales"
    @click="replay"
  >
    <svg
      class="diagram"
      viewBox="0 0 1000 540"
      role="img"
      aria-label="Un vecteur colonne représentant les 13 002 paramètres du réseau de neurones. Les nombres varient aléatoirement puis se figent progressivement sur les meilleures valeurs numériques."
    >
      <defs>
        <filter id="pv-glow" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation="3.5" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <!-- En-tête minimal -->
      <text class="title" x="500" y="38">
        {{ converged ? 'Paramètres optimaux du modèle' : 'Recherche des meilleurs paramètres' }}
      </text>
      <text class="subtitle" x="500" y="60">
        Réseau 784 → 16 → 16 → 10 · 13 002 paramètres ajustables
      </text>

      <!-- Symbole du vecteur à gauche : θ  =  (ou θ* = une fois stabilisé) -->
      <g class="lhs" :transform="`translate(335, ${VEC_CY})`">
        <text class="sym" x="0" y="6" :class="{ optimal: converged }">
          {{ converged ? 'θ*' : 'θ' }}
        </text>
        <text class="dim" x="0" y="28">∈ ℝ¹³ ⁰⁰²</text>
        <text class="eq" x="54" y="6">=</text>
      </g>

      <!-- Parenthèses / Crochets du vecteur colonne -->
      <g class="brackets" :class="{ optimal: converged }">
        <!-- Crochet gauche -->
        <path
          :d="`M ${BOX.x0 + 16} ${BOX.y0} L ${BOX.x0} ${BOX.y0} L ${BOX.x0} ${BOX.y1} L ${BOX.x0 + 16} ${BOX.y1}`"
        />
        <!-- Crochet droit -->
        <path
          :d="`M ${BOX.x1 - 16} ${BOX.y0} L ${BOX.x1} ${BOX.y0} L ${BOX.x1} ${BOX.y1} L ${BOX.x1 - 16} ${BOX.y1}`"
        />
      </g>

      <!-- Composantes du vecteur -->
      <g class="entries">
        <g
          v-for="(row, idx) in displayRows"
          :key="row.id"
          :transform="`translate(500, ${rowY(idx)})`"
        >
          <!-- Ellipse verticale pour représenter les 13 002 composantes -->
          <template v-if="row.ellipsis">
            <circle cx="0" cy="-9" r="1.8" class="dot" />
            <circle cx="0" cy="0" r="1.8" class="dot" />
            <circle cx="0" cy="9" r="1.8" class="dot" />
          </template>

          <!-- Valeur numérique animée puis figée -->
          <template v-else>
            <!-- Halo subtil au moment où le paramètre se fige -->
            <rect
              v-if="row.flash > 0.02"
              x="-86"
              y="-15"
              width="172"
              height="26"
              rx="6"
              class="lock-pill"
              :opacity="row.flash * 0.45"
              filter="url(#pv-glow)"
            />

            <!-- Valeur numérique formatée (ex. +0,42 / −1,38) -->
            <text
              class="num"
              x="-14"
              y="4"
              :class="{
                locked: row.locked,
                neg: row.val < 0,
              }"
            >
              {{ frSigned(row.val) }}
            </text>

            <!-- Indice discret du paramètre à droite -->
            <text class="idx-lbl" x="148" y="3">
              {{ row.label }}
            </text>
          </template>
        </g>
      </g>

      <!-- Indication d'état à droite du vecteur -->
      <g class="status" :transform="`translate(665, ${VEC_CY})`">
        <line
          class="status-line"
          x1="-32"
          y1="0"
          x2="-6"
          y2="0"
          :class="{ optimal: converged }"
        />
        <text class="status-main" x="4" y="-4" :class="{ optimal: converged }">
          {{ converged ? 'Convergence atteinte' : 'Exploration aléatoire…' }}
        </text>
        <text class="status-sub" x="4" y="16">
          {{ converged ? 'Erreur minimale sur les 10 chiffres' : `${lockedCount} / ${ACTIVE_COUNT} composantes figées` }}
        </text>
      </g>

      <!-- Légende pédagogique en bas -->
      <text class="cap" x="500" y="516">{{ caption }}</text>
    </svg>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* =====================================================================
   1. Définition des composantes affichées du vecteur θ ∈ ℝ¹³ ⁰⁰²
      (6 premières composantes, ellipse ⋮, 5 dernières composantes)
   ===================================================================== */
const ROWS = [
  { id: 'w0', label: 'w₁', target: 0.42 },
  { id: 'w1', label: 'w₂', target: -1.38 },
  { id: 'w2', label: 'w₃', target: 0.87 },
  { id: 'w3', label: 'w₄', target: -0.19 },
  { id: 'w4', label: 'w₅', target: 1.64 },
  { id: 'w5', label: 'w₆', target: -0.73 },
  { id: 'dots', ellipsis: true },
  { id: 'wN4', label: 'w₁₂ ₉₉₈', target: -1.12 },
  { id: 'wN3', label: 'w₁₂ ₉₉₉', target: 0.56 },
  { id: 'wN2', label: 'w₁₃ ₀₀₀', target: 1.91 },
  { id: 'wN1', label: 'w₁₃ ₀₀₁', target: -0.64 },
  { id: 'bN', label: 'b₁₃ ₀₀₂', target: 0.31 },
]

const ACTIVE_ROWS = ROWS.filter((r) => !r.ellipsis)
const ACTIVE_COUNT = ACTIVE_ROWS.length

// Instants (en ms) où chaque composante se fige progressivement
const LOCK_TIMES = [
  1500, 1780, 2040, 2290, 2530, 2760,
  null,
  3020, 3260, 3490, 3710, 3920,
]

/* =====================================================================
   2. Géométrie du vecteur colonne
   ===================================================================== */
const VEC_CY = 276
const ROW_H = 31
const TOTAL_H = (ROWS.length - 1) * ROW_H
const BOX = {
  x0: 416,
  x1: 584,
  y0: VEC_CY - TOTAL_H / 2 - 24,
  y1: VEC_CY + TOTAL_H / 2 + 24,
}
const rowY = (idx) => VEC_CY - TOTAL_H / 2 + idx * ROW_H

/* =====================================================================
   3. Générateur pseudo-aléatoire déterministe & formatage français
   ===================================================================== */
function hashNoise(seed) {
  let x = Math.imul(seed ^ 0x9e3779b9, 0x85ebca6b)
  x ^= x >>> 13
  x = Math.imul(x, 0xc2b2ae35)
  x ^= x >>> 16
  return ((x >>> 0) / 4294967296) * 2 - 1 // dans [-1, 1]
}

const clamp = (v) => Math.min(1, Math.max(0, v))
const easeOut = (u) => 1 - Math.pow(1 - u, 3)

function frSigned(v) {
  const clean = Math.abs(v) < 0.005 ? 0 : v
  const absStr = Math.abs(clean).toFixed(2).replace('.', ',')
  if (clean > 0) return '+' + absStr
  if (clean < 0) return '\u2212' + absStr
  return ' 0,00'
}

/* =====================================================================
   4. Boucle d'animation (60 ips)
   ===================================================================== */
const CYCLE_DUR = 8400 // 4,0 s de recherche/convergence + 4,4 s d'affichage stable
const t = ref(0)
let raf = 0
let t0 = 0

function frame(ts) {
  if (!t0) t0 = ts
  t.value = (ts - t0) % CYCLE_DUR
  raf = requestAnimationFrame(frame)
}

function replay() {
  t0 = performance.now()
  t.value = 0
}

onMounted(() => {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    t.value = 4500
  } else {
    raf = requestAnimationFrame(frame)
  }
})

onBeforeUnmount(() => cancelAnimationFrame(raf))

/* =====================================================================
   5. Calcul des valeurs affichées à chaque frame
   ===================================================================== */
const displayRows = computed(() => {
  const T = t.value
  return ROWS.map((row, idx) => {
    if (row.ellipsis) return row

    const lockAt = LOCK_TIMES[idx]
    const locked = T >= lockAt

    if (locked) {
      const sinceLock = T - lockAt
      const flash = sinceLock < 550 ? 1 - easeOut(clamp(sinceLock / 550)) : 0
      return {
        ...row,
        val: row.target,
        locked: true,
        flash,
      }
    }

    // Ralentissement progressif du tirage aléatoire dans les 650 ms avant verrouillage
    const remaining = lockAt - T
    const slowdown = remaining < 650 ? 1 - remaining / 650 : 0
    const stepMs = 45 + Math.round(slowdown * slowdown * 130)
    const tick = Math.floor(T / stepMs)

    // Amplitude du bruit qui diminue légèrement juste avant de converger
    const amp = 2.4 * (1 - 0.55 * slowdown)
    const jitter = hashNoise(tick * 31 + idx * 997) * amp
    const val = row.target * slowdown + jitter

    return {
      ...row,
      val,
      locked: false,
      flash: 0,
    }
  })
})

const lockedCount = computed(() =>
  displayRows.value.filter((r) => !r.ellipsis && r.locked).length
)

const converged = computed(() => lockedCount.value === ACTIVE_COUNT)

const caption = computed(() => {
  if (!converged.value) {
    return 'Sans entraînement, les 13 002 paramètres sont aléatoires : le modèle répond au hasard'
  }
  return 'Entraîner un modèle consiste à trouver ces valeurs exactes θ* qui minimisent l’erreur'
})
</script>

<style scoped>
.param-vector {
  box-sizing: border-box;
  width: 100%;
  color: #fff;
  background: #050505;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  cursor: pointer;
  user-select: none;
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
.title {
  fill: #fff;
  font-size: 19px;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.subtitle {
  fill: rgba(255, 255, 255, 0.56);
  font: italic 13.5px Georgia, 'Times New Roman', serif;
}

/* Membre de gauche : θ = */
.lhs .sym {
  fill: rgba(255, 255, 255, 0.85);
  font: italic 30px Georgia, 'Times New Roman', serif;
  transition: fill 0.35s ease;
}
.lhs .sym.optimal {
  fill: #67e8f9;
}
.lhs .dim {
  fill: rgba(255, 255, 255, 0.5);
  font: italic 12.5px Georgia, 'Times New Roman', serif;
}
.lhs .eq {
  fill: rgba(255, 255, 255, 0.72);
  font: 24px Georgia, 'Times New Roman', serif;
}

/* Crochets du vecteur */
.brackets path {
  fill: none;
  stroke: rgba(255, 255, 255, 0.65);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: stroke 0.35s ease;
}
.brackets.optimal path {
  stroke: #67e8f9;
}

/* Valeurs à l'intérieur du vecteur */
.num {
  font: 500 17px ui-monospace, SFMono-Regular, Menlo, monospace;
  fill: rgba(255, 255, 255, 0.68);
}
.num.neg {
  fill: rgba(251, 146, 60, 0.78);
}
.num.locked {
  fill: #67e8f9;
  font-weight: 700;
}

.lock-pill {
  fill: #67e8f9;
}

.dot {
  fill: rgba(255, 255, 255, 0.55);
}

.diagram .idx-lbl {
  text-anchor: start;
  fill: rgba(255, 255, 255, 0.38);
  font: italic 12px Georgia, 'Times New Roman', serif;
}

/* État à droite */
.status-line {
  stroke: rgba(255, 255, 255, 0.3);
  stroke-width: 1.2;
  stroke-dasharray: 3 3;
}
.status-line.optimal {
  stroke: #67e8f9;
  stroke-dasharray: none;
}
.diagram .status-main {
  text-anchor: start;
  fill: rgba(255, 255, 255, 0.85);
  font-size: 13.5px;
  font-weight: 600;
}
.diagram .status-main.optimal {
  fill: #67e8f9;
}
.diagram .status-sub {
  text-anchor: start;
  fill: rgba(255, 255, 255, 0.52);
  font: italic 12px Georgia, 'Times New Roman', serif;
}

/* Légende basse */
.cap {
  fill: rgba(255, 255, 255, 0.86);
  font: italic 16.5px Georgia, 'Times New Roman', serif;
}
</style>