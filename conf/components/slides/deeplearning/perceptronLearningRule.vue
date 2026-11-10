<template>
    <splitSide
        title="Règle d'apprentissage"
        ratio="50/50"
        frame="none"
    >

        <div>
            La règle de l'apprentissage est définie comme suit :
            <div v-html="tex(rule, true)" />
        </div>

        
        <template #media>
            <regle_apprentissage_perceptron_anime />
        </template>
    </splitSide>
</template>

<script setup>
import katex from 'katex';
import 'katex/dist/katex.min.css';
import splitSide from '../../splitSide.vue';
import regle_apprentissage_perceptron_anime from '../../regle_apprentissage_perceptron_anime.vue'

const rule = String.raw`w_{ij} = w_{ij} + \eta (y_{i} - \hat{y_{i}})x_i`


const tex = (src, display = false) =>
    katex.renderToString(src, {
        displayMode: display,
        throwOnError: false,
        output: 'html',
    })
</script>

<style scoped>

</style>