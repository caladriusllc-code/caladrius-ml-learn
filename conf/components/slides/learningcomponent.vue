<template>
  <splitSide
    title="Modèle d'apprentissage"
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

    <p>
      Une fois le modèle entraîné, il doit donner une prédiction
      <span v-html="tex(y)" /> à partir de <span v-html="tex(x)" />.
    </p>

    <p>
      Quand <span v-html="tex(y)" /> est continue on parle de tâche de regression, quand <span v-html="tex(y)" /> est discrète on parle de tâche de classification.
    </p>
   

    <template #media>
      <regressionplot :n="40" :seed="7" :amplitude="6"  />
    </template>
  </splitSide>
</template>

<script setup>
import { useNav } from '@slidev/client'
import katex from 'katex'
import 'katex/dist/katex.min.css' // au cas où le CSS n'est pas chargé

import splitSide from '../splitSide.vue'
import regressionplot from '../regressionPlot.vue'

const { clicks } = useNav()

const model = String.raw`y_t = f(x_t ;\, \theta)`
const x = String.raw`x_t`
const y = String.raw`y_t`

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