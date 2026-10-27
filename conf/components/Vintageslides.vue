<script setup lang="ts">
import { ref } from 'vue'

const hidden = ref(false)
function onError(e: Event) {
  console.warn('Image introuvable :', (e.target as HTMLImageElement).src)
  hidden.value = true
}
</script>

<template>
  <div class="vintage">
    <img
      v-if="!hidden"
      class="photo"
      src="/marie-curie.jpg"
      alt="Portrait de Marie Curie"
      @error="onError"
    />
    <div class="vignette" />
    <div class="grain" />
    <div class="frame" />
    <div class="content"><slot /></div>
  </div>
</template>

<style scoped>
.vintage {
  --v-paper: #e8dcc2;
  --v-ink: #2a1d12;
  --v-faded: #7d6a52;
  --v-accent: #6e2a22;
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: var(--v-paper);
  color: var(--v-ink);
  font-family: 'IM Fell English', Georgia, 'Times New Roman', serif;
}

.photo {
  position: absolute;
  top: 0;
  right: 0;
  width: 62%;
  height: 100%;
  object-fit: cover;
  object-position: center 20%;
  filter: grayscale(1) sepia(0.75) contrast(1.05) brightness(0.95);
  mix-blend-mode: multiply;
  /* le portrait se fond dans le papier côté texte */
  -webkit-mask-image: linear-gradient(to right, transparent 0%, transparent 25%, #000 70%);
  mask-image: linear-gradient(to right, transparent 0%, transparent 25%, #000 70%);
}

.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, transparent 55%, rgba(60, 35, 15, 0.38) 100%);
  pointer-events: none;
}

.grain {
  position: absolute;
  inset: 0;
  opacity: 0.35;
  mix-blend-mode: multiply;
  pointer-events: none;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .2  0 0 0 0 .13  0 0 0 0 .08  0 0 0 .55 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
}

.frame {
  position: absolute;
  inset: 22px;
  border: 3px double rgba(42, 29, 18, 0.5);
  pointer-events: none;
}

.content {
  position: relative;
  box-sizing: border-box;
  height: 100%;
  max-width: 56%;
  padding: 72px 40px 72px 84px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>