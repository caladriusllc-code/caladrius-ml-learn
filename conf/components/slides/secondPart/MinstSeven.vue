
<template>
  <div class="mnist-comparison">

    <!-- 1. Image manuscrite originale -->
    <div class="mnist-panel">
      <div class="panel-title">IMAGE ORIGINALE</div>

      <div class="mnist-frame">
        <svg viewBox="0 0 280 280">
          <path
            class="digit-path"
            d="M65 66 Q137 61 216 70 Q175 130 122 222"
            fill="none"
            stroke="white"
            stroke-width="13"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>

      <div class="panel-caption">
        CHIFFRE MANUSCRIT · 7
      </div>
    </div>

    <!-- 2. Matrice numérique : apparition au deuxième clic -->
    <div
      v-click.fade.right
      class="mnist-panel numeric-panel"
    >
      <div class="panel-title">REPRÉSENTATION NUMÉRIQUE</div>

      <div class="matrix-frame">
        <div class="pixel-matrix">
          <div
            v-for="(pixel, index) in pixels"
            :key="index"
            class="pixel"
            :style="{
              backgroundColor: `rgb(${pixel},${pixel},${pixel})`
            }"
          >
            <span
              :class="{ bright: pixel > 125 }"
            >
              {{ pixel }}
            </span>
          </div>
        </div>
      </div>

      <div class="panel-caption">
        MATRICE DE 28 × 28 · 784 VALEURS
      </div>
    </div>

  </div>
</template>

<script setup>

// Distance entre un point et un segment
function segmentDistance(px, py, a, b) {
  const dx = b[0] - a[0]
  const dy = b[1] - a[1]

  const t = Math.max(0, Math.min(1,
    ((px - a[0]) * dx + (py - a[1]) * dy)
    / (dx * dx + dy * dy)
  ))

  const x = a[0] + t * dx
  const y = a[1] + t * dy

  return Math.hypot(px - x, py - y)
}

// Approximation du même tracé SVG
const points = [
  [65, 66],
  [100, 62],
  [137, 61],
  [175, 65],
  [216, 70],
  [190, 110],
  [165, 150],
  [142, 190],
  [122, 222]
]

// Calcul des 784 intensités
const pixels = Array.from({ length: 28 * 28 }, (_, index) => {
  const col = index % 28
  const row = Math.floor(index / 28)

  const x = col * 10 + 5
  const y = row * 10 + 5

  let distance = Infinity

  for (let i = 0; i < points.length - 1; i++) {
    distance = Math.min(
      distance,
      segmentDistance(x, y, points[i], points[i + 1])
    )
  }

  // Intensité de 0 à 255
  const intensity = Math.max(
    0,
    Math.min(255, Math.round((8.5 - distance) * 85))
  )

  return intensity
})

</script>

<style scoped>
.mnist-comparison {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: center;
  gap: 18px;
  width: 100%;
  max-width: 850px;
  margin: auto;
  color: white;
  font-family: monospace;
}

.mnist-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-title {
  color: #999;
  font-size: 10px;
  letter-spacing: 2px;
  text-align: center;
}

.mnist-frame,
.matrix-frame {
  width: 100%;
  aspect-ratio: 1;
  background: #050505;
  border: 1px solid #383838;
  border-radius: 6px;
  overflow: hidden;
}

.mnist-frame svg {
  width: 100%;
  height: 100%;
  padding: 5%;
}

.digit-path {
  stroke-dasharray: 420;
  stroke-dashoffset: 420;
  animation: draw-digit 2.2s
    cubic-bezier(.65, 0, .35, 1) forwards;
}

.pixel-matrix {
  display: grid;
  width: 100%;
  height: 100%;
  grid-template-columns: repeat(28, minmax(0, 1fr));
  grid-template-rows: repeat(28, minmax(0, 1fr));
}

.pixel {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 0;
  border: 1px solid rgba(110, 110, 110, .17);
  overflow: hidden;
}

.pixel span {
  color: #777;
  font-size: clamp(3px, .65vw, 6px);
  line-height: 1;
  transform: scale(.95);
}

.pixel span.bright {
  color: #111;
}

.panel-caption {
  color: #888;
  font-size: 9px;
  letter-spacing: 1px;
  text-align: center;
}

@keyframes draw-digit {
  to {
    stroke-dashoffset: 0;
  }
}

@media (max-width: 500px) {
  .mnist-comparison {
    gap: 8px;
  }

  .panel-title {
    font-size: 8px;
    letter-spacing: 1px;
  }

  .pixel span {
    font-size: 3px;
  }
}
</style>
