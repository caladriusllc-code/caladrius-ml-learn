<template>
  <splitSide
    title="Algorithme d'apprentissage"
    ratio="50/50"
    frame="none"
  >

    <p>
      Le but de notre algorithme d'apprentissage est de nous aider à trouver les meilleurs
      paramètres de notre modèle. Pour le faire nous allons passer
      une fonction de coût <span v-html="tex(j)" />.
    </p>

    <div>
      Un Exemple : l'erreur quadratique moyenne (MSE) :
      <div v-html="tex(example, true)" />
    </div>
   

    <template #media>
      <gradientDescent :n="40" :seed="7" :amplitude="6" />
    </template>
  </splitSide>
</template>

<script setup>
import { useNav } from '@slidev/client'
import katex from 'katex'
import 'katex/dist/katex.min.css' // au cas où le CSS n'est pas chargé

import splitSide from '../splitSide.vue'
import gradientDescent from '../gradientDescent.vue'

const { clicks } = useNav()

const model = String.raw`J = f(\theta)`
const j = String.raw`J = f(\theta)`
const example = String.raw`MSE = \frac{1}{N} \sum_{i=1}^{N} (y_i - f(x_i ;\, \theta))^2`

const tex = (src, display = false) =>
  katex.renderToString(src, {
    displayMode: display,
    throwOnError: false,
    output: 'html', // ← supprime la version MathML
  })
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