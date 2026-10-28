<template>
  <splitSide
    title="Apprendre, puis réfléchir"
    ratio="50/50"
    frame="none"
    takeaway="Un réseau de neurones apprend, puis raisonne."
  >
    <p>Chaque roue entraîne la suivante : sans apprentissage, pas de réflexion.</p>

    <template #media>
      <gearmecanism />
    </template>
  </splitSide>
</template>

<script setup>
import splitSide from '../splitSide.vue';
import gearmecanism from '../gearmecanism.vue'
</script>