<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useIsSlideActive } from '@slidev/client'

// Chiffres de 12 x 12 pixels, avec les deux chiffres qui leur ressemblent le plus
const DIGITS = [
  {
    d: 3, rivals: [8, 5],
    rows: [
      '...######...',
      '..##....##..',
      '........##..',
      '.......##...',
      '....####....',
      '.......###..',
      '........###.',
      '........###.',
      '........##..',
      '..##....##..',
      '...######...',
      '............',
    ],
  },
  {
    d: 7, rivals: [1, 9],
    rows: [
      '..########..',
      '..########..',
      '........##..',
      '.......##...',
      '.......##...',
      '......##....',
      '......##....',
      '.....##.....',
      '.....##.....',
      '....##......',
      '....##......',
      '............',
    ],
  },
  {
    d: 1, rivals: [7, 4],
    rows: [
      '.....##.....',
      '....###.....',
      '...####.....',
      '.....##.....',
      '.....##.....',
      '.....##.....',
      '.....##.....',
      '.....##.....',
      '.....##.....',
      '.....##.....',
      '...######...',
      '............',
    ],
  },
  {
    d: 0, rivals: [6, 8],
    rows: [
      '....####....',
      '...##..##...',
      '..##....##..',
      '..##....##..',
      '..##....##..',
      '..##....##..',
      '..##....##..',
      '..##....##..',
      '..##....##..',
      '...##..##...',
      '....####....',
      '............',
    ],
  },
  {
    d: 4, rivals: [9, 1],
    rows: [
      '......##....',
      '.....###....',
      '....####....',
      '...##.##....',
      '..##..##....',
      '.##...##....',
      '.##########.',
      '......##....',
      '......##....',
      '......##....',
      '......##....',
      '............',
    ],
  },
]
const N = 12
const CELL = 24
// Quantité de bruit à chaque étape : de l'image illisible à l'image nette
const NOISE = [0.95, 0.8, 0.65, 0.5, 0.37, 0.25, 0.14, 0.06, 0]
const STEP_MS = 650
const HOLD_MS = 2200 // pause sur l'image nette avant le chiffre suivant

const reduce = typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches
const canvas = ref<HTMLCanvasElement>()
const cur = ref(0)
const conf = ref(0)
const done = ref(false)
const newNoise = () => Array.from({ length: N * N }, () => Math.random())
let rnd = newNoise()
let runId = 0
const wait = (ms: number) => new Promise(r => setTimeout(r, ms))

function draw(noise: number) {
  const ctx = canvas.value?.getContext('2d')
  if (!ctx) return
  DIGITS[cur.value].rows.forEach((row, y) => {
    for (let x = 0; x < N; x++) {
      const base = row[x] === '#' ? 1 : 0
      const v = base * (1 - noise) + rnd[y * N + x] * noise
      // du gris-bleu clair (fond) vers l'encre
      ctx.fillStyle = `rgb(${Math.round(238 - 211 * v)},${Math.round(241 - 205 * v)},${Math.round(245 - 197 * v)})`
      ctx.fillRect(x * CELL, y * CELL, CELL, CELL)
    }
  })
}

// Scores du réseau : plus l'image est nette, plus le bon chiffre domine ;
// les deux chiffres qui lui ressemblent restent ses concurrents
const top3 = computed(() => {
  const { d, rivals } = DIGITS[cur.value]
  const logits = Array(10).fill(0)
  logits[d] = conf.value * 6
  logits[rivals[0]] = conf.value * 3.2
  logits[rivals[1]] = conf.value * 2.8
  const e = logits.map(Math.exp)
  const sum = e.reduce((a, b) => a + b)
  return e
    .map((v, k) => ({ d: k, p: Math.round((v / sum) * 100) }))
    .sort((a, b) => b.p - a.p)
    .slice(0, 3)
})

async function play() {
  const id = ++runId
  done.value = false
  if (reduce) {
    // Mouvement réduit : une seule image nette, sans boucle
    cur.value = 0
    conf.value = 1
    draw(0)
    done.value = true
    return
  }
  let i = 0
  while (id === runId) {
    cur.value = i % DIGITS.length
    rnd = newNoise()
    for (const n of NOISE) {
      conf.value = 1 - n
      draw(n)
      await wait(STEP_MS)
      if (id !== runId) return
    }
    done.value = true
    await wait(HOLD_MS)
    if (id !== runId) return
    done.value = false
    i++
  }
}

const active = useIsSlideActive()
onMounted(() => { if (active.value) play() })
// La boucle s'arrête dès qu'on quitte la slide et repart en y revenant
watch(active, (v) => { v ? play() : runId++ })
onBeforeUnmount(() => { runId++ })
</script>

<template>
  <div class="wrap">
    <div class="left">
      <h1 class="title">Comment une machine apprend à voir.</h1>
      <div class="sub"><slot /></div>
    </div>

    <div class="right">
      <canvas
        ref="canvas"
        :width="N * CELL"
        :height="N * CELL"
        role="img"
        aria-label="Image de 12 par 12 pixels d'un chiffre manuscrit, d'abord bruitée puis nette"
      />
      <div class="rows">
        <div
          v-for="(c, i) in top3"
          :key="c.d"
          class="row"
          :class="{ pick: done && i === 0 }"
        >
          <span class="digit">{{ c.d }}</span>
          <span class="bar" :style="{ width: c.p + '%' }" />
          <span class="pct">{{ c.p }}%</span>
        </div>
      </div>
      <p class="verdict" :class="{ on: done }">
        Le réseau reconnaît un {{ DIGITS[cur].d }}.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: flex; align-items: center; gap: 56px; }
.left { flex: 1; }
.title {
  font-size: 50px;
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.03em;
  max-width: 460px;
  margin: 0 0 24px;
}
.sub { font-size: 19px; line-height: 1.5; max-width: 460px; }
.sub :deep(.theme) { margin-bottom: 20px; }
.sub :deep(strong) { font-weight: 600; }

.right { width: 288px; }
canvas {
  display: block;
  width: 288px;
  height: 288px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px rgba(27, 36, 48, 0.15);
}
.rows { margin-top: 18px; }
.row {
  display: grid;
  grid-template-columns: 28px 1fr 44px;
  align-items: center;
  gap: 12px;
  margin: 6px 0;
  color: var(--muted);
}
.digit { font-size: 20px; font-weight: 600; }
.bar {
  height: 8px;
  border-radius: 4px;
  background: currentColor;
  opacity: 0.4;
  transition: width 0.5s ease;
}
.pct { text-align: right; font-size: 15px; }
.row.pick { color: var(--cobalt); }
.row.pick .bar { opacity: 1; }

.verdict {
  margin: 14px 0 0;
  font-size: 16px;
  color: var(--cobalt);
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.6s ease;
}
.verdict.on { opacity: 1; }

@media (prefers-reduced-motion: reduce) {
  .bar, .verdict { transition: none; }
}
</style>