<!-- components/GearMechanism.vue

  Trois roues dentées engrenées : « Apprentissage » entraîne « Réflexion »,
  qui entraîne une petite roue de sortie. Les roues tournent en sens
  alterné, et plus une roue a de dents, plus elle tourne lentement.

  La rotation est pilotée en JavaScript (requestAnimationFrame) : elle ne
  dépend ni du CSS ni du réglage « réduire les animations » du système.

  Props
    active    true = les roues tournent, false = à l'arrêt (ex. piloté par les clics)
    duration  secondes pour un tour de la plus grande roue (défaut : 16)
    learn     texte de la première roue (défaut : « Apprentissage »)
    think     texte de la deuxième roue (défaut : « Réflexion »)

  Exemple dans une slide Slidev (tourne à partir du 1er clic) :
    <GearMechanism :active="clicks >= 1" />
-->
<template>
  <svg
    class="gears"
    :viewBox="view"
    role="img"
    :aria-label="`Engrenage : ${learn} entraîne ${think}`"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g v-for="g in gears" :key="g.id">
      <!-- Partie qui tourne : corps denté, anneau, moyeu -->
      <g :transform="`rotate(${rotation(g)} ${g.cx} ${g.cy})`">
        <path
          :d="g.path"
          :fill="g.color"
          fill-rule="evenodd"
          :stroke="g.stroke"
          stroke-width="1.5"
          stroke-linejoin="round"
        />
        <circle
          :cx="g.cx"
          :cy="g.cy"
          :r="g.r * 0.72"
          fill="none"
          stroke="#ffffff"
          stroke-opacity="0.28"
          stroke-width="1.5"
        />
        <template v-if="!g.label">
          <circle :cx="g.cx" :cy="g.cy" :r="g.r * 0.4" fill="#e8ecef" :stroke="g.stroke" stroke-width="1.5" />
          <circle :cx="g.cx" :cy="g.cy" :r="g.r * 0.12" :fill="g.stroke" />
        </template>
      </g>

      <!-- Plaque de texte : fixe, elle ne tourne pas avec la roue -->
      <template v-if="g.label">
        <circle
          :cx="g.cx"
          :cy="g.cy"
          :r="g.r * 0.6"
          fill="#ffffff"
          :stroke="g.stroke"
          stroke-width="2"
        />
        <text
          :x="g.cx"
          :y="g.cy"
          text-anchor="middle"
          dominant-baseline="central"
          :font-size="g.fs"
          font-weight="600"
          fill="#1f2a33"
        >
          {{ g.label }}
        </text>
      </template>
    </g>
  </svg>
</template>

<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  active: { type: Boolean, default: true },
  duration: { type: Number, default: 16 },
  learn: { type: String, default: 'Apprentissage' },
  think: { type: String, default: 'Réflexion' }
})

const M = 9 // module : taille des dents, identique pour toutes les roues (condition pour engrener)
const PAD = 14

const rad = (deg) => (deg * Math.PI) / 180
const frac = (x) => ((x % 1) + 1) % 1

// Path SVG d'une roue : dents + trous d'allègement (fill-rule evenodd)
function gearPath(cx, cy, n, r, offset) {
  const ro = r + 0.4 * M // rayon de tête
  const rr = r - 0.55 * M // rayon de pied
  const step = 360 / n
  const pt = (R, a) =>
    `${(cx + R * Math.cos(rad(a))).toFixed(2)} ${(cy + R * Math.sin(rad(a))).toFixed(2)}`

  let d = `M ${pt(rr, offset - 0.28 * step)}`
  for (let k = 0; k < n; k++) {
    const a = offset + k * step
    d +=
      ` L ${pt(ro, a - 0.16 * step)}` +
      ` A ${ro} ${ro} 0 0 1 ${pt(ro, a + 0.16 * step)}` +
      ` L ${pt(rr, a + 0.28 * step)}` +
      ` A ${rr} ${rr} 0 0 1 ${pt(rr, a + 0.72 * step)}`
  }
  d += ' Z'

  const holes = n >= 14 ? 6 : 5
  const hr = r * 0.09
  for (let i = 0; i < holes; i++) {
    const a = offset + (i * 360) / holes
    const hx = cx + r * 0.78 * Math.cos(rad(a))
    const hy = cy + r * 0.78 * Math.sin(rad(a))
    d +=
      ` M ${(hx + hr).toFixed(2)} ${hy.toFixed(2)}` +
      ` a ${hr} ${hr} 0 1 0 ${-2 * hr} 0 a ${hr} ${hr} 0 1 0 ${2 * hr} 0 Z`
  }
  return d
}

