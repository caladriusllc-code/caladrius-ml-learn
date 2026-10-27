<!--
  SplitSlide : slide « texte + média » réutilisable (Slidev).

  Props
    title      Titre en haut du bloc texte (optionnel)
    takeaway   Phrase clé en bas du bloc texte, ex. le concept à retenir (optionnel)
    image      URL de l'image. Depuis /public : "/mon-image.jpg"
    alt        Texte alternatif de l'image
    caption    Légende / source sous le média (optionnel)
    ratio      Largeur texte/média : "50/50" (défaut), "60/40", "40/60"...
    reverse    Place le média à gauche et le texte à droite
    fit        "contain" (défaut, image entière) ou "cover" (image rognée pour remplir)
    frame      "white" (défaut), "subtle" (fond neutre) ou "none" (aucun cadre)

  Slots
    default    Contenu du bloc texte (paragraphes, listes, etc.)
    title      Remplace la prop title (pour du contenu riche)
    takeaway   Remplace la prop takeaway
    media      Remplace l'image : schéma, composant Vue (ex. <MnistSimulator />), vidéo...
-->
<template>
  <div class="split" :style="{ '--cols': cols }">
    <section class="text" :class="{ 'is-second': reverse }">
      <h2 v-if="title || $slots.title" class="title">
        <slot name="title">{{ title }}</slot>
      </h2>

      <div class="body">
        <slot />
      </div>

      <p v-if="takeaway || $slots.takeaway" class="takeaway">
        <slot name="takeaway">{{ takeaway }}</slot>
      </p>
    </section>

    <figure class="media" :class="[`frame-${frame}`, { 'is-first': reverse }]">
      <div class="media-box">
        <slot name="media">
          <img
            v-if="image"
            :src="image"
            :alt="alt"
            :style="fit === 'cover'
              ? { objectFit: 'cover', width: '100%', height: '100%' }
              : { objectFit: fit }"
          />
        </slot>
      </div>
      <figcaption v-if="caption" class="caption">{{ caption }}</figcaption>
    </figure>
  </div>
</template>

<script>
export default {
  name: 'SplitSlide',
  props: {
    title: { type: String, default: '' },
    takeaway: { type: String, default: '' },
    image: { type: String, default: '' },
    alt: { type: String, default: '' },
    caption: { type: String, default: '' },
    ratio: { type: String, default: '50/50' },
    reverse: { type: Boolean, default: false },
    fit: { type: String, default: 'contain' },
    frame: { type: String, default: 'white' }
  },
  computed: {
    cols() {
      const [a, b] = this.ratio.split('/').map(Number)
      const text = a || 50
      const media = b || 50
      // Le texte reste le premier élément du DOM (ordre de lecture) ;
      // en mode reverse, on inverse seulement les largeurs et l'ordre visuel.
      return this.reverse ? `${media}fr ${text}fr` : `${text}fr ${media}fr`
    }
  }
}
</script>

<style scoped>
.split {
  display: grid;
  grid-template-columns: var(--cols);
  grid-template-rows: minmax(0, 1fr);
  align-items: center;
  gap: 2rem;
  width: 100%;
  height: 100%;
  padding: 1rem;
  box-sizing: border-box;
}

/* ---------- Bloc texte ---------- */
.text {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.text.is-second {
  order: 2;
}

.title {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  line-height: 1.2;
}

.body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  line-height: 1.55;
}

/* Le contenu des slots appartient au parent : :deep est nécessaire pour le styler */
.body :deep(p),
.body :deep(ul),
.body :deep(ol) {
  margin: 0;
}

.body :deep(ul),
.body :deep(ol) {
  padding-left: 1.25rem;
}

.body :deep(li + li) {
  margin-top: 0.4rem;
}

.takeaway {
  margin: 0.5rem 0 0;
  padding-left: 0.9rem;
  border-left: 3px solid rgba(128, 128, 128, 0.6);
  font-size: 26px;
  font-weight: 600;
  line-height: 1.25;
}

/* ---------- Média ---------- */
.media {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  height: 100%;
  min-width: 0;
  min-height: 0;
  margin: 0;
}

.media.is-first {
  order: 1;
}

.media-box {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  border-radius: 8px;
  overflow: hidden;
}

.frame-white .media-box {
  background: #ffffff;
}

.frame-subtle .media-box {
  background: rgba(128, 128, 128, 0.08);
  border: 1px solid rgba(128, 128, 128, 0.3);
}

.frame-none .media-box {
  padding: 0;
}

/* Les proportions de l'image sont conservées (plus d'étirement) */
.media-box img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  border-radius: 4px;
}

.caption {
  font-size: 0.75rem;
  line-height: 1.3;
  opacity: 0.65;
}
</style>