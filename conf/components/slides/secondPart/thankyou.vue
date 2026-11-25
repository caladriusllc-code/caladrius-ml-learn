<template>
  <section class="merci" :aria-label="message">
    <p class="reply" aria-hidden="true">
      <span v-for="(tok, i) in visible" :key="i" class="tok">{{ tok }}</span><span
        class="cursor"
        :class="{ idle: done }"
      />
    </p>

    <div class="prompt" :class="{ on: done }" aria-hidden="true">
      <span class="placeholder">{{ placeholder }}</span>
      <span class="send">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
  placeholder: { type: String, default: 'Des questions ?' },
  /** Délai moyen entre deux mots (ms) */
  speed: { type: Number, default: 90 },
})

const tokens = computed(() => props.message.match(/\S+\s*/g) ?? [])
const count = ref(0)
const visible = computed(() => tokens.value.slice(0, count.value))
const done = computed(() => count.value >= tokens.value.length)

let timer = 0

function next() {
  if (count.value >= tokens.value.length) return
  count.value++
  // Rythme légèrement irrégulier, comme un vrai flux de tokens
  timer = setTimeout(next, props.speed * (0.6 + Math.random() * 0.9))
}

onMounted(() => {
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduce) count.value = tokens.value.length
  else timer = setTimeout(next, 600)
})
onBeforeUnmount(() => clearTimeout(timer))
</script>

<style scoped>
.merci {
  --accent: #67e8f9;

  position: relative;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 320px;
  padding: 2rem 2.5rem 7rem;
  color: #fff;
  background: #050505;
}

.reply {
  max-width: 22ch;
  margin: 0;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(2.2rem, 5.5vw, 4rem);
  line-height: 1.25;
  letter-spacing: -0.01em;
  text-align: left;
}

/* Chaque mot apparaît en fondu, comme un flux de tokens */
.tok {
  animation: in 0.35s ease-out both;
}

.cursor {
  display: inline-block;
  width: 0.09em;
  height: 0.95em;
  margin-left: 0.12em;
  vertical-align: -0.1em;
  background: var(--accent);
  box-shadow: 0 0 12px rgba(103, 232, 249, 0.55);
}

.cursor.idle {
  animation: blink 1.1s steps(1) infinite;
}

/* Barre de saisie */
.prompt {
  position: absolute;
  bottom: 2.5rem;
  left: 50%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  width: min(640px, calc(100% - 3rem));
  padding: 0.7rem 0.7rem 0.7rem 1.25rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.03);
  opacity: 0;
  transform: translate(-50%, 8px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}

.prompt.on {
  opacity: 1;
  transform: translate(-50%, 0);
}

.placeholder {
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.45);
}

.send {
  display: grid;
  place-items: center;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  color: #050505;
  background: var(--accent);
}

@keyframes in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes blink {
  50% { opacity: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .tok, .cursor.idle { animation: none; }
  .prompt { transition: none; }
}
</style>