<template>
  <div class="main-wrapper">
    <h1>
      <span v-for="(t, i) in visible.title" :key="'t' + i" class="token">{{ t }}</span>
      <span v-if="cursorOn === 'title'" class="caret" />
    </h1>

    <p>
      <span v-for="(t, i) in visible.body" :key="'b' + i" class="token">{{ t }}</span>
      <span v-if="cursorOn === 'body'" class="caret" />
    </p>
  </div>
</template>

<script>
import { useIsSlideActive } from '@slidev/client'

const TITLE = "Deuxième partie : Comment fonctionne la reconnaissance d'image?"
const BODY =
  "Voyons ensemble comment est-ce que les ordinateurs analysent " +
  "et reconnaissent-ils les images manuscrites " +
  "Et souvent les visages des individus"

// Découpe grossière façon « tokens » : mots (avec leur espace) en morceaux de 4 lettres max.
function tokenize(text) {
  const raw = text.match(/\s?[\p{L}’']+|\s?[^\s\p{L}]/gu) || []
  const tokens = []
  for (const piece of raw) {
    const lead = piece.match(/^\s/) ? piece[0] : ""
    const word = piece.slice(lead.length)
    if (word.length <= 5) {
      tokens.push(piece)
      continue
    }
    for (let i = 0; i < word.length; i += 4) {
      tokens.push((i === 0 ? lead : "") + word.slice(i, i + 4))
    }
  }
  return tokens
}

export default {
  setup() {
    // true uniquement quand cette slide est affichée
    return { isActive: useIsSlideActive() }
  },
  data() {
    return {
      visible: { title: [], body: [] },
      cursorOn: "title",
      timer: null,
    }
  },
  watch: {
    isActive: {
      immediate: true,
      handler(active) {
        if (active) this.start()
        else this.stop()
      },
    },
  },
  beforeUnmount() {
    this.stop()
  },
  methods: {
    stop() {
      clearTimeout(this.timer)
    },
    start() {
      this.stop()
      this.visible = { title: [], body: [] }
      this.cursorOn = "title"

      const queue = [
        ...tokenize(TITLE).map((t) => ({ part: "title", t })),
        ...tokenize(BODY).map((t) => ({ part: "body", t })),
      ]
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches

      const next = () => {
        const item = queue.shift()
        if (!item) {
          this.cursorOn = "body"
          return
        }
        this.cursorOn = item.part
        this.visible[item.part].push(item.t)
        const pause = /[.,:]$/.test(item.t) ? 380 : 40 + Math.random() * 110
        this.timer = setTimeout(next, reduced ? 0 : pause)
      }
      next()
    },
  },
}
</script>

<style scoped>
/* Remplit toute la slide (et non la fenêtre du navigateur) et centre le contenu */
.main-wrapper {
  position: absolute;
  inset: 0;
  box-sizing: border-box;
  padding: 0 4rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  text-align: center;
  width: 100%;
}

.main-wrapper h1 {
  margin: 0;
  width: 100%;
  max-width: 18ch;
  font-size: 2rem;
  line-height: 1.1;
  font-weight: 650;
  letter-spacing: -0.02em;
  text-align: center;
}

.main-wrapper p {
  margin: 0;
  width: 100%;
  max-width: 34em;
  font-size: 1.6rem;
  line-height: 1.5;
  opacity: 0.8;
  text-align: center;
}

/* Chaque nouveau token apparaît avec un léger surlignage qui s’estompe. */
.token {
  animation: arrive 0.6s ease-out;
}

@keyframes arrive {
  from {
    background: rgba(80, 130, 255, 0.35);
  }
  to {
    background: transparent;
  }
}

.caret {
  display: inline-block;
  width: 0.12em;
  height: 1em;
  margin-left: 0.08em;
  vertical-align: -0.12em;
  background: #2f5fd0;
  animation: blink 1s steps(1) infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .token,
  .caret {
    animation: none;
  }
}
</style>