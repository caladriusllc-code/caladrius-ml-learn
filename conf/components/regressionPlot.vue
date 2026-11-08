<!--
  RegressionPlot : repère (axes x/y) + nuage de points qui flottent légèrement.
  Pensé pour le slot #media de splitSide (frame="none").

  Props
    n          Nombre de points (défaut 40)
    seed       Graine du générateur aléatoire : même graine = même nuage (défaut 7)
    amplitude  Amplitude du flottement en unités du repère SVG, ~px (défaut 4)
    grid       Affiche la grille discrète (défaut true)

  Notes pour la suite (descente de gradient)
    - `points` contient les vraies coordonnées (domaine 0..10 sur x et y).
    - Le flottement est purement visuel (animation CSS) et ne modifie pas `points`.
    - sx() / sy() convertissent une coordonnée de données en coordonnée SVG :
      utilise-les pour tracer la droite y = w·x + b.
-->
<template>
  <svg
    class="plot"
    :viewBox="`0 0 ${W} ${H}`"
    role="img"
    aria-label="Nuage de points dans un repère x, y"
  >
    <defs>
      <marker
        id="axis-arrow"
        viewBox="0 0 10 10"
        refX="8"
        refY="5"
        markerWidth="7"
        markerHeight="7"
        orient="auto-start-reverse"
      >
        <path d="M 0 1 L 9 5 L 0 9 z" fill="currentColor" />
      </marker>
    </defs>

    <!-- Grille -->
    <g v-if="grid" class="grid">
      <line
        v-for="t in ticks"
        :key="`gx${t}`"
        :x1="sx(t)" :y1="sy(0)" :x2="sx(t)" :y2="sy(10)"
      />
      <line
        v-for="t in ticks"
        :key="`gy${t}`"
        :x1="sx(0)" :y1="sy(t)" :x2="sx(10)" :y2="sy(t)"
      />
    </g>

    <!-- Axes -->
    <g class="axes">
      <line :x1="sx(0)" :y1="sy(0)" :x2="sx(10) + 14" :y2="sy(0)" marker-end="url(#axis-arrow)" />
      <line :x1="sx(0)" :y1="sy(0)" :x2="sx(0)" :y2="sy(10) - 14" marker-end="url(#axis-arrow)" />
    </g>

    <text class="label" :x="sx(10) + 8" :y="sy(0) + 28">x</text>
    <text class="label" :x="sx(0) - 24" :y="sy(10) - 10">y</text>

    <!-- Nuage de points -->
    <g class="points">
      <circle
        v-for="p in points"
        :key="p.id"
        class="dot"
        :cx="sx(p.x)"
        :cy="sy(p.y)"
        r="5.5"
        :style="p.style"
      />
    </g>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  n: { type: Number, default: 40 },
  seed: { type: Number, default: 7 },
  amplitude: { type: Number, default: 4 },
  grid: { type: Boolean, default: true }
})

// ---------- Géométrie du repère ----------
const W = 760
const H = 540
const ORIGIN = { x: 90, y: 470 }
const UNIT = { x: 60, y: 42 } // pixels SVG par unité de donnée
const ticks = [2, 4, 6, 8, 10]

const sx = (x) => ORIGIN.x + x * UNIT.x
const sy = (y) => ORIGIN.y - y * UNIT.y

// ---------- Données ----------
// Générateur pseudo-aléatoire à graine (mulberry32) : le nuage reste identique
// à chaque rendu, ce qui évite qu'il change quand la slide se recharge.
function mulberry32(a) {
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v))

const points = computed(() => {
  const rand = mulberry32(props.seed)
  const gauss = () =>
    Math.sqrt(-2 * Math.log(1 - rand())) * Math.cos(2 * Math.PI * rand())

  return Array.from({ length: props.n }, (_, i) => {
    const x = 0.8 + rand() * 8.4
    // Tendance linéaire + bruit : de quoi faire une belle régression ensuite
    const y = clamp(0.7 * x + 1.5 + gauss() * 0.9, 0.4, 9.6)

    // Chaque point a son propre trajet, sa durée et son décalage de départ
    const a = props.amplitude * (0.5 + rand() * 0.5)
    const angle = rand() * Math.PI * 2
    return {
      id: i,
      x,
      y,
      style: {
        '--dx': `${(Math.cos(angle) * a).toFixed(2)}px`,
        '--dy': `${(Math.sin(angle) * a).toFixed(2)}px`,
        '--dur': `${(3.5 + rand() * 3).toFixed(2)}s`,
        '--delay': `${(-rand() * 6).toFixed(2)}s`
      }
    }
  })
})

defineExpose({ points, sx, sy })
</script>

<style scoped>
.plot {
  --point: #1d4ed8;
  width: 100%;
  height: 100%;
  color: currentColor;
  overflow: visible;
}

.grid line {
  stroke: currentColor;
  stroke-opacity: 0.1;
  stroke-width: 1;
}

.axes line {
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}

.label {
  fill: currentColor;
  font-family: KaTeX_Math, 'Times New Roman', serif;
  font-style: italic;
  font-size: 22px;
}

.dot {
  fill: var(--point);
  fill-opacity: 0.85;
  stroke: #ffffff;
  stroke-width: 1.5;
  animation: float var(--dur) ease-in-out var(--delay) infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(var(--dx), var(--dy));
  }
}

@media (prefers-reduced-motion: reduce) {
  .dot {
    animation: none;
  }
}
</style>