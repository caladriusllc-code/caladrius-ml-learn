
<template>
  <div class="mnist-comparison">
    <div class="mnist-panel">
      <div class="panel-title">IMAGE MANUSCRITE</div>

      <div class="mnist-frame">
        <!-- Grille de pixels -->
        <div class="pixel-grid"></div>

        <!-- Chiffre manuscrit -->
        <svg
          class="digit-svg"
          viewBox="0 0 280 280"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <filter id="digit-glow">
              <feGaussianBlur stdDeviation="5" />
            </filter>
          </defs>

          <!-- Halo lumineux -->
          <path
            class="digit-halo"
            d="M65 66 Q137 61 216 70 Q175 130 122 222"
            fill="none"
            stroke="white"
            stroke-width="19"
            stroke-linecap="round"
            filter="url(#digit-glow)"
          />

          <!-- Trait principal -->
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

        <!-- Balayage lumineux -->
        <div class="scan-line"></div>

        <!-- Coins décoratifs -->
        <div class="corner top-left"></div>
        <div class="corner top-right"></div>
        <div class="corner bottom-left"></div>
        <div class="corner bottom-right"></div>
      </div>

      <div class="panel-caption">ÉCHANTILLON MNIST · CHIFFRE 7</div>
    </div>

    <div v-click.fade.right class="mnist-panel numeric-panel">
      <div class="panel-title">VALEURS DES PIXELS</div>

      <div class="matrix-frame">
        <div class="pixel-matrix">
          <div
            v-for="(pixel, index) in pixels"
            :key="index"
            class="pixel"
            :style="{ backgroundColor: `rgb(${pixel},${pixel},${pixel})` }"
          >
            <span :class="{ bright: pixel > 125 }">{{ pixel }}</span>
          </div>
        </div>
      </div>

      <div class="panel-caption">MATRICE 28 × 28 · 784 VALEURS</div>
    </div>
  </div>
</template>

<script setup>
function segmentDistance(px, py, a, b) {
  const dx = b[0] - a[0]
  const dy = b[1] - a[1]
  const t = Math.max(0, Math.min(1,
    ((px - a[0]) * dx + (py - a[1]) * dy) / (dx * dx + dy * dy)
  ))
  const x = a[0] + t * dx
  const y = a[1] + t * dy

  return Math.hypot(px - x, py - y)
}

const points = [
  [65, 66],
  [100, 62],
  [137, 61],
  [175, 65],
  [216, 70],
  [190, 110],
  [165, 150],
  [142, 190],
  [122, 222],
]

const pixels = Array.from({ length: 28 * 28 }, (_, index) => {
  const col = index % 28
  const row = Math.floor(index / 28)
  const x = col * 10 + 5
  const y = row * 10 + 5
  let distance = Infinity

  for (let i = 0; i < points.length - 1; i++) {
    distance = Math.min(distance, segmentDistance(x, y, points[i], points[i + 1]))
  }

  return Math.max(0, Math.min(255, Math.round((8.5 - distance) * 85)))
})
</script>

<style scoped>
.mnist-comparison {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: center;
  gap: 20px;
  width: min(100%, 900px);
  margin: 0 auto;
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

.mnist-frame {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: #080808;
  border: 1px solid #333;
  border-radius: 8px;
  isolation: isolate;
}

.matrix-frame {
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: #080808;
  border: 1px solid #333;
  border-radius: 8px;
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
}

.pixel span.bright {
  color: #111;
}

.pixel-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(#ffffff0b 1px, transparent 1px),
    linear-gradient(90deg, #ffffff0b 1px, transparent 1px);
  background-size: 3.57% 3.57%;
  opacity: 0;
  animation: grid-appear 1.5s ease forwards 0.5s;
}

.digit-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  padding: 7%;
  overflow: visible;
}

.digit-path {
  stroke-dasharray: 420;
  stroke-dashoffset: 420;
  animation: draw-digit 2.2s
    cubic-bezier(.65, 0, .35, 1) forwards;
}

.digit-halo {
  opacity: 0;
  animation: halo-appear 1.5s ease forwards 1.8s;
}

.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  top: 0;
  background: linear-gradient(
    90deg,
    transparent,
    #ffffff,
    transparent
  );
  box-shadow: 0 0 18px #ffffff;
  opacity: 0;
  animation: scan 3.5s ease-in-out infinite 2.4s;
  pointer-events: none;
}

.corner {
  position: absolute;
  width: 15px;
  height: 15px;
  border-color: #888;
  border-style: solid;
  opacity: 0;
  animation: corner-appear .7s ease forwards 1s;
}

.top-left {
  top: 10px;
  left: 10px;
  border-width: 1px 0 0 1px;
}

.top-right {
  top: 10px;
  right: 10px;
  border-width: 1px 1px 0 0;
}

.bottom-left {
  bottom: 10px;
  left: 10px;
  border-width: 0 0 1px 1px;
}

.bottom-right {
  bottom: 10px;
  right: 10px;
  border-width: 0 1px 1px 0;
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

@keyframes halo-appear {
  to { opacity: .35; }
}

@keyframes grid-appear {
  to { opacity: 1; }
}

@keyframes corner-appear {
  to { opacity: 1; }
}

@keyframes scan {
  0% {
    top: 0;
    opacity: 0;
  }
  15% { opacity: .8; }
  85% { opacity: .8; }
  100% {
    top: 100%;
    opacity: 0;
  }
}

@media (max-width: 560px) {
  .mnist-comparison {
    grid-template-columns: 1fr;
    gap: 16px;
    max-width: 420px;
  }

  .numeric-panel {
    max-width: 100%;
  }
}
</style>
