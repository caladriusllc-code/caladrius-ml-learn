<template>
  <section class="learning-demo" aria-label="Règle d’apprentissage du perceptron et descente de gradient">
    <svg
      class="diagram"
      viewBox="0 0 820 580"
      role="img"
      aria-label="Un perceptron à trois entrées reçoit des exemples, compare sa prédiction à la cible et corrige ses poids. En dessous, la fonction de coût diminue : c'est la descente de gradient."
    >
      <defs>
        <filter id="lr-glow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <marker id="lr-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
          <path d="M0 0 L6 3 L0 6" fill="none" stroke="white" />
        </marker>
      </defs>

      <!-- ============ Le perceptron ============ -->
      <g transform="translate(0 -66)">
        <!-- Connexions au repos : épaisseur = |poids|, pointillés si négatif -->
        <g class="wires">
          <path
            v-for="(p, i) in inputPaths"
            :key="'w' + i"
            :d="p.d"
            :stroke-width="wireWidth(shownW[i])"
            :stroke-dasharray="shownW[i] < 0 ? '6 6' : null"
          />
          <path d="M490 205 H585" stroke-width="1.35" marker-end="url(#lr-arrow)" />
          <path class="feedback" :d="FB_D" marker-end="url(#lr-arrow)" />
          <path d="M697 205 H666" class="compare" marker-end="url(#lr-arrow)" />
        </g>

        <!-- Projections : les connexions s'illuminent au passage des signaux -->
        <g class="overlays" filter="url(#lr-glow)">
          <path
            v-for="(o, i) in inputOverlay"
            :key="'ov' + i"
            :d="o.d"
            pathLength="1"
            stroke-dasharray="1 1"
            :stroke-dashoffset="1 - o.prog"
            :stroke-width="o.width"
            :opacity="o.op"
          />
          <path
            d="M490 205 H585"
            pathLength="1"
            stroke-dasharray="1 1"
            :stroke-dashoffset="1 - fwdProg"
            stroke-width="2.4"
            :opacity="fwdOp"
          />
          <path
            :d="FB_D"
            pathLength="1"
            stroke-dasharray="1 1"
            :stroke-dashoffset="1 - fbProg"
            stroke-width="2.4"
            :opacity="fbOp"
          />
        </g>

        <!-- Impulsions -->
        <g class="particles" filter="url(#lr-glow)">
          <circle
            v-for="(p, i) in pulses"
            :key="'pu' + i"
            :cx="p.x" :cy="p.y" :r="p.r"
            :opacity="p.o"
          />
        </g>

        <!-- Poids actuels sur les connexions -->
        <g v-for="(n, i) in inputs" :key="'wt' + i">
          <rect
            x="207" :y="n.y - 12" width="56" height="24" rx="12"
            class="pill"
            :stroke-opacity="0.3 + 0.7 * pillGlow"
            :filter="pillGlow > 0.1 ? 'url(#lr-glow)' : null"
          />
          <text x="235" :y="n.y + 5" class="weight">{{ fr(shownW[i], 2) }}</text>
        </g>

        <!-- Entrées : la valeur est lue dans le noyau -->
        <g v-for="(n, i) in inputs" :key="'in' + i">
          <circle
            class="input-ring"
            :cx="n.x" :cy="n.y" r="25"
            :stroke-dasharray="shownX[i] < 0 ? '3 4' : null"
          />
          <circle class="input-core" :cx="n.x" :cy="n.y" r="17" />
          <circle
            :cx="n.x" :cy="n.y" r="17"
            fill="#fff"
            :fill-opacity="clamp(Math.abs(shownX[i]) / 1.2) * 0.95"
          />
          <text
            class="node-text" :x="n.x" :y="n.y + 5"
            :style="{ fill: Math.abs(shownX[i]) > 0.6 ? '#050505' : '#fff' }"
          >{{ fr(shownX[i], 1) }}</text>
        </g>

        <!-- Neurone : somme | seuil -->
        <g class="neuron">
          <circle class="halo" cx="420" cy="205" r="83" />
          <circle
            class="core" cx="420" cy="205" r="67"
            :filter="bump > 0.2 ? 'url(#lr-glow)' : null"
          />
          <text class="sigma" x="400" y="218">Σ</text>
          <path class="divider" d="M432 155 V255" />
          <path class="activation" d="M448 228 H462 V181 H478" />
          <circle
            :cx="markerX" :cy="markerY" r="4.2"
            class="marker"
            :opacity="markerOp"
            filter="url(#lr-glow)"
          />
          <text class="zval" x="420" y="306" :opacity="markerOp">z = {{ fr(zShown, 2) }}</text>
        </g>

        <!-- Prédiction et cible -->
        <g>
          <circle class="result-ring" cx="625" cy="205" r="34" />
          <text class="result" x="625" y="213" :opacity="yhatOp">{{ step.yhat }}</text>
        </g>
        <g>
          <circle class="result-ring target" cx="735" cy="205" r="34" />
          <text class="result" x="735" y="213" :opacity="enterK">{{ step.y }}</text>
        </g>

        <!-- Erreur y − ŷ -->
        <text class="err" x="680" y="182" :opacity="errOp">{{ errText }}</text>

        <!-- Règle de mise à jour appliquée aux données -->
        <g class="update">
          <rect x="175" y="326" width="490" height="124" rx="15" />
          <text class="equation" x="420" y="355" :opacity="eqOp">wᵢ ← wᵢ + η (y − ŷ) xᵢ</text>
          <text
            v-for="(r, i) in rows"
            :key="'row' + i"
            class="row"
            x="420" :y="384 + i * 25"
            :opacity="r.op"
          >{{ r.text }}</text>
        </g>
      </g>

      <!-- ============ Fonction de coût et descente de gradient ============ -->
      <g class="cost">
        <line :x1="40" :y1="PY_BASE" :x2="780" :y2="PY_BASE" class="axis" />
        <line :x1="CX" :y1="PY_TOP" :x2="CX" :y2="PY_BASE" class="axis dashed" />
        <path :d="BOWL_D" class="bowl" />
        <text x="46" :y="PY_TOP + 12" class="sym">J</text>
        <text x="772" :y="PY_BASE + 20" class="sym">w</text>

        <!-- Positions déjà visitées par les poids -->
        <circle
          v-for="(p, i) in visited"
          :key="'vis' + i"
          :cx="p.x" :cy="p.y" r="4.5"
          class="visited"
        />

        <!-- Direction de la descente : opposée au gradient -->
        <path :d="gradPath" class="grad" marker-end="url(#lr-arrow)" :opacity="gradOp" />
        <text :x="gradLabel.x" :y="gradLabel.y" class="sym" :opacity="gradOp">−∇J</text>

        <!-- La balle qui dévale la courbe -->
        <circle
          v-for="(p, i) in trail"
          :key="'tr' + i"
          :cx="p.x" :cy="p.y" :r="p.r"
          class="ball"
          :opacity="p.o"
        />
        <circle :cx="ball.x" :cy="ball.y" r="8" class="ball" filter="url(#lr-glow)" />
        <text :x="ball.x + 16" :y="ball.y - 12" class="jval">J = {{ fr(jShown, 2) }}</text>
      </g>
    </svg>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* ---------- Données fictives ----------
   Chaque exemple : trois entrées x et la cible y (0 ou 1).
   Règle : si z = Σ wᵢxᵢ ≥ 0 alors ŷ = 1, sinon ŷ = 0.

   Coût (critère du perceptron) : J(w) = Σ max(0, −t·z), avec t = +1 si y = 1 et t = −1 si y = 0.
   Pour un exemple mal classé, −∇J = t·x : la règle η(y − ŷ)x est donc bien
   un pas de descente de gradient. Tout est calculé ici, rien n'est écrit en dur. */
