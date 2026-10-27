<template>
  <div class="wrap">
    <div class="panel">
      <!-- Contrôles : niveau de déformation + nouveau tirage -->
      <div class="toolbar">
        <label class="slider">
          <span>Déformation</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            v-model.number="distortion"
            @input="drawAll"
          />
          <span class="slider-val">{{ Math.round(distortion * 100) }} %</span>
        </label>
        <button type="button" class="btn" @click="drawAll">Nouveau tirage</button>
      </div>

      <div class="mnist-grid">
        <figure
          v-for="item in mnistData"
          :key="item.value"
          class="mnist-card"
        >
          <canvas
            :ref="el => setCanvasRef(el, item.value)"
            width="28"
            height="28"
            class="mnist-canvas"
            role="img"
            :aria-label="`Chiffre manuscrit simulé, classe ${item.value}`"
          ></canvas>

          <figcaption class="mnist-caption">
            <span class="label-key">Label</span>
            <span class="label-val">{{ item.value }}</span>
          </figcaption>
        </figure>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MnistSimulator',
  data() {
    return {
      canvasRefs: {},
      distortion: 0.8, // 0 = tracé propre, 1 = très difficile à lire
      mnistData: Array.from({ length: 10 }, (_, i) => ({ value: i }))
    }
  },
  methods: {
    setCanvasRef(el, digit) {
      if (el) {
        this.canvasRefs[digit] = el
      }
    },
    drawAll() {
      this.mnistData.forEach(item => {
        const canvas = this.canvasRefs[item.value]
        if (canvas) {
          this.drawMnistDigit(canvas, item.value)
        }
      })
    },
    drawMnistDigit(canvas, digit) {
      const ctx = canvas.getContext('2d')
      const d = this.distortion
      const r = a => (Math.random() * 2 - 1) * a // aléa dans [-a, a]

      // 1. Fond noir (spécifique au dataset MNIST)
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.shadowBlur = 0
      ctx.fillStyle = '#000000'
      ctx.fillRect(0, 0, 28, 28)

      // 2. Déformation globale : rotation, cisaillement (italique), échelle anisotrope, décalage
      ctx.translate(14, 14)
      ctx.rotate(r(0.55 * d))
      ctx.transform(1, 0, r(0.5 * d), 1, 0, 0)
      ctx.scale(1 + r(0.2 * d), 1 + r(0.2 * d))
      ctx.translate(-14 + r(3 * d), -14 + r(3 * d))

      // 3. Trait d'épaisseur variable avec flou léger (anti-aliasing)
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = Math.max(1.3, 2.5 + r(1.0 * d))
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.shadowColor = '#ffffff'
      ctx.shadowBlur = 1 + Math.random() * 1.5 * d

      // Déformation locale : chaque point de contrôle est perturbé
      const jit = 1.8 * d
      const P = (x, y) => [x + r(jit), y + r(jit)]
      const M = (x, y) => ctx.moveTo(...P(x, y))
      const L = (x, y) => ctx.lineTo(...P(x, y))
      const B = (a, b, c, e, f, g) =>
        ctx.bezierCurveTo(...P(a, b), ...P(c, e), ...P(f, g))
      const E = (x, y, rx, ry, rot) => {
        const cx = x + r(jit)
        const cy = y + r(jit)
        const rX = rx * (1 + r(0.18 * d))
        const rY = ry * (1 + r(0.18 * d))
        const a = rot + r(0.35 * d)
        // moveTo évite le trait parasite entre deux ellipses
        ctx.moveTo(cx + rX * Math.cos(a), cy + rX * Math.sin(a))
        ctx.ellipse(cx, cy, rX, rY, a, 0, Math.PI * 2)
      }

      ctx.beginPath()

      switch (digit) {
        case 0:
          E(14, 14, 7, 9, 0.1)
          break
        case 1:
          M(11, 8); L(14, 5); L(14, 22)
          break
        case 2:
          M(8, 9)
          B(8, 4, 20, 4, 20, 11)
          L(8, 22)
          L(21, 22)
          break
        case 3:
          M(9, 7); L(20, 7); L(13, 13)
          B(19, 13, 21, 22, 9, 21)
          break
        case 4:
          M(18, 22); L(18, 6)
          L(7, 16); L(21, 16)
          break
        case 5:
          M(19, 7); L(10, 7); L(9, 13)
          B(18, 11, 21, 22, 9, 21)
          break
        case 6:
          M(18, 8)
          B(9, 9, 6, 17, 13, 21)
          B(20, 21, 19, 14, 13, 14)
          B(8, 14, 8, 20, 13, 21)
          break
        case 7:
          M(7, 7); L(21, 7); L(12, 22)
          break
        case 8:
          E(14, 10, 4.5, 4, 0)
          E(14, 18, 5.5, 5, 0)
          break
        case 9:
          E(14, 10, 5, 4.5, 0)
          M(19, 10); L(17, 20); L(12, 22)
          break
      }
      ctx.stroke()

      // 4. Trous dans le trait (encre manquante), plus fréquents si la déformation est forte
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.shadowBlur = 0
      ctx.fillStyle = '#000000'
      const gaps = Math.round(Math.random() * 3 * d)
      for (let g = 0; g < gaps; g++) {
        ctx.beginPath()
        ctx.arc(7 + Math.random() * 14, 6 + Math.random() * 16, 0.9 + Math.random() * 1.2, 0, Math.PI * 2)
        ctx.fill()
      }

      // 5. Bruit synthétique : fond granuleux + quelques pixels parasites
      const imgData = ctx.getImageData(0, 0, 28, 28)
      const data = imgData.data
      const bg = 18 + 32 * d
      for (let i = 0; i < data.length; i += 4) {
        if (data[i] < 20) {
          let v = Math.floor(Math.random() * bg)
          if (Math.random() < 0.012 * d) {
            v = 110 + Math.floor(Math.random() * 90) // pixel parasite
          }
          data[i] = v
          data[i + 1] = v
          data[i + 2] = v
        }
      }
      ctx.putImageData(imgData, 0, 0)
    }
  },
  mounted() {
    this.$nextTick(this.drawAll)
  }
}
</script>

<style scoped>
.wrap {
  display: flex;
  justify-content: center;
  padding: 1rem;
  width: 100%;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 640px;
  width: 100%;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
}

.slider {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.slider input[type='range'] {
  width: 160px;
}

.slider-val {
  min-width: 3ch;
  font-variant-numeric: tabular-nums;
  opacity: 0.75;
}

.btn {
  padding: 0.35rem 0.9rem;
  font: inherit;
  color: inherit;
  background: rgba(128, 128, 128, 0.12);
  border: 1px solid rgba(128, 128, 128, 0.4);
  border-radius: 6px;
  cursor: pointer;
}

.btn:hover {
  background: rgba(128, 128, 128, 0.22);
}

.btn:focus-visible,
.slider input:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}

.mnist-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  width: 100%;
}

.mnist-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  padding: 0.75rem;
  background: rgba(128, 128, 128, 0.08);
  border: 1px solid rgba(128, 128, 128, 0.3);
  border-radius: 8px;
}

/* Le canvas 28x28 est agrandi sans lissage pour que les pixels restent visibles */
.mnist-canvas {
  width: 100%;
  max-width: 96px;
  aspect-ratio: 1 / 1;
  image-rendering: pixelated;
  border: 1px solid rgba(128, 128, 128, 0.4);
  border-radius: 4px;
  background: #000;
}

.mnist-caption {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  font-size: 0.85rem;
}

.label-key {
  opacity: 0.65;
}

.label-val {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-weight: 600;
  font-size: 1.1rem;
}
</style>