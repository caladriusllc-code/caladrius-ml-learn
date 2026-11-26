<template>
  <section ref="containerRef" class="merci" :aria-label="message">
    <!-- Banc de milliers de micro-carreaux en arrière-plan -->
    <canvas ref="canvasRef" class="shoal-canvas" aria-hidden="true" />

    <!-- Halo doux au centre pour garantir le contraste du texte -->
    <div class="readability-veil" aria-hidden="true" />

    <div class="stage" :class="{ fading }">
      <!-- En-tête signature IA -->
      <div class="ai-badge" :class="phase" aria-hidden="true">
        <svg class="sparkle" viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" />
        </svg>
        <span class="status-text">
          {{ phase === 'thinking' ? thinkingLabel : statusLabel }}
        </span>
      </div>

      <!-- Flux de réponse -->
      <p class="reply" aria-hidden="true">
        <span v-for="(tok, i) in visible" :key="`${cycle}-${i}`" class="tok">{{ tok }}</span><span
          v-if="phase !== 'thinking'"
          class="cursor"
          :class="{ idle: phase === 'idle' }"
        />
      </p>
    </div>

    <!-- Barre de saisie flottante -->
    <div class="prompt" :class="{ on: ready }" aria-hidden="true">
      <div class="prompt-left">
        <span class="prompt-dot" />
        <span class="placeholder">{{ placeholder }}</span>
      </div>
      <span class="send" :class="{ pulse: phase === 'idle' }">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 19V5" />
          <path d="M5 12l7-7 7 7" />
        </svg>
      </span>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  message: { type: String, default: 'Merci de votre attention.' },
  placeholder: { type: String, default: 'Posez votre question…' },
  thinkingLabel: { type: String, default: 'Synthèse en cours…' },
  statusLabel: { type: String, default: 'Réponse générée' },
  /** Délai moyen entre deux tokens (ms) */
  speed: { type: Number, default: 75 },
  /** Temps de lecture une fois la réponse terminée (ms) */
  hold: { type: Number, default: 4200 },
  /** Pause avant une nouvelle génération (ms) */
  pause: { type: Number, default: 8000 },
  /** Nombre maximal de micro-carreaux dans le banc */
  tileCount: { type: Number, default: 2600 },
})

/* --- Logique LLM (streaming de tokens) --- */
const tokens = computed(() => props.message.match(/\S+\s*/g) ?? [])
const count = ref(0)
const cycle = ref(0)
const ready = ref(false)
const fading = ref(false)
const phase = ref('thinking')
const visible = computed(() => tokens.value.slice(0, count.value))

let timer = 0
const later = (fn, ms) => { timer = setTimeout(fn, ms) }

function startCycle() {
  fading.value = false
  count.value = 0
  phase.value = 'thinking'
  cycle.value++

  later(() => {
    phase.value = 'streaming'
    write()
  }, 850)
}

function write() {
  if (count.value < tokens.value.length) {
    count.value++
    const lastTok = tokens.value[count.value - 1] || ''
    const extraPause = /[,.;:!?]\s*$/.test(lastTok) ? 140 : 0
    later(write, props.speed * (0.55 + Math.random() * 0.75) + extraPause)
  } else {
    phase.value = 'idle'
    ready.value = true
    later(resetSmoothly, props.hold)
  }
}

function resetSmoothly() {
  fading.value = true
  later(() => {
    later(startCycle, props.pause)
  }, 550)
}

/* --- Simulation banc de sardines (micro-carreaux) --- */
const containerRef = ref(null)
const canvasRef = ref(null)

let rafId = 0
let resizeObserver = null
let width = 0
let height = 0
let particles = []

// Palette éditoriale discrète sur fond blanc
const PALETTE = [
  [161, 161, 170], // Gris perle (#a1a1aa)
  [129, 140, 248], // Indigo doux (#818cf8)
  [99, 102, 241],  // Indigo signature (#6366f1)
  [148, 163, 184], // Ardoise clair (#94a3b8)
]

