<template>
  <splitSide
    title="Solution d'apprentissage"
    ratio="50/50"
    frame="none"
    takeaway="Composant du machine learning"
  >

    <p>
        Pour mettre en place un modèle de Machine Learnig,
        Nous passons par <span class="kw" :class="{ on: clicks >= 1 }">un modèle</span> et 
        <span class="kw" :class="{ on: clicks >= 2 }" >un algorithme 
        d'apprentissage.</span>
    </p>

    <div>
      Un modèle :
      <div v-html="tex(model, true)" />
    </div>
   

    <template #media>
      <gearmecanism />
    </template>
  </splitSide>
</template>

<script setup>
import { useNav } from '@slidev/client';
import katex from 'katex'

import splitSide from '../splitSide.vue';
import gearmecanism from '../gearmecanism.vue'

const {clicks} = useNav()

// String.raw évite de doubler les antislashs (\theta au lieu de \\theta)
const model = String.raw`y_t = f(x_t ;\, \theta)`

const tex = (src, display = false) =>
  katex.renderToString(src, { displayMode: display, throwOnError: false })
</script>

<style scoped>
.kw {
  font-weight: 400;
  transition: font-weight 0.4s ease, color 0.4s ease;
}
.kw.on {
  font-weight: 700;
  color: #1d4ed8;
}
</style>