<template>
  <section class="network" aria-label="Réseau de neurones à deux entrées, trois neurones cachés et trois sorties">
    <div class="network__heading">
      <span class="eyebrow">RÉSEAU NEURONAL</span>
      <span class="architecture">2 — 3 — 3</span>
    </div>

    <svg class="network__diagram" viewBox="0 0 760 430" role="img"
      aria-label="Deux entrées reliées à trois neurones cachés, puis à trois sorties">
      <defs>
        <filter id="whiteGlow" x="-150%" y="-150%" width="400%" height="400%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <!-- Connexions entre les entrées et la couche cachée -->
      <g class="connections">
        <path v-for="edge in firstEdges" :key="edge.id" :id="edge.id" :d="edge.d" />
      </g>
      <!-- Connexions entre la couche cachée et les sorties -->
      <g class="connections">
        <path v-for="edge in secondEdges" :key="edge.id" :id="edge.id" :d="edge.d" />
      </g>

      <!-- Impulsions lumineuses qui parcourent les connexions -->
      <g class="signals" filter="url(#whiteGlow)">
        <g v-for="edge in firstEdges" :key="'signal-' + edge.id">
          <circle r="4"><animateMotion :dur="edge.duration" repeatCount="indefinite" :begin="edge.delay"><mpath :href="'#' + edge.id" /></animateMotion></circle>
        </g>
        <g v-for="edge in secondEdges" :key="'signal-' + edge.id">
          <circle r="4"><animateMotion :dur="edge.duration" repeatCount="indefinite" :begin="edge.delay"><mpath :href="'#' + edge.id" /></animateMotion></circle>
        </g>
      </g>

      <!-- Colonnes et repères -->
      <g class="layer-labels">
        <text x="105" y="48">ENTRÉES</text>
        <text x="380" y="48">COUCHE CACHÉE</text>
        <text x="655" y="48">SORTIES</text>
      </g>

      <!-- Nœuds d'entrée -->
      <g v-for="(node, i) in inputNodes" :key="node.id" class="neuron input-neuron">
        <circle class="node-halo" :cx="node.x" :cy="node.y" r="25" />
        <circle class="node-core" :cx="node.x" :cy="node.y" r="17" />
        <text class="node-label" :x="node.x" :y="node.y + 5">{{ `x${i + 1}` }}</text>
      </g>

      <!-- Couche cachée -->
      <g v-for="(node, i) in hiddenNodes" :key="node.id" class="neuron hidden-neuron">
        <circle class="node-halo breathe" :cx="node.x" :cy="node.y" r="29" :style="{ animationDelay: `${i * 260}ms` }" />
        <circle class="node-core" :cx="node.x" :cy="node.y" r="20" />
        <circle class="node-center" :cx="node.x" :cy="node.y" r="3" />
      </g>

      <!-- Nœuds de sortie -->
      <g v-for="(node, i) in outputNodes" :key="node.id" class="neuron output-neuron">
        <circle class="node-halo breathe" :cx="node.x" :cy="node.y" r="27" :style="{ animationDelay: `${i * 340}ms` }" />
        <circle class="node-core" :cx="node.x" :cy="node.y" r="18" />
        <text class="node-label" :x="node.x" :y="node.y + 5">{{ `y${i + 1}` }}</text>
      </g>
    </svg>

    <div class="network__footer">
      <span>PROPAGATION DES SIGNAUX</span>
      <span class="legend"><i></i> ACTIVITÉ NEURONALE</span>
    </div>
  </section>
</template>

<script setup>
const inputNodes = [
  { id: 'x1', x: 105, y: 165 },
  { id: 'x2', x: 105, y: 285 },
]
const hiddenNodes = [
  { id: 'h1', x: 380, y: 125 },
  { id: 'h2', x: 380, y: 225 },
  { id: 'h3', x: 380, y: 325 },
]
const outputNodes = [
  { id: 'y1', x: 655, y: 125 },
  { id: 'y2', x: 655, y: 225 },
  { id: 'y3', x: 655, y: 325 },
]

const makeEdges = (from, to, prefix, offset = 0) => {
  const edges = []
  from.forEach((a, i) => to.forEach((b, j) => {
    const id = `${prefix}-${i}-${j}`
    const dx = (b.x - a.x) * 0.48
    edges.push({
      id,
      d: `M ${a.x} ${a.y} C ${a.x + dx} ${a.y}, ${b.x - dx} ${b.y}, ${b.x} ${b.y}`,
      delay: `${(offset + (i * to.length + j) * 0.19).toFixed(2)}s`,
      duration: `${(1.7 + ((i + j) % 3) * 0.25).toFixed(2)}s`,
    })
  }))
  return edges
}
const firstEdges = makeEdges(inputNodes, hiddenNodes, 'input', 0)
const secondEdges = makeEdges(hiddenNodes, outputNodes, 'output', 0.8)
</script>

<style scoped>
.network {
  --white: #fff;
  --black: #050505;
  box-sizing: border-box;
  width: 100%;
  overflow: hidden;
  padding: clamp(18px, 3vw, 34px);
  color: var(--white);
  background: var(--black);
  border: 1px solid rgba(255,255,255,.16);
  border-radius: 18px;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.network__heading, .network__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.eyebrow, .network__footer, .layer-labels {
  font-size: 10px;
  font-weight: 650;
  letter-spacing: .2em;
}
.eyebrow, .network__footer { color: rgba(255,255,255,.62); }
.architecture {
  font-size: 12px;
  letter-spacing: .24em;
  color: #fff;
}
.network__diagram { display: block; width: 100%; height: auto; margin: 8px 0 2px; }
.connections path {
  fill: none;
  stroke: rgba(255,255,255,.34);
  stroke-width: 1.25;
  vector-effect: non-scaling-stroke;
}
.signals circle { fill: #fff; opacity: .95; }
.layer-labels text {
  fill: rgba(255,255,255,.58);
  text-anchor: middle;
}
.node-halo {
  fill: none;
  stroke: rgba(255,255,255,.22);
  stroke-width: 1;
}
.node-core {
  fill: #050505;
  stroke: #fff;
  stroke-width: 1.6;
  vector-effect: non-scaling-stroke;
}
.node-center { fill: #fff; }
.node-label {
  fill: #fff;
  font-size: 12px;
  font-weight: 500;
  text-anchor: middle;
}
.breathe { transform-box: fill-box; transform-origin: center; animation: breathe 2.8s ease-in-out infinite; }
.network__footer {
  padding-top: 15px;
  border-top: 1px solid rgba(255,255,255,.16);
  font-size: 9px;
}
.legend { display: inline-flex; align-items: center; gap: 8px; }
.legend i { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #fff; box-shadow: 0 0 9px #fff; }
@keyframes breathe {
  0%, 100% { opacity: .35; transform: scale(.92); }
  50% { opacity: .9; transform: scale(1.12); }
}
@media (prefers-reduced-motion: reduce) {
  .breathe { animation: none; }
}
</style>