const ETA = 0.3
const W0 = [0.2, 0.6, 0.4]
const SAMPLES = [
  { x: [1.0, 0.5, 1.0], y: 1 },
  { x: [0.5, 1.0, -0.5], y: 0 },
  { x: [-0.5, -1.0, 0.5], y: 1 },
  { x: [1.0, 1.5, 0.5], y: 0 },
]

// Durées (ms) : une étape qui corrige les poids est plus longue qu'une étape sans erreur
const DUR_UPDATE = 4600
const DUR_OK = 2800

const cost = (w) =>
  SAMPLES.reduce((acc, s) => {
    const z = s.x.reduce((a, v, i) => a + v * w[i], 0)
    return acc + Math.max(0, -(s.y ? 1 : -1) * z)
  }, 0)

function train() {
  const steps = []
  let w = [...W0]
  let start = 0
  for (let epoch = 0; epoch < 10; epoch++) {
    let errors = 0
    for (const s of SAMPLES) {
      const z = s.x.reduce((acc, v, i) => acc + v * w[i], 0)
      const yhat = z >= 0 ? 1 : 0
      const err = s.y - yhat
      const nw = w.map((wi, i) => Number((wi + ETA * err * s.x[i]).toFixed(2)))
      const dur = err !== 0 ? DUR_UPDATE : DUR_OK
      steps.push({
        epoch, x: s.x, y: s.y, z, yhat, err,
        w: [...w], nw, dur, start,
        J: cost(w), Jn: cost(nw),
      })
      start += dur
      if (err !== 0) errors++
      w = nw
    }
    if (errors === 0) break // l'époque est parfaite : l'apprentissage est terminé
  }
  return steps
}

