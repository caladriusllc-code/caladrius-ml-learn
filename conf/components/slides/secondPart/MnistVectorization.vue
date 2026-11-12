<template>
  <div class="mnist-vectorization">
    <!-- Réserve un clic Slidev -->
    <span v-click class="hidden" />

    <!-- ========== MATRICE M ========== -->
    <div
      class="panel matrix-panel"
      :style="{
        width: `calc(var(--W) * ${1 - c})`,
        marginRight: `calc(48px * ${p * (1 - c)})`,
        opacity: 1 - c * 0.6
      }"
    >
      <div class="panel-inner matrix-inner">
        <div class="representation-label">
          MATRICE M
          <span>28 × 28</span>
        </div>

        <div class="matrix-frame">
          <div class="bracket left" />
          <div class="bracket right" />

          <div class="pixel-matrix">
            <div
              v-for="(row, r) in rows"
              :key="r"
              class="mrow"
              :style="{
                transform: `translateX(${row.e * 110}px)`,
                opacity: 1 - row.e
              }"
            >
              <div
                v-for="col in 28"
                :key="col"
                class="cell"
                :style="{ backgroundColor: cellBg[r * 28 + col - 1] }"
              >
                <span :class="{ zero: cellText[r * 28 + col - 1] === '0' }">
                  {{ cellText[r * 28 + col - 1] }}
                </span>
              </div>

              <!-- Halo cyan qui accompagne la ligne pendant son départ -->
              <div
                class="row-glow"
                :style="{ opacity: row.glow * 0.6 }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== VECTEUR x ========== -->
    <div
      class="panel vector-panel"
      :style="{ width: `calc(var(--V) * ${p})`, opacity: p }"
    >
      <div class="panel-inner vector-inner">
        <div class="representation-label">
          VECTEUR x
          <span>784 × 1</span>
        </div>

        <div class="vector-frame">
          <div class="vector-bracket left-bracket" />

          <div class="vector-content">
            <div
              v-for="(item, i) in vectorItems"
              :key="i"
              class="vector-row"
              :class="{ ellipsis: item.ellipsis }"
              :style="{
                opacity: item.reveal,
                transform: `translateX(${(1 - item.reveal) * -24}px)`
              }"
            >
              <template v-if="item.ellipsis">
                <span class="vector-index">⋮</span>
                <span class="vector-value">⋮</span>
              </template>
              <template v-else>
                <span class="vector-index">x<sub>{{ item.index + 1 }}</sub></span>
                <span
                  class="vector-value"
                  :class="{ zero: item.text === '0' }"
                  :style="{ backgroundColor: item.bg }"
                >
                  {{ item.text }}
                </span>
              </template>
            </div>
          </div>

          <div class="vector-bracket right-bracket" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useSlideContext } from '@slidev/client'

/* ---------- Génération du chiffre 7 ---------- */
function segmentDistance(px, py, a, b) {
  const dx = b[0] - a[0]
  const dy = b[1] - a[1]
  const t = Math.max(0, Math.min(1,
    ((px - a[0]) * dx + (py - a[1]) * dy) / (dx * dx + dy * dy)
  ))
  return Math.hypot(px - a[0] - t * dx, py - a[1] - t * dy)
}

const points = [
  [65, 66], [100, 62], [137, 61], [175, 65], [216, 70],
  [190, 110], [165, 150], [142, 190], [122, 222]
]

const pixels = Array.from({ length: 784 }, (_, index) => {
  const x = (index % 28) * 10 + 5
  const y = Math.floor(index / 28) * 10 + 5
  let distance = Infinity
  for (let i = 0; i < points.length - 1; i++) {
    distance = Math.min(distance, segmentDistance(x, y, points[i], points[i + 1]))
  }
  return Math.max(0, Math.min(255, Math.round((8.5 - distance) * 85)))
})

/* ---------- Valeurs affichées ---------- */
// Format court : 0, 1, ou une décimale (0.5) → les cases restent lisibles
function fmt(v) {
  const x = v / 255
  if (x === 0) return '0'
  if (x >= 0.95) return '1'
  return x.toFixed(1)
}

// Teinte de fond selon la valeur : le 7 apparaît comme une carte de chaleur
const tint = v => (v === 0 ? '#ffffff' : `rgba(14, 165, 233, ${0.12 + (v / 255) * 0.5})`)

const cellText = pixels.map(fmt)
const cellBg = pixels.map(tint)

/* ---------- Chronologie (t : 0 → 1) ---------- */
const DURATION = 4500
const ROW_START = 0.02
const ROW_SPAN = 0.66
const ROW_LEN = 0.2

const clamp01 = x => Math.max(0, Math.min(1, x))
const smooth = x => x * x * (3 - 2 * x)

const t = ref(0)

const p = computed(() => smooth(clamp01(t.value / 0.04)))
const c = computed(() => smooth(clamp01((t.value - 0.86) / 0.14)))

