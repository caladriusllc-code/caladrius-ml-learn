<template>
    <splitSide
        title="Comment le perceptron apprend t-il?"
        ratio="50/50"
        frame="none"
    >

        <p>
            L'algorithme d'entraînement du perceptron proposé 
            par Rosenblatt se base sur la règle de Hebb
        </p>

        <p>
            Donald Hebb suggère que si un neurone biologique 
            déclenche souvent un autre ; alors la connexion 
            entre les deux se renforcent !
        </p>

        <p>
            La règle de l'apprentissage du perceptron renforce 
            les connexions qui aident à réduire l'erreur
        </p>

        <p>
            A chaque instance d'apprentissage, il réduit 
            les poids qui ont contribué à l'erreur et 
            renforce ceux qui ont contribué à la bonne réponse.
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

const rule = String.raw`z = w_1x_1 + w_2x_2 + \dots + w_nx_n + b = x^{T}w + b`


const tex = (src, display = false) =>
    katex.renderToString(src, {
        displayMode: display,
        throwOnError: false,
        output: 'html',
    })
</script>

<style scoped>

</style>