const STEPS = train()
const TOTAL = STEPS.reduce((acc, s) => acc + s.dur, 0) + 1200 // courte pause avant la reprise

/* ---------- Géométrie du perceptron ---------- */
const inputs = [
  { x: 105, y: 115 },
  { x: 105, y: 205 },
  { x: 105, y: 295 },
]
const inputPts = inputs.map((n) => [[n.x + 25, n.y], [245, n.y], [300, 205], [353, 205]])
const inputPaths = inputPts.map((pts) => ({
  d: `M ${pts[0][0]} ${pts[0][1]} C ${pts[1][0]} ${pts[1][1]}, ${pts[2][0]} ${pts[2][1]}, ${pts[3][0]} ${pts[3][1]}`,
}))

const FB_D = 'M735 242 C735 345 560 370 420 370 C290 370 245 345 245 285'
const FB = [
  [[735, 242], [735, 345], [560, 370], [420, 370]],
  [[420, 370], [290, 370], [245, 345], [245, 285]],
]

/* ---------- Géométrie de la courbe de coût ---------- */
const CX = 410
const XH = 330 // demi-largeur de la cuvette
const PY_TOP = 418
const PY_BASE = 548
const H = PY_BASE - PY_TOP
// Parabole exacte : courbe de Bézier quadratique dont le sommet touche la ligne de base
const BOWL_D = `M ${CX - XH} ${PY_TOP} Q ${CX} ${PY_BASE + H} ${CX + XH} ${PY_TOP}`
const J_MAX = STEPS[0].J * 1.08

const clamp = (v) => Math.min(1, Math.max(0, v))
const ease = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2)
const lerp = (a, b, k) => a + (b - a) * k

// Position sur la cuvette (versant gauche) d'un coût J : la hauteur est le coût réel
function onBowl(J) {
  const h = clamp(J / J_MAX)
  return { x: CX - XH * Math.sqrt(h), y: PY_BASE - H * h }
}

function bez(pts, u) {
  const m = 1 - u
  const [p0, p1, p2, p3] = pts
  return [
    m * m * m * p0[0] + 3 * m * m * u * p1[0] + 3 * m * u * u * p2[0] + u * u * u * p3[0],
    m * m * m * p0[1] + 3 * m * m * u * p1[1] + 3 * m * u * u * p2[1] + u * u * u * p3[1],
  ]
}
const fbPoint = (u) => (u < 0.5 ? bez(FB[0], u * 2) : bez(FB[1], (u - 0.5) * 2))

// Nombres à la française : virgule décimale, vrai signe moins
const fr = (n, d) => {
  const v = Math.abs(n) < 0.5 * Math.pow(10, -d) ? 0 : n
  const s = Math.abs(v).toFixed(d).replace('.', ',')
  return v < 0 ? '\u2212' + s : s
}
const wireWidth = (w) => 1 + Math.abs(w) * 2.2

/* ---------- Horloge ---------- */
const stepIdx = ref(0)
const t = ref(0) // temps écoulé dans l'étape courante
let raf = 0
let t0 = 0

function locate(tau) {
  // pendant la pause finale, on reste à la fin de la dernière étape
  for (let k = STEPS.length - 1; k >= 0; k--) {
    if (tau >= STEPS[k].start) {
      stepIdx.value = k
      t.value = Math.min(tau - STEPS[k].start, STEPS[k].dur)
      return
    }
  }
}

