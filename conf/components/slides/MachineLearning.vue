<template>
  <splitSide
    title="Solution d'apprentissage"
    ratio="50/50"
    frame="none"
    takeaway="Apprentissage automatique"
  >

    <p>
        <strong>Machine learning :</strong>
        C'est un domaine de l'intelligence
        artificielle qui se base sur des approches 
        mathématiques pour conférer aux ordinateurs 
        la capacité d'apprendre à partir de données.
    </p> 

    <p>Dans le Machine Learning, il y a différents types d'apprentissage :</p>

    <ul>
        <li>L'apprentissage supervisé (ce que nous allons utiliser)</li>
        <li>L'apprentissage non-supervisé</li>
        <li>L'apprentissage par renforcement</li>
    </ul>

    <template #media>
      <gearmecanism />
    </template>
  </splitSide>
</template>

<script setup>
import splitSide from '../splitSide.vue';
import gearmecanism from '../gearmecanism.vue'
</script>

<style scoped>

</style>