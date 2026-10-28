<!-- components/slides/iadefinition_two.vue -->
<template>
  <SplitSlide
    :image="img"
    alt="Marvin Minsky"
    takeaway="Intelligence artificielle"
  >
    <p>
      C'est la construction de programmes informatiques qui
      s'adonnent à des tâches qui sont, pour l'instant,
      accomplies de façon plus satisfaisante par des humains,
      car elles demandent des processus mentaux de haut niveau
      tels que :
      <span class="kw" :class="{ on: clicks >= 1 }">l'apprentissage perceptuel</span>,
      <span class="kw" :class="{ on: clicks >= 2 }">l'organisation de la mémoire</span>
      et
      <span class="kw" :class="{ on: clicks >= 3 }">le raisonnement critique</span>.
    </p>

    <strong>Marvin Lee Minsky</strong>
  </SplitSlide>
</template>

<script setup>
import { useNav } from '@slidev/client'
import SplitSlide from '../splitSide.vue'
import img from '../assets/Marvin_Minsky_at_OLPCb.jpg'

const { clicks } = useNav()
</script>

<style scoped>
.kw {
  font-weight: 400;
  transition: font-weight 0.4s ease, color 0.4s ease;
}
.kw.on {
  font-weight: 700;
  color: #1d4ed8;
}
</style>