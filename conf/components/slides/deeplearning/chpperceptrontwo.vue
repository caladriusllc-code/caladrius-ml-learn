<template>
    <splitSide
        title="Le perceptron"
        ratio="50/50"
        frame="none"
    >

        <p>
            <strong>Le perceptron:</strong>
            C'est une architecture un peu plus différente 
            de la précédente où maintenant les entrées et 
            les sorties de sont désormais des nombres et 
            chaque connexion en entrée possède un poids. 
        </p>

        <p>
            Ici un neurone est appelé unité linéaire à 
            seuil ou Linear Threshold Unit (TLU)
        </p>

        <div>
            la TLU se calcul comme suit:
            <div v-html="tex(model, true)" />
        </div>

        <p>
            Puis elle applique une fonction échélon <span v-html="tex(f)" /> à 
            <span v-html="tex(z)" /> telle que:
        </p>

        <div v-html="tex(f_z, true)" />
    

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