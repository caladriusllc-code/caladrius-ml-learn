<template>
  <div class="main-content">
    <div class="stage">
      <!-- Colonne gauche : les modèles simples échouent -->
      <section class="col">
        <h3>
          Dans la vie, les données ne sont pas modélisables par une droite, une courbe, un cercle;
        </h3>

        <div class="panels">
          <figure>
            <svg viewBox="0 0 120 120" role="img" aria-label="Une droite ne sépare pas les deux classes de points">
              <circle v-for="(p, i) in classA" :key="'a' + i" :cx="p.x" :cy="p.y" r="2.6" class="dot-a" />
              <circle v-for="(p, i) in classB" :key="'b' + i" :cx="p.x" :cy="p.y" r="2.6" class="dot-b" />
              <line x1="8" y1="112" x2="112" y2="8" class="fail" />
            </svg>
            <figcaption>Droite</figcaption>
          </figure>

          <figure>
            <svg viewBox="0 0 120 120" role="img" aria-label="Une courbe ne sépare pas les deux classes de points">
              <circle v-for="(p, i) in classA" :key="'a' + i" :cx="p.x" :cy="p.y" r="2.6" class="dot-a" />
              <circle v-for="(p, i) in classB" :key="'b' + i" :cx="p.x" :cy="p.y" r="2.6" class="dot-b" />
              <path d="M8 104 Q60 -8 112 104" class="fail" />
            </svg>
            <figcaption>Courbe</figcaption>
          </figure>

          <figure>
            <svg viewBox="0 0 120 120" role="img" aria-label="Un cercle ne sépare pas les deux classes de points">
              <circle v-for="(p, i) in classA" :key="'a' + i" :cx="p.x" :cy="p.y" r="2.6" class="dot-a" />
              <circle v-for="(p, i) in classB" :key="'b' + i" :cx="p.x" :cy="p.y" r="2.6" class="dot-b" />
              <circle cx="60" cy="60" r="34" class="fail" />
            </svg>
            <figcaption>Cercle</figcaption>
          </figure>
        </div>
      </section>

      <!-- Flèche de transition -->
      <svg class="arrow" viewBox="0 0 40 80" aria-hidden="true">
        <path d="M8 10 L30 40 L8 70" />
      </svg>

      <!-- Colonne droite : le réseau de neurones -->
      <section class="col" v-click>
        <h3>
          La complexité des données nous pousse à adopter des architectures plus complexes;
        </h3>

        <svg class="network" viewBox="0 0 265 150" role="img" aria-label="Schéma d'un réseau de neurones à plusieurs couches">
          <line
            v-for="(e, i) in edges"
            :key="'e' + i"
            :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
            class="edge"
          />
          <circle
            v-for="(n, i) in nodes"
            :key="'n' + i"
            :cx="n.x" :cy="n.y" r="7"
            :class="['neuron', n.kind]"
          />
        </svg>
      </section>
    </div>

    <p class="conclusion" v-click>On passe donc au deepLearning</p>
  </div>
</template>

<script setup>
// Pseudo-aléatoire déterministe : le rendu est identique à chaque affichage de la slide
const rnd = (s) => {
  const x = Math.sin(s * 127.1) * 43758.5453
  return x - Math.floor(x)
}

// Deux spirales imbriquées : un jeu de données qu'aucune forme simple ne sépare
const spiral = (offset, seed) =>
  Array.from({ length: 34 }, (_, i) => {
    const t = i / 33
    const r = 8 + t * 46
    const a = t * 5.2 + offset
    return {
      x: +(60 + r * Math.cos(a) + (rnd(i + seed) - 0.5) * 7).toFixed(1),
      y: +(60 + r * Math.sin(a) + (rnd(i + seed + 50) - 0.5) * 7).toFixed(1),
    }
  })

const classA = spiral(0, 1)
const classB = spiral(Math.PI, 200)

// Réseau de neurones : entrée, deux couches cachées, sortie
const layers = [3, 5, 5, 2]
const xs = [28, 98, 168, 238]

const nodes = layers.flatMap((count, l) =>
  Array.from({ length: count }, (_, i) => ({
    x: xs[l],
    y: 75 + (i - (count - 1) / 2) * 26,
    layer: l,
    kind: l === 0 ? 'input' : l === layers.length - 1 ? 'output' : 'hidden',
  }))
)

const edges = nodes.flatMap((a) =>
  nodes
    .filter((b) => b.layer === a.layer + 1)
    .map((b) => ({ x1: a.x, y1: a.y, x2: b.x, y2: b.y }))
)
</script>

<style scoped>
.main-content {
  --class-a: #3b82c4;
  --class-b: #e8a33d;
  --fail: #d6456b;
  --net: #1fa38a;

  width: 100%;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  gap: 1.6rem;
}

.stage {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: start;
  gap: 1rem;
}

.col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

h3 {
  margin: 0;
  text-align: center;
  font-size: 1.05rem;
  line-height: 1.4;
  max-width: 24em;
}

/* Les trois modèles simples */
.panels {
  display: flex;
  gap: 0.75rem;
  width: 100%;
  justify-content: center;
}

figure {
  margin: 0;
  flex: 1;
  max-width: 9rem;
  text-align: center;
}

figure svg {
  width: 100%;
  height: auto;
  border: 1px solid color-mix(in srgb, currentColor 25%, transparent);
  border-radius: 6px;
}

figcaption {
  margin-top: 0.3rem;
  font-size: 0.8rem;
  opacity: 0.75;
}

.dot-a { fill: var(--class-a); }
.dot-b { fill: var(--class-b); }

.fail {
  fill: none;
  stroke: var(--fail);
  stroke-width: 2.4;
  stroke-dasharray: 5 4;
  stroke-linecap: round;
}

/* Flèche */
.arrow {
  width: 2rem;
  align-self: center;
}

.arrow path {
  fill: none;
  stroke: currentColor;
  stroke-width: 5;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.5;
}

/* Réseau de neurones */
.network {
  width: 100%;
  max-width: 24rem;
  height: auto;
}

.edge {
  stroke: currentColor;
  stroke-width: 0.7;
  opacity: 0.2;
}

.neuron {
  stroke-width: 2;
}

.neuron.input {
  fill: var(--class-a);
  stroke: var(--class-a);
}

.neuron.hidden {
  fill: transparent;
  stroke: var(--net);
}

.neuron.output {
  fill: var(--class-b);
  stroke: var(--class-b);
}

.conclusion {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--net);
}
</style>