const rows = computed(() =>
  Array.from({ length: 28 }, (_, r) => {
    const local = clamp01((t.value - ROW_START - (r / 28) * ROW_SPAN) / ROW_LEN)
    return { e: smooth(local), glow: Math.sin(Math.PI * local) }
  })
)

/* ---------- Vecteur : entrées affichées ---------- */
const firstNZ = Math.max(3, cellText.findIndex(s => s !== '0'))

const shownIndices = [
  0, 1, 2,
  null,
  firstNZ - 1, firstNZ, firstNZ + 1,
  null,
  781, 782, 783
]

const startOf = idx =>
  ROW_START + (Math.floor(idx / 28) / 28) * ROW_SPAN + ((idx % 28) / 28) * ROW_LEN

const baseItems = shownIndices.map((idx, i) => {
  if (idx !== null) {
    return { index: idx, text: cellText[idx], bg: cellBg[idx], start: startOf(idx) }
  }
  const prev = startOf(shownIndices[i - 1])
  const next = startOf(shownIndices[i + 1])
  return { ellipsis: true, start: (prev + next) / 2 }
})

const vectorItems = computed(() =>
  baseItems.map(item => ({
    ...item,
    reveal: smooth(clamp01((t.value - item.start) / 0.04))
  }))
)

/* ---------- Animation & synchronisation Slidev ---------- */
let raf = null
function animateTo(target) {
  cancelAnimationFrame(raf)
  const from = t.value
  const start = performance.now()
  const dur = DURATION * Math.abs(target - from)
  if (dur === 0) return

  const step = now => {
    const k = clamp01((now - start) / dur)
    t.value = from + (target - from) * k
    if (k < 1) raf = requestAnimationFrame(step)
  }
  raf = requestAnimationFrame(step)
}

const { $clicks } = useSlideContext()

onMounted(() => { t.value = $clicks.value >= 1 ? 1 : 0 })
watch($clicks, n => animateTo(n >= 1 ? 1 : 0))
onBeforeUnmount(() => cancelAnimationFrame(raf))
</script>

<style scoped>
.mnist-vectorization {
  /* Tailles en px : le canvas Slidev (980×552) est mis à l'échelle automatiquement */
  --W: 640px;   /* largeur de la matrice */
  --H: 470px;   /* hauteur de la matrice (et du vecteur) */
  --V: 210px;   /* largeur du vecteur */

  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: monospace;
}

/* ---------- Panneaux ---------- */
.panel {
  flex: none;
  overflow: hidden;
}

.panel-inner {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.matrix-inner { width: var(--W); }
.vector-inner { width: var(--V); }

.representation-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #999;
  font-size: 13px;
  letter-spacing: 2px;
  white-space: nowrap;
}

.representation-label span {
  color: #666;
  font-size: 11px;
  letter-spacing: 1px;
}

/* ---------- Matrice : fond blanc, texte noir ---------- */
.matrix-frame {
  position: relative;
  width: var(--W);
  height: var(--H);
  background: #ffffff;
  border-radius: 6px;
  overflow: hidden;
}

.pixel-matrix {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 10px 36px;    /* place pour les crochets */
  box-sizing: border-box;
}

.mrow {
  position: relative;
  flex: 1 1 0;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(28, minmax(0, 1fr));
  will-change: transform, opacity;
}

.cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  border: 1px solid #0000000d;
}

.cell span {
  color: #111;
  font-weight: 700;
  font-size: 10.5px;
  line-height: 1;
}

.cell span.zero {
  color: #c8c8c8;
  font-weight: 400;
}

.row-glow {
  position: absolute;
  inset: 0;
  background: rgba(34, 211, 238, 0.7);
  mix-blend-mode: multiply;
  pointer-events: none;
}

/* Crochets de la matrice */
.bracket {
  position: absolute;
  top: 6px;
  bottom: 6px;
  width: 16px;
  border: 4px solid #111;
  z-index: 2;
}

.bracket.left {
  left: 8px;
  border-right: none;
}

.bracket.right {
  right: 8px;
  border-left: none;
}

/* ---------- Vecteur colonne ---------- */
.vector-frame {
  width: var(--V);
  height: var(--H);
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: 10px;
  padding: 10px 14px;
  box-sizing: border-box;
  background: #ffffff;
  border-radius: 6px;
}

.vector-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 6px 0;
}

.vector-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 8px;
  text-align: center;
  font-size: 16px;
  will-change: transform, opacity;
}

.vector-index {
  color: #666;
}

.vector-value {
  color: #111;
  font-weight: 700;
  border-radius: 4px;
  padding: 3px 0;
}

.vector-value.zero {
  color: #c8c8c8;
  font-weight: 400;
}

.vector-row.ellipsis {
  font-size: 24px;
}

.vector-bracket {
  width: 14px;
  border-color: #111;
  border-style: solid;
}

.left-bracket  { border-width: 4px 0 4px 4px; }
.right-bracket { border-width: 4px 4px 4px 0; }
</style>