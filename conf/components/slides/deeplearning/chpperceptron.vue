<template>
    <splitSide
        title="Deep Learning"
        ratio="50/50"
        frame="none"
    >

        <p>
            <strong>Le deep learning:</strong>
            le deep learning se base sur le fonctionnement 
            du cerveau humain pour construire une machine 
            intelligente. Il s'agit en fait d'un modèle 
            d'apprentissage automatique qui se base sur 
            les neurones biologiques que l'on trouve dans 
            notre cerveau. 
        </p>

        <p>
            Cette philosophie d'apprentissage est initiée 
            par McCulloch et Pits en 1943 et voici comment 
            le premier réseau de neurones est formalisé 
            comme suit :
        </p>

        <p>
            Ils ont montré qu'en construisant un système de neuronne,
            on pourrait réaliser des tâches complexes.
        </p>
    

        <template #media>
            <McCullochPitts />
        </template>
    </splitSide>
</template>

<script setup>
import splitSide from '../../splitSide.vue';
import McCullochPitts from '../../McCullochPitts.vue'


</script>

<style scoped>

</style>