function createParticles(w, h) {
  // Adapte automatiquement la densité à la surface tout en gardant des milliers de carreaux
  const target = Math.min(props.tileCount, Math.max(900, Math.floor((w * h) / 420)))
  const list = new Array(target)

  for (let i = 0; i < target; i++) {
    const angle = Math.random() * Math.PI * 2
    const speed = 0.45 + Math.random() * 0.85
    const size = 2 + Math.random() * 1.6
    const color = PALETTE[Math.floor(Math.random() * PALETTE.length)]

    list[i] = {
      x: Math.random() * w,
      y: Math.random() * h,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      baseSpeed: speed,
      size,
      color,
      phase: Math.random() * Math.PI * 2,
      // Légère variation individuelle au sein du banc
      agility: 0.025 + Math.random() * 0.03,
    }
  }
  return list
}

function setupCanvas() {
  const container = containerRef.value
  const canvas = canvasRef.value
  if (!container || !canvas) return

  const rect = container.getBoundingClientRect()
  width = rect.width
  height = rect.height

  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  canvas.width = Math.floor(width * dpr)
  canvas.height = Math.floor(height * dpr)

  const ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  if (!particles.length) {
    particles = createParticles(width, height)
  }
}

function renderShoal(timeMs, staticOnly = false) {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')

  ctx.clearRect(0, 0, width, height)

  const t = timeMs * 0.00035
  const margin = 16

  for (let i = 0; i < particles.length; i++) {
    const p = particles[i]

    // Champ vectoriel multi-ondes : crée des courants collectifs et des virages en banc
    const nx = p.x * 0.0024
    const ny = p.y * 0.0024

    const macroFlow =
      Math.sin(nx + t * 1.1) * 1.35 +
      Math.cos(ny - t * 0.85) * 1.35
    const shoalRipple =
      Math.sin((nx + ny) * 2.3 + t * 2.2) * 0.65

    const desiredAngle = macroFlow + shoalRipple
    // Modulation de vitesse par vagues (accélérations groupées comme des sardines)
    const waveSpeed = p.baseSpeed * (0.85 + 0.45 * Math.sin(nx * 1.8 - t * 2.4 + p.phase * 0.15))

    const targetVx = Math.cos(desiredAngle) * waveSpeed
    const targetVy = Math.sin(desiredAngle) * waveSpeed

    const prevVx = p.vx
    const prevVy = p.vy

    if (!staticOnly) {
      p.vx += (targetVx - p.vx) * p.agility
      p.vy += (targetVy - p.vy) * p.agility
      p.x += p.vx
      p.y += p.vy

      // Bouclage fluide aux bords de l'écran
      if (p.x < -margin) p.x = width + margin
      else if (p.x > width + margin) p.x = -margin
      if (p.y < -margin) p.y = height + margin
      else if (p.y > height + margin) p.y = -margin
    }

    // Calcul de l'amplitude du virage : déclenche un léger scintillement (effet écailles)
    const turnDelta = Math.hypot(p.vx - prevVx, p.vy - prevVy)
    const glint = Math.min(0.32, turnDelta * 14)
    const alpha = 0.14 + glint

    const heading = Math.atan2(p.vy, p.vx)
    const [r, g, b] = p.color

    ctx.save()
    ctx.translate(p.x, p.y)
    ctx.rotate(heading)
    ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha.toFixed(3)})`
    // Micro-carreau légèrement étiré dans le sens de la nage pour lire le mouvement collectif
    ctx.fillRect(-p.size * 0.65, -p.size * 0.45, p.size * 1.3, p.size * 0.9)
    ctx.restore()
  }

  if (!staticOnly) {
    rafId = requestAnimationFrame(renderShoal)
  }
}

onMounted(() => {
  setupCanvas()

  resizeObserver = new ResizeObserver(() => {
    setupCanvas()
  })
  if (containerRef.value) {
    resizeObserver.observe(containerRef.value)
  }

  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) {
    count.value = tokens.value.length
    phase.value = 'idle'
    ready.value = true
    renderShoal(0, true)
  } else {
    startCycle()
    rafId = requestAnimationFrame(renderShoal)
  }
})

onBeforeUnmount(() => {
  clearTimeout(timer)
  cancelAnimationFrame(rafId)
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.merci {
  --bg: #ffffff;
  --ink: #141413;
  --muted: #71717a;
  --accent: #4f46e5;
  --accent-soft: rgba(79, 70, 229, 0.12);
  --border: rgba(20, 20, 19, 0.09);

  position: relative;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 420px;
  padding: 3rem 2.5rem 8rem;
  overflow: hidden;
  color: var(--ink);
  background: var(--bg);
}

/* Canvas des micro-carreaux */
.shoal-canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* Voile radial subtil au centre pour que les carreaux n'interfèrent jamais avec la lecture */
.readability-veil {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background: radial-gradient(
    ellipse 62% 52% at 50% 45%,
    rgba(255, 255, 255, 0.86) 0%,
    rgba(255, 255, 255, 0.45) 58%,
    rgba(255, 255, 255, 0) 100%
  );
}

.stage {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 640px;
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.stage.fading {
  opacity: 0;
  transform: translateY(-6px);
}

/* Badge signature IA */
.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.1rem;
  padding: 0.32rem 0.75rem 0.32rem 0.55rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(6px);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  color: var(--muted);
  transition: border-color 0.4s ease, color 0.4s ease;
}

.ai-badge.thinking,
.ai-badge.streaming {
  color: var(--accent);
  border-color: rgba(79, 70, 229, 0.22);
}

.sparkle {
  color: var(--accent);
  transition: transform 0.6s ease;
}

.ai-badge.thinking .sparkle {
  animation: spinPulse 1.6s ease-in-out infinite;
}

.ai-badge.streaming .sparkle {
  animation: pulseScale 1.2s ease-in-out infinite;
}

/* Typographie éditoriale */
.reply {
  min-height: 2.6em;
  margin: 0;
  font-family: 'Newsreader', Georgia, 'Times New Roman', serif;
  font-size: clamp(2.2rem, 5.2vw, 3.75rem);
  font-weight: 400;
  line-height: 1.22;
  letter-spacing: -0.02em;
  color: var(--ink);
  text-align: left;
}

.tok {
  display: inline;
  animation: tokenIn 0.38s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.cursor {
  display: inline-block;
  width: 2.5px;
  height: 0.88em;
  margin-left: 0.12em;
  vertical-align: -0.08em;
  border-radius: 2px;
  background: linear-gradient(180deg, #4f46e5 0%, #9333ea 100%);
  box-shadow: 0 0 10px var(--accent-soft);
}

.cursor.idle {
  animation: blink 1.15s ease-in-out infinite;
}

/* Barre de saisie flottante blanche */
.prompt {
  position: absolute;
  bottom: 2.5rem;
  left: 50%;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  width: min(640px, calc(100% - 3rem));
  padding: 0.65rem 0.65rem 0.65rem 1.35rem;
  border-radius: 999px;
  border: 1px solid rgba(20, 20, 19, 0.1);
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(12px);
  box-shadow:
    0 4px 20px -2px rgba(20, 20, 19, 0.05),
    0 12px 32px -4px rgba(79, 70, 229, 0.06);
  opacity: 0;
  transform: translate(-50%, 12px);
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.prompt.on {
  opacity: 1;
  transform: translate(-50%, 0);
}

.prompt-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.prompt-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0.65;
}

.placeholder {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
  font-size: 0.95rem;
  color: var(--muted);
}

.send {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  color: #ffffff;
  background: var(--ink);
}

.send.pulse {
  animation: subtleReady 2.8s ease-in-out infinite;
}

@keyframes tokenIn {
  from {
    opacity: 0;
    filter: blur(3px);
  }
  to {
    opacity: 1;
    filter: blur(0);
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.15; }
}

@keyframes spinPulse {
  0% { transform: rotate(0deg) scale(0.9); opacity: 0.6; }
  50% { transform: rotate(90deg) scale(1.12); opacity: 1; }
  100% { transform: rotate(180deg) scale(0.9); opacity: 0.6; }
}

@keyframes pulseScale {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.18); }
}

@keyframes subtleReady {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@media (prefers-reduced-motion: reduce) {
  .tok, .cursor.idle, .sparkle, .send.pulse { animation: none; }
  .prompt, .stage { transition: none; }
}
</style>