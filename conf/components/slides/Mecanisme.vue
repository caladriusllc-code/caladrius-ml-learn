<template>
  <splitSide
    title="Comment une IA apprend t-elle?"
    ratio="50/50"
    frame="none"
    takeaway="Apprentissage automatique"
  >
    <p>
      De cette définition on comprend que pour exécuter 
      une tâche il faut de l'apprentissage perceptuelle, 
      de l'organisation cognitive et d'un raisonnement critique.
    </p>

    <p>
      Dès-lors, comment est-ce qu'une intelligence artificielle apprend à faire une tâche ? 
      En l'occurrence comment pouvons-nous entrainer notre intelligence artificielle ?
    </p>

    <template #media>
      <gearmecanism />
    </template>
  </splitSide>
</template>

<script setup>
import splitSide from '../splitSide.vue';
import gearmecanism from '../gearmecanism.vue'
</script>