function frame(ts) {
  if (!t0) t0 = ts
  locate((ts - t0) % TOTAL)
  raf = requestAnimationFrame(frame)
}

onMounted(() => {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    // Image fixe : première étape où les poids sont corrigés, flèche de gradient visible
    const k = STEPS.findIndex((s) => s.err !== 0)
    stepIdx.value = k === -1 ? 0 : k
    t.value = 3400
  } else {
    raf = requestAnimationFrame(frame)
  }
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

/* ---------- États dérivés ---------- */
const step = computed(() => STEPS[stepIdx.value])
const prev = computed(() => STEPS[(stepIdx.value - 1 + STEPS.length) % STEPS.length])
const hasErr = computed(() => step.value.err !== 0)

const endFade = computed(() => 1 - clamp((t.value - (step.value.dur - 350)) / 350))
const enterK = computed(() => ease(clamp(t.value / 350)))
// Avancement de la correction des poids (et donc de la descente sur la courbe)
const moveK = computed(() => ease(clamp((t.value - 3500) / 600)))

const shownX = computed(() => step.value.x.map((x, i) => lerp(prev.value.x[i], x, enterK.value)))

// Poids affichés : retour fluide au début, puis correction pendant la mise à jour
const shownW = computed(() =>
  step.value.w.map((w, i) => {
    if (t.value < 350) return lerp(prev.value.nw[i], w, enterK.value)
    if (!hasErr.value) return w
    return lerp(w, step.value.nw[i], moveK.value)
  })
)

// Contribution xᵢ·wᵢ de chaque entrée (avec les poids avant correction)
const contribs = computed(() => step.value.x.map((x, i) => x * step.value.w[i]))

// La somme se construit à mesure que les impulsions arrivent
const zShown = computed(
  () =>
    contribs.value.reduce((acc, c, i) => acc + c * ease(clamp((t.value - (1000 + i * 100)) / 300)), 0) *
    endFade.value
)
const markerX = computed(() => 462 + clamp((zShown.value + 1.5) / 3) * 24 - 12)
const markerY = computed(() => (zShown.value >= 0 ? 181 : 228))
const markerOp = computed(() => clamp((t.value - 1000) / 200) * endFade.value)

const bump = computed(() => clamp((t.value - 1100) / 300) * (1 - clamp((t.value - 2100) / 500)))

const yhatOp = computed(() => clamp((t.value - 1950) / 200) * endFade.value)
const errOp = computed(() => clamp((t.value - 2300) / 200) * endFade.value)
const errText = computed(() => {
  const e = step.value.err
  return e > 0 ? '+1' : e < 0 ? '\u22121' : '0'
})

const pillGlow = computed(() =>
  hasErr.value ? clamp((t.value - 3400) / 200) * (1 - clamp((t.value - 4100) / 400)) : 0
)

/* ---------- Connexions et impulsions ---------- */
const overlayFade = computed(() => 1 - clamp((t.value - (hasErr.value ? 3300 : 2300)) / 600))

const inputOverlay = computed(() =>
  inputPaths.map((p, i) => ({
    d: p.d,
    prog: ease(clamp((t.value - 400 - i * 100) / 900)),
    width: wireWidth(shownW.value[i]) + 0.8,
    op: Math.abs(contribs.value[i]) < 0.005 ? 0 : overlayFade.value,
  }))
)

const fwdProg = computed(() => ease(clamp((t.value - 1500) / 500)))
const fwdOp = computed(() => 1 - clamp((t.value - 2500) / 500))
const fbProg = computed(() => (hasErr.value ? ease(clamp((t.value - 2700) / 1000)) : 0))
const fbOp = computed(() => (hasErr.value ? 1 - clamp((t.value - 3700) / 500) : 0))

const pulses = computed(() => {
  const out = []
  // Entrées → neurone : la taille suit |xᵢ·wᵢ|
  contribs.value.forEach((c, i) => {
    if (Math.abs(c) < 0.005) return
    const u0 = (t.value - 400 - i * 100) / 900
    if (u0 <= 0 || u0 >= 1) return
    const rBase = 2.6 + 3 * clamp(Math.abs(c) / 0.8)
    for (let k = 0; k < 5; k++) {
      const [x, y] = bez(inputPts[i], ease(clamp(u0 - k * 0.04)))
      out.push({ x, y, r: Math.max(rBase - k * 0.7, 0.8), o: 1 - k * 0.2 })
    }
  })
  // Neurone → prédiction
  const uf = (t.value - 1500) / 500
  if (uf > 0 && uf < 1) {
    for (let k = 0; k < 5; k++) {
      const v = ease(clamp(uf - k * 0.05))
      out.push({ x: 490 + 95 * v, y: 205, r: 4.2 - k * 0.7, o: 1 - k * 0.2 })
    }
  }
  // Retour de l'erreur vers les poids
  if (hasErr.value) {
    const ub = (t.value - 2700) / 1000
    if (ub > 0 && ub < 1) {
      for (let k = 0; k < 5; k++) {
        const [x, y] = fbPoint(ease(clamp(ub - k * 0.04)))
        out.push({ x, y, r: Math.max(3.8 - k * 0.65, 0.8), o: 1 - k * 0.2 })
      }
    }
  }
  return out
})

/* ---------- Règle de mise à jour appliquée ligne par ligne ---------- */
const eqOp = computed(
  () => 0.45 + 0.55 * (hasErr.value ? clamp((t.value - 2700) / 300) * endFade.value : 0)
)

const SUB = '\u2081\u2082\u2083'
const rows = computed(() => {
  const s = step.value
  const sign = s.err > 0 ? '(+1)' : s.err < 0 ? '(\u22121)' : '(0)'
  return s.x.map((x, i) => ({
    text: `w${SUB[i]} \u2190 ${fr(s.w[i], 2)} + ${fr(ETA, 1)} \u00d7 ${sign} \u00d7 ${fr(x, 1)} = ${fr(s.nw[i], 2)}`,
    op: hasErr.value ? clamp((t.value - 2900 - i * 120) / 250) * endFade.value : 0,
  }))
})

/* ---------- Descente de gradient sur la courbe de coût ---------- */
// Coût affiché : même mouvement que les poids, donc la balle suit exactement les corrections
const jShown = computed(() => {
  const s = step.value
  if (t.value < 350) return lerp(prev.value.Jn, s.J, enterK.value)
  if (!hasErr.value) return s.J
  return lerp(s.J, s.Jn, moveK.value)
})
const ball = computed(() => onBowl(jShown.value))

// Traînée lumineuse pendant la descente
const trail = computed(() => {
  if (!hasErr.value || t.value < 3500 || t.value > 4100) return []
  const s = step.value
  const u = (t.value - 3500) / 600
  return Array.from({ length: 5 }, (_, k) => {
    const p = onBowl(lerp(s.J, s.Jn, ease(clamp(u - (k + 1) * 0.07))))
    return { x: p.x, y: p.y, r: 7 - k * 1.1, o: 0.5 - k * 0.09 }
  })
})

// Points déjà atteints par les poids depuis le début de l'entraînement
const visited = computed(() => {
  const pts = [onBowl(STEPS[0].J)]
  STEPS.forEach((s, k) => {
    if (s.err === 0) return
    const done = k < stepIdx.value || (k === stepIdx.value && t.value > 4100)
    if (done) pts.push(onBowl(s.Jn))
  })
  return pts
})

// Flèche tangente : le pas de descente, dans le sens opposé au gradient
const gradOp = computed(() =>
  hasErr.value ? clamp((t.value - 2800) / 250) * (1 - clamp((t.value - 3500) / 250)) : 0
)
const gradDir = computed(() => {
  const p = onBowl(step.value.J)
  const slope = (-2 * H * (p.x - CX)) / (XH * XH) // dy/dx de la parabole à l'écran
  const n = Math.hypot(1, slope)
  return { p, dx: 1 / n, dy: slope / n }
})
const gradPath = computed(() => {
  const { p, dx, dy } = gradDir.value
  return `M ${(p.x + dx * 14).toFixed(1)} ${(p.y + dy * 14).toFixed(1)} L ${(p.x + dx * 72).toFixed(1)} ${(p.y + dy * 72).toFixed(1)}`
})
const gradLabel = computed(() => {
  const { p, dx, dy } = gradDir.value
  // décalage perpendiculaire, vers le haut
  return { x: p.x + dx * 46 + dy * 22, y: p.y + dy * 46 - dx * 22 }
})
</script>

<style scoped>
.learning-demo {
  --white: #fff;
  --muted: rgba(255, 255, 255, 0.58);
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  padding: clamp(16px, 3vw, 30px);
  overflow: hidden;
  color: #fff;
  background: #050505;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.diagram {
  display: block;
  width: 100%;
  height: auto;
  overflow: visible;
}

.diagram text {
  text-anchor: middle;
}

/* Connexions */
.wires path {
  fill: none;
  stroke: rgba(255, 255, 255, 0.34);
  stroke-linecap: round;
}
.wires .feedback {
  stroke-width: 1.35;
  stroke-dasharray: 5 7;
  opacity: 0.85;
}
.wires .compare {
  stroke: #fff;
  stroke-width: 1.2;
  stroke-dasharray: 3 4;
}
.overlays path {
  fill: none;
  stroke: #fff;
  stroke-linecap: round;
}
.particles circle {
  fill: #fff;
}

/* Poids */
.pill {
  fill: #050505;
  stroke: #fff;
  stroke-width: 1.1;
}
.weight {
  fill: rgba(255, 255, 255, 0.9);
  font: italic 15px Georgia, serif;
  text-anchor: middle;
}

/* Entrées */
.input-ring,
.result-ring {
  fill: none;
  stroke: rgba(255, 255, 255, 0.78);
  stroke-width: 1.4;
}
.input-core,
.core {
  fill: #050505;
  stroke: #fff;
  stroke-width: 1.6;
}
.node-text,
.result {
  fill: #fff;
  font-family: Georgia, serif;
  font-style: italic;
}
.node-text {
  font-size: 14px;
}
.result {
  font-size: 23px;
}
.target {
  stroke-dasharray: 3 4;
}

/* Neurone */
.halo {
  fill: none;
  stroke: rgba(255, 255, 255, 0.3);
  stroke-width: 1;
  animation: halo 2.8s ease-in-out infinite;
  transform-box: fill-box;
  transform-origin: center;
}
.core {
  stroke-width: 1.8;
}
.sigma {
  fill: #fff;
  font: 42px Georgia, serif;
}
.divider,
.activation {
  fill: none;
  stroke: #fff;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.marker {
  fill: #fff;
}
.zval {
  fill: #fff;
  font: italic 18px Georgia, serif;
}

/* Erreur */
.err {
  fill: #fff;
  font: 17px Georgia, serif;
}

/* Mise à jour des poids */
.update rect {
  fill: #080808;
  stroke: rgba(255, 255, 255, 0.8);
  stroke-width: 1.2;
  animation: glowBorder 3s ease-in-out infinite;
}
.equation {
  fill: #fff;
  font: italic 20px Georgia, 'Times New Roman', serif;
}
.row {
  fill: #fff;
  font: italic 16px Georgia, 'Times New Roman', serif;
}

/* Courbe de coût */
.cost .axis {
  stroke: rgba(255, 255, 255, 0.3);
  stroke-width: 1.2;
}
.cost .axis.dashed {
  stroke-dasharray: 3 5;
  stroke: rgba(255, 255, 255, 0.2);
}
.bowl {
  fill: none;
  stroke: #fff;
  stroke-width: 2.2;
  stroke-linecap: round;
}
.visited {
  fill: #050505;
  stroke: rgba(255, 255, 255, 0.75);
  stroke-width: 1.4;
}
.grad {
  fill: none;
  stroke: #fff;
  stroke-width: 2;
  stroke-linecap: round;
}
.ball {
  fill: #fff;
}
.sym {
  fill: rgba(255, 255, 255, 0.8);
  font: italic 18px Georgia, 'Times New Roman', serif;
}
.diagram .jval {
  fill: #fff;
  font: italic 16px Georgia, 'Times New Roman', serif;
  text-anchor: start;
}

@keyframes halo {
  0%, 100% { opacity: 0.3; transform: scale(0.96); }
  50% { opacity: 1; transform: scale(1.06); }
}
@keyframes glowBorder {
  0%, 100% { stroke-opacity: 0.5; }
  50% { stroke-opacity: 1; }
}

@media (max-width: 560px) {
  .learning-demo { padding: 13px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; }
}
</style>