<template>
    <splitSide
        title="Le perceptron"
        ratio="50/50"
        frame="none"
    >

        <p>
            Une seule TLU peut être employé pour faire de la 
            classification bilinéaire simple. 
            Elle calcule une fonction linéaire de ses entrées, 
            si le résultat dépasse un certain seuil, 
            présente en sortie la classe positive sinon 
            elle présente la classe négative. 
            Elle ressemble plus à de la régression logistique 
        </p>

        <p>
            Le souci est que le perceptron ne fait que des classifications 
            linéaires, or on sait que dans la vie, les données ne sont pas 
            linéaires, par exemple les images. Comment procède-t-on pour 
            faire une classification d'images ?
        </p>
    

        <template #media>
            <tlu_minimaliste_noir_blanc />
        </template>
    </splitSide>
</template>

<script setup>
import katex from 'katex';
import 'katex/dist/katex.min.css';
import splitSide from '../../splitSide.vue';
import tlu_minimaliste_noir_blanc from '../../tlu_minimaliste_noir_blanc.vue'

const model = String.raw`z = w_1x_1 + w_2x_2 + \dots + w_nx_n + b = x^{T}w + b`
const f = String.raw`f`
const z = String.raw`z`
const f_z = String.raw`f(z) = \begin{cases} 1 & \text{si } z \geq 0 \\ 0 & \text{si } z < 0 \end{cases}`

const tex = (src, display = false) =>
    katex.renderToString(src, {
        displayMode: display,
        throwOnError: false,
        output: 'html',
    })
</script>

<style scoped>

</style>