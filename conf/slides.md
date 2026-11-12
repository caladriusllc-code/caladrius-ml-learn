---
theme: default
title: L'intelligence artificielle
colorSchema: light
transition: fade
fonts:
  sans: Bricolage Grotesque
  provider: google
  weight: '400,600,700'
layout: none
class: px-24 py-20
---

<script setup>
import TokenTitle from './components/tokentitle.vue'
import Vintageslides from './components/Vintageslides.vue'
</script>

<TokenTitle>
  <div class="theme">
    Reconnaissance d’image et réseaux de neurones artificiels : le b.a.-ba du deep learning
  </div>
  <strong>MIAKO Jean Yves Arnold</strong><br />
  UCAO-UUA, 28/11/2026
</TokenTitle>

---
layout: none
class: px-12 py-8
---

<Vintageslides> 
  <p class="q"> « Rien dans la vie n’est à 
    <span :class="$clicks >= 1 ? 'dim' : ''">craindre</span>, 
    <span :class="$clicks >= 1 ? 'hl' : ''">tout doit être compris.</span> 
  </p> 
  <p v-click="2" class="q"> C’est maintenant le moment d’apprendre davantage. » </p> 
  <p v-click="2" class="by">Marie Curie, prix Nobel de physique et de chimie</p> 
  <p v-click="3" class="ia"> Pour les réseaux de neurones aussi : comprendre comment ils voient, c’est le premier pas pour ne plus les craindre. </p> 
</Vintageslides>

<style>
.quote {
  border-left: 6px solid var(--cobalt);
  padding-left: 40px;
  max-width: 800px;
}
.quote .q {
  font-size: 40px;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.02em;
  margin: 0 0 16px;
}
.quote .dim { color: var(--muted); transition: color 0.5s ease; }
.quote .hl { background: var(--tint); color: var(--cobalt); border-radius: 0.12em; transition: all 0.5s ease; }
.quote .by { font-size: 18px; color: var(--muted); margin: 8px 0 40px; }
.quote .ia { font-size: 22px; max-width: 620px; line-height: 1.4; margin: 0; }

.q { font-size: 36px; font-style: italic; line-height: 1.25; margin: 0 0 14px; } .q .dim { color: var(--v-faded); transition: color 0.5s ease; } .q .hl { color: var(--v-accent); box-shadow: inset 0 -0.3em rgba(110, 42, 34, 0.16); transition: all 0.5s ease; } .by { font-size: 18px; color: var(--v-faded); margin: 6px 0 36px; } .ia { font-size: 20px; line-height: 1.4; margin: 0; }
</style>

---
layout: none
class: px-12 py-8
---

<script setup>
import manuscrits from './components/slides/manuscrits.vue'
</script>

<manuscrits>
  
</manuscrits>

---
layout: center
class: px-12 py-8
---

<script setup>
import iadefinition from './components/slides/iadefinition.vue'
</script>

<iadefinition>
  
</iadefinition>

---
layout: center
class: px-12 py-8
clicks: 3
---

<script setup>
import IADefinitionTwo from './components/slides/iadefinition_two.vue'
</script>

<IADefinitionTwo />

---
layout: none
class: px-12 py-8
---
<script setup>
import Mecanisme from './components/slides/Mecanisme.vue'
</script>

<Mecanisme />

---
layout: center
class: px-12 py-8
---
<script setup>
import MachineLearning from './components/slides/MachineLearning.vue'
</script>

<MachineLearning />

---
layout: none
class: px-12 py-8
clicks: 2
---
<script setup>
import learningcomponent from './components/slides/learningcomponent.vue'
</script>

<learningcomponent />

---
layout: none
class: px-12 py-8
---
<script setup>
import learnalgorithm from './components/slides/learnalgorithm.vue'
</script>

<learnalgorithm />

---
layout: none
class: px-12 py-8
---
<script setup>
import DeepLearningTransition from './components/slides/deeplearning/transition.vue'
</script>

<DeepLearningTransition />

---
layout: none
class: px-12 py-8
---

<script setup>
import chpperceptron from './components/slides/deeplearning/chpperceptron.vue'
</script>

<chpperceptron />

---
layout: none
class: px-12 py-8
---

<script setup>
import TluMinimalisteNoirBlanc from './components/tlu_minimaliste_noir_blanc.vue'
</script>

<TluMinimalisteNoirBlanc />

---
layout: none
class: px-12 py-8
---
<script setup>
import chpperceptrontwo from './components/slides/deeplearning/chpperceptrontwo.vue'
</script>

<chpperceptrontwo />

---
layout: none
class: px-12 py-8
---
<script setup>
import perceptronLearning from './components/slides/deeplearning/perceptronLearning.vue'
</script>

<perceptronLearning />

---
layout: center
class: px-12 py-8
---
<script setup>
import learninganimation from './components/regle_apprentissage_perceptron_anime.vue'
</script>

<learninganimation />

---
layout: none
class: px-12 py-8
---
<script setup>
import perceptronLearningRule from './components/slides/deeplearning/perceptronLearningRule.vue'
</script>

<perceptronLearningRule />

---
layout: none
class: px-12 py-8
---
<script setup>
import chpperceptrontwotwo from './components/slides/deeplearning/chpperceptrontwotwo.vue'
</script>

<chpperceptrontwotwo />

---
layout: none
class: px-12 py-8
---
<script setup>
import multiperceptrondemo from './components/illustration/multiperceptrondemo.vue'
</script>

<multiperceptrondemo />

---
layout: none
class: px-12 py-8
---
<script setup>
import perceptronMulti from './components/slides/deeplearning/perceptronMulti.vue'
</script>

<perceptronMulti />

---
layout: none
class: p-0
---
<script setup>
import secondPartIndex from './components/slides/secondPart/secondPartIndex.vue'
</script>

<secondPartIndex />

---
layout: none
class: p-4
---
<script setup>
import numberPic from './components/slides/secondPart/numberPic.vue'
</script>

<numberPic />

---
layout: center
class: p-4
---
<script setup>
import MnistNormalization from './components/slides/secondPart/MnistNormalization.vue'
</script>

<MnistNormalization />

---
layout: center
class: p-4
---
<script setup>
import MnistVectorization from './components/slides/secondPart/MnistVectorization.vue'
</script>

<MnistVectorization />

---
class: p-4
---
<script setup>
import neuralNetworkMnist from './components/slides/secondPart/neuralNetworkMnist.vue'
</script>

<neuralNetworkMnist />

---
class: p-4
---
<script setup>
import forwardPropagation from './components/slides/secondPart/forwardPropagation.vue'
</script>

<forwardPropagation />