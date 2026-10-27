<!-- components/slides/iadefinition.vue -->
<template>
  <SplitSlide
    :image="img"
    alt="Whirlwind, ordinateur du MIT, 1943"
    takeaway="Intelligence artificielle"
  >
    <p>
      Imaginons un instant qu'on décide d'écrire un programme informatique
      dont le but est de reconnaître les chiffres ci-dessus : on vient là de
      définir <strong>une intelligence artificielle (IA)</strong>.
    </p>
    <p>
      C'est un terme employé formellement pour la première fois en 1956 par
      John McCarthy et ses pairs, lors de la conférence
      <i>« Dartmouth Summer Research Project on Artificial Intelligence »</i>.
    </p>
  </SplitSlide>
</template>

<script setup>
import SplitSlide from '../splitSide.vue'
import img from '../assets/Marvin_Minsky_at_OLPCb_(3x4_cropped).jpg'
</script>