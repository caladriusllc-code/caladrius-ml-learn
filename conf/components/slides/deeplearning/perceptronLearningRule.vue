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

        <ul>
            <li> - <span v-html="tex(weight)" /> correspond au poids de la connexion entre <i>i-ème</i> de neurone d'entrée et le <i>j-ème</i> neurone de sortie</li>
            <li> - <span v-html="tex(eta)" />est le taux d'apprentissage</li>
            <li> - <span v-html="tex(y_i)" />est la sortie désirée pour l'entrée <span v-html="tex(x_i)" /></li>
            <li> - <span v-html="tex(y_hat_i)" /> est la sortie calculée par le perceptron</li>
            <li> - <span v-html="tex(x_i)" /> est l'entrée du neurone</li>
        </ul>

        <p>Franck Rosenblatt a montré que cette règle permet de faire converger le perceptron vers une solution optimale.</p>
        
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