// Géométrie : calculée une seule fois (ne dépend pas de l'angle de rotation)
const gears = computed(() => {
  // dir = direction (en degrés) de la roue précédente vers celle-ci
  const specs = [
    { id: 'learn', n: 20, label: props.learn, color: '#23406f', stroke: '#14284a', fs: 14 },
    { id: 'think', n: 14, label: props.think, color: '#b5832a', stroke: '#6e4d14', fs: 12.5, dir: -28 },
    { id: 'out', n: 10, label: '', color: '#5d6872', stroke: '#2f3a42', fs: 0, dir: 38 }
  ]

  // 1) positions et phases : chaque dent doit tomber dans un creux de la roue voisine
  const raw = []
  specs.forEach((s, i) => {
    const r = (M * s.n) / 2
    let cx = 0
    let cy = 0
    let offset = 0
    if (i > 0) {
      const p = raw[i - 1]
      const dist = p.r + r
      cx = p.cx + dist * Math.cos(rad(s.dir))
      cy = p.cy + dist * Math.sin(rad(s.dir))
      const phase = frac((s.dir - p.offset) / (360 / p.n)) // 0 = dent, 0.5 = creux
      offset = s.dir + 180 - frac(phase + 0.5) * (360 / s.n)
    }
    raw.push({ ...s, r, cx, cy, offset })
  })

  // 2) recadrage : tout est décalé pour que la boîte englobante commence à (PAD, PAD)
  const outer = (g) => g.r + 0.4 * M
  const minX = Math.min(...raw.map((g) => g.cx - outer(g)))
  const minY = Math.min(...raw.map((g) => g.cy - outer(g)))

  return raw.map((g, i) => {
    const cx = g.cx - minX + PAD
    const cy = g.cy - minY + PAD
    return {
      ...g,
      cx,
      cy,
      sign: i % 2 === 1 ? -1 : 1, // sens alterné
      ratio: raw[0].n / g.n, // plus de dents = plus lent
      path: gearPath(cx, cy, g.n, g.r, g.offset)
    }
  })
})

const view = computed(() => {
  const outer = (g) => g.r + 0.4 * M
  const w = Math.max(...gears.value.map((g) => g.cx + outer(g))) + PAD
  const h = Math.max(...gears.value.map((g) => g.cy + outer(g))) + PAD
  return `0 0 ${w.toFixed(1)} ${h.toFixed(1)}`
})

// ---------- Animation ----------
// `turn` = angle de la première roue (en degrés). Les autres roues en
// découlent par le rapport de dents : l'engrènement reste donc parfait.
const turn = ref(0)
const rotation = (g) => (g.sign * turn.value * g.ratio).toFixed(2)

let frame = null
let last = 0

function tick(now) {
  if (!props.active) {
    frame = null
    return
  }
  const dt = last ? Math.min((now - last) / 1000, 0.1) : 0 // plafonné : pas de saut après un onglet inactif
  last = now
  turn.value += (360 / props.duration) * dt // pas de modulo : sinon les autres roues « sauteraient » à chaque tour
  frame = requestAnimationFrame(tick)
}

function start() {
  if (frame === null) {
    last = 0
    frame = requestAnimationFrame(tick)
  }
}

function stop() {
  if (frame !== null) cancelAnimationFrame(frame)
  frame = null
}

onMounted(() => {
  if (props.active) start()
})

watch(
  () => props.active,
  (on) => (on ? start() : stop())
)

onBeforeUnmount(stop)
</script>

<style scoped>
.gears {
  display: block;
  width: 100%;
  height: 100%;
}
</style>