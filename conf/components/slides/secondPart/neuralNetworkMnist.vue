<template>
  <section class="mlp-static" aria-label="Réseau de neurones 784, 16, 16, 10">
    <svg
      class="diagram"
      viewBox="0 0 880 520"
      role="img"
      aria-label="Réseau de neurones entièrement connecté : 784 entrées, deux couches cachées de 16 neurones, 10 sorties correspondant aux chiffres de 0 à 9."
    >
      <!-- ============ En-têtes de couches ============ -->
      <g v-for="(L, l) in LAYERS" :key="'hd' + l">
        <text class="hd" :x="L.x" y="30">{{ L.name }}</text>
        <text class="hd-sub" :x="L.x" y="50">{{ L.sub }}</text>
      </g>

      <!-- ============ Connexions ============ -->
      <g class="wires">
        <line
          v-for="(w, k) in WIRES"
          :key="'w' + k"
          :x1="w.x1" :y1="w.y1" :x2="w.x2" :y2="w.y2"
          :stroke-opacity="w.o"
        />
      </g>

      <!-- ============ Neurones ============ -->
      <g v-for="n in NODES" :key="'n' + n.l + '-' + n.k">
        <circle class="core" :cx="n.x" :cy="n.y" :r="n.r" />
      </g>

      <!-- Points de suspension de la couche d'entrée -->
      <g class="dots">
        <circle v-for="d in 3" :key="'d' + d" :cx="XS[0]" :cy="DOTS_Y + (d - 2) * 9" r="2.2" />
      </g>

      <!-- Étiquettes des entrées -->
      <text
        v-for="n in LAYER_NODES[0]"
        :key="'xl' + n.k"
        class="sym end"
        :x="n.x - 20"
        :y="n.y + 5"
      >x{{ sub(n.idx) }}</text>

      <!-- Étiquettes des sorties : chiffres 0 à 9 -->
      <text
        v-for="n in LAYER_NODES[3]"
        :key="'yl' + n.k"
        class="digit"
        :x="n.x + 26"
        :y="n.y + 6"
      >{{ n.k }}</text>

      <!-- Nombre de neurones par couche -->
      <text
        v-for="(L, l) in LAYERS"
        :key="'ct' + l"
        class="count"
        :x="L.x"
        y="505"
      >{{ L.count }}</text>
    </svg>
  </section>
</template>

<script setup>
/* ---------- Architecture 784 → 16 → 16 → 10 ---------- */
const XS = [120, 340, 560, 750]
const CENTER_Y = 268
const R = [9, 10, 10, 13]               // rayon des neurones par couche

const SUBS = '₀₁₂₃₄₅₆₇₈₉'
const sub = (n) => String(n).replace(/\d/g, (d) => SUBS[d])

const LAYERS = [
  { x: XS[0], name: 'Entrée',   sub: 'x ∈ ℝ⁷⁸⁴', count: '784 neurones' },
  { x: XS[1], name: 'Cachée 1', sub: 'h¹ ∈ ℝ¹⁶', count: '16 neurones' },
  { x: XS[2], name: 'Cachée 2', sub: 'h² ∈ ℝ¹⁶', count: '16 neurones' },
  { x: XS[3], name: 'Sortie',   sub: 'ŷ ∈ ℝ¹⁰',  count: '10 neurones' },
]

/* Entrée : 7 neurones en haut, « ⋮ », 7 neurones en bas (indices 1..7 et 778..784) */
const INPUT_IDX = [1, 2, 3, 4, 5, 6, 7, null, 778, 779, 780, 781, 782, 783, 784]
const SLOT_IN = 25                       // pas vertical de la couche d'entrée
const SLOT_H = 24                        // pas vertical des couches cachées
const SLOT_OUT = 36                      // pas vertical de la sortie

const spread = (count, step, center) =>
  Array.from({ length: count }, (_, k) => center + (k - (count - 1) / 2) * step)

const inputYs = spread(INPUT_IDX.length, SLOT_IN, CENTER_Y)
const DOTS_Y = inputYs[INPUT_IDX.indexOf(null)]

const LAYER_NODES = [
  INPUT_IDX
    .map((idx, k) => ({ idx, k, y: inputYs[k] }))
    .filter((n) => n.idx !== null)
    .map((n) => ({ l: 0, k: n.k, idx: n.idx, x: XS[0], y: n.y, r: R[0] })),
  spread(16, SLOT_H, CENTER_Y).map((y, k) => ({ l: 1, k, x: XS[1], y, r: R[1] })),
  spread(16, SLOT_H, CENTER_Y).map((y, k) => ({ l: 2, k, x: XS[2], y, r: R[2] })),
  spread(10, SLOT_OUT, CENTER_Y).map((y, k) => ({ l: 3, k, x: XS[3], y, r: R[3] })),
]
const NODES = LAYER_NODES.flat()

/* ---------- Connexions (opacité légèrement variable, générateur à graine) ---------- */
function rng(seed) {
  return () => {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
const rand = rng(11)

const WIRES = []
for (let l = 0; l < 3; l++) {
  for (const a of LAYER_NODES[l]) {
    for (const b of LAYER_NODES[l + 1]) {
      WIRES.push({
        x1: a.x + a.r, y1: a.y,
        x2: b.x - b.r, y2: b.y,
        o: Number((0.05 + rand() * 0.2).toFixed(2)),
      })
    }
  }
}
</script>

<style scoped>
.mlp-static {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  padding: 1rem;
  color: #fff;
  background: #050505;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 18px;
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
.hd {
  fill: #fff;
  font: italic 17px Georgia, 'Times New Roman', serif;
}
.hd-sub {
  fill: rgba(255, 255, 255, 0.58);
  font: italic 14px Georgia, 'Times New Roman', serif;
}
.count {
  fill: rgba(255, 255, 255, 0.45);
  font: 12px ui-monospace, monospace;
  letter-spacing: 1px;
}

/* Connexions */
.wires line {
  stroke: #fff;
  stroke-width: 0.7;
}

/* Neurones */
.core {
  fill: #050505;
  stroke: #fff;
  stroke-width: 1.5;
}
.dots circle {
  fill: rgba(255, 255, 255, 0.8);
}

/* Étiquettes */
.sym {
  fill: rgba(255, 255, 255, 0.8);
  font: italic 15px Georgia, 'Times New Roman', serif;
}
.diagram .sym.end {
  text-anchor: end;
}
.diagram .digit {
  text-anchor: start;
  fill: #fff;
  font: italic 20px Georgia, 'Times New Roman', serif;
}
</style>