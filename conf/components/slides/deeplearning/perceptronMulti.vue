<template>
    <splitSide
        title="Perceptron multi-couches"
        ratio="50/50"
        frame="none"
    >

        <p>
            Un perceptron multicouche est constituée d'une couche d'entrée, 
            d'une ou plusieurs couche TLU appelées couches cachées.
        </p>
        
        <template #media>
            <multiperceptrondemo />
        </template>
    </splitSide>
</template>

<script setup>
import katex from 'katex';
import 'katex/dist/katex.min.css';
import splitSide from '../../splitSide.vue';
import multiperceptrondemo from '../../illustration/multiperceptrondemo.vue';

const rule = String.raw`w_{ij} \longleftarrow w_{ij} + \eta (y_{i} - \hat{y_{i}})x_i`
const weight =String.raw`w_{ij}`
const x_i = String.raw`x_i`
const y_i = String.raw`y_i`
const y_hat_i = String.raw`\hat{y_{i}}`
const eta = String.raw`\eta`

const tex = (src, display = false) =>
    katex.renderToString(src, {
        displayMode: display,
        throwOnError: false,
        output: 'html',
    })
</script>

<style scoped>

</style>