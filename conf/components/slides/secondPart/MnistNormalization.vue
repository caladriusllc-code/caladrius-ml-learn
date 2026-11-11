<template>
  <div class="mnist-normalization">
    <!-- Enregistre 1 clic dans Slidev (sans rien afficher) -->
    <span v-click class="hidden" />

    <div class="mnist-panel">
      <Transition name="fade" mode="out-in">
        <div :key="phase" class="panel-label">
          {{ phase === 'norm' ? 'NORMALISATION' : 'IMAGE ORIGINALE' }}
        </div>
      </Transition>

      <div class="matrix-frame">
        <div class="pixel-matrix">
          <div
            v-for="(cell, index) in cells"
            :key="index"
            class="pixel"
            :style="{
              backgroundColor: cell.bg,
              boxShadow: `inset 0 0 0 100px rgba(34, 211, 238, ${cell.glow * 0.55})`,
              transform: `scale(${1 + cell.glow * 0.5})`,
              zIndex: cell.glow > 0.05 ? 1 : 0
            }"
          >
            <span :class="{ dark: cell.dark }">{{ cell.text }}</span>
          </div>
        </div>
      </div>

      <Transition name="fade" mode="out-in">
        <div :key="phase" class="range-label">
          <template v-if="phase === 'norm'">0 ≤ x ≤ 1</template>
          <template v-else>0 ≤ x ≤ 255</template>
        </div>
      </Transition>
    </div>

    <!-- Formule LaTeX : apparaît une fois la normalisation terminée -->
    <div class="formula" :class="{ show: done }">
      <div class="formula-inner" v-html="formulaHtml" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useSlideContext } from '@slidev/client'
import katex from 'katex'

/* ---------- Formule ---------- */
const formulaHtml = katex.renderToString(
  String.raw`\begin{aligned}
    x_{\text{norm}} &= \frac{x - x_{\min}}{x_{\max} - x_{\min}} \\[1.2em]
                    &= \frac{x - 0}{255 - 0} \\[1.2em]
                    &= \frac{x}{255}
  \end{aligned}`,
  { displayMode: true, throwOnError: false }
)

/* ---------- Génération de l'image ---------- */
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

const normalized = pixels.map(v => v / 255)

/* ---------- Animation ---------- */
const DURATION = 2600
const SPREAD = 0.6
const CENTER = 13.5
const MAX_DIST = Math.hypot(CENTER, CENTER)

const delays = pixels.map((_, i) => {
  const col = i % 28
  const row = Math.floor(i / 28)
  return (Math.hypot(col - CENTER, row - CENTER) / MAX_DIST) * SPREAD
})

const easeOutCubic = x => 1 - Math.pow(1 - x, 3)
const clamp01 = x => Math.max(0, Math.min(1, x))

const t = ref(0)
const phase = computed(() => (t.value > 0.5 ? 'norm' : 'raw'))
const done = computed(() => t.value >= 1)   // normalisation terminée

const cells = computed(() =>
  pixels.map((raw, i) => {
    const local = clamp01((t.value - delays[i]) / (1 - SPREAD))
    const e = easeOutCubic(local)
    const norm = normalized[i]
    const v = raw + (norm - raw) * e

    let text
    if (local <= 0) text = String(raw)
    else if (local >= 1) text = norm.toFixed(1)
    else text = v >= 10 ? String(Math.round(v)) : v.toFixed(1)

    const glow = Math.sin(Math.PI * local) * (raw > 0 ? 1 : 0.3)
    const g = Math.round(norm * 255)

    return { text, glow, bg: `rgb(${g}, ${g}, ${g})`, dark: norm > 0.5 }
  })
)

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
watch($clicks, c => animateTo(c >= 1 ? 1 : 0))
onBeforeUnmount(() => cancelAnimationFrame(raf))
</script>

<style scoped>
.mnist-normalization {
  width: 100%;
  margin: auto;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-family: monospace;
}

.mnist-panel {
  flex: none;
  width: min(55vw, 55vh);
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-label,
.range-label {
  text-align: center;
  color: #999;
  font-size: 14px;
  letter-spacing: 2px;
  min-height: 1.2em;
}

.range-label {
  letter-spacing: 1px;
}

.matrix-frame {
  width: 100%;
  aspect-ratio: 1;
  background: #050505;
  border: 1px solid #383838;
  border-radius: 5px;
  overflow: hidden;
  container-type: inline-size;
}

.pixel-matrix {
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: repeat(28, minmax(0, 1fr));
  grid-template-rows: repeat(28, minmax(0, 1fr));
}

.pixel {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  border: 1px solid #77777720;
  will-change: transform;
}

.pixel span {
  color: #888;
  font-size: calc(100cqw / 28 / 3.3);
  line-height: 1;
}

.pixel span.dark {
  color: #111;
}

/* ---------- Formule ---------- */
.formula {
  flex: none;
  max-width: 0;
  margin-left: 0;
  overflow: hidden;
  opacity: 0;
  transition:
    max-width 0.8s ease,
    margin-left 0.8s ease,
    opacity 0.6s ease 0.4s;
}

.formula.show {
  max-width: 32vw;
  margin-left: 40px;
  opacity: 1;
}

.formula-inner {
  width: max-content;
  font-size: clamp(16px, 3.2vh, 32px);
  color: #222222;
}

.formula-inner :deep(.katex-display) {
  margin: 0;
  text-align: left;
}

/* ---------- Transitions de labels ---------- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 500px) {
  .mnist-panel {
    width: 100%;
  }
  .panel-label,
  .range-label {
    font-size: 10px;
  }
}
</style>