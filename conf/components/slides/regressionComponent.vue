<template>
  <splitSide
    title="Régression et descente de gradient"
    ratio="50/50"
    frame="none"
    takeaway="Trouver la droite qui passe au plus près des points"
  >

    <p>
      Nous observons des données <span v-html="tex(pair)" />.
      Chaque point associe une entrée <span v-html="tex(x)" />
      à une sortie <span v-html="tex(y)" />.
    </p>

    <p>
      Quand <span v-html="tex(y)" /> est continue, on cherche un modèle
      <span v-html="tex(line)" /> qui reproduit cette tendance.
    </p>

    <template #media>
      <regressionplot :n="40" :seed="7" :amplitude="4" />
    </template>
  </splitSide>
</template>

<script setup>
import katex from 'katex'
import 'katex/dist/katex.min.css'

import splitSide from '../splitSide.vue'
import regressionplot from '../regressionPlot.vue'

const pair = String.raw`(x_t,\, y_t)`
const x = String.raw`x_t`
const y = String.raw`y_t`
const line = String.raw`f(x_t ;\, \theta) = \theta_1 x_t + \theta_0`

const tex = (src, display = false) =>
  katex.renderToString(src, {
    displayMode: display,
    throwOnError: false,
    output: 'html',
  })
</script>