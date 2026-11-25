<template>
  <section
    class="apa-biblio"
    :class="{ compact }"
    aria-label="Bibliographie au format APA"
  >
    <header class="biblio-header">
      <h2 class="biblio-title">{{ title }}</h2>
      <span class="biblio-badge">Norme APA · 7ᵉ éd. · {{ sortedEntries.length }} références</span>
    </header>

    <ul class="biblio-grid" :style="gridStyle">
      <li
        v-for="(book, i) in sortedEntries"
        :key="book.id"
        class="biblio-card"
        :style="{ '--i': i }"
      >
        <!-- Scène de couverture -->
        <div class="cover-stage">
          <span v-if="book.kind" class="kind-tag">{{ book.kind }}</span>

          <div class="book-showcase" :class="{ 'landscape-frame': isVideo(book) }">
            <img
              v-if="book.cover && !brokenCovers[book.id]"
              :src="book.cover"
              :alt="`Couverture de ${book.title}`"
              class="cover-img"
              loading="lazy"
              @error="brokenCovers[book.id] = true"
            />
            <div v-else class="cover-fallback" aria-hidden="true">
              <span v-if="book.edition" class="fb-edition">{{ book.edition }}</span>
              <span class="fb-title">{{ book.title }}</span>
              <span class="fb-author">{{ book.authors }}</span>
            </div>
            <div class="book-sheen" aria-hidden="true"></div>
          </div>
        </div>

        <!-- Référence APA 7 -->
        <div class="ref-body">
          <p class="apa-citation">
            <span class="authors">{{ book.authors }}</span>{{ ' ' }}({{ book.year }}).{{ ' ' }}
            <em class="book-title">{{ fullTitle(book) }}</em>{{ details(book) }}.{{ ' ' }}
            <span class="publisher">{{ book.publisher }}.</span>
            <template v-if="book.url">
              {{ ' ' }}<a
                :href="book.url"
                class="ref-url"
                target="_blank"
                rel="noopener noreferrer"
              >{{ shortUrl(book.url) }}</a>
            </template>
          </p>

          <p v-if="book.note" class="ref-note">{{ book.note }}</p>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { reactive, computed } from 'vue'

const defaultEntries = [
  {
    id: 'geron-2023',
    kind: 'Livre',
    authors: 'Géron, A.',
    year: 2023,
    title: 'Deep Learning avec Keras et TensorFlow',
    subtitle: 'Mise en œuvre et cas concrets',
    edition: '3ᵉ éd.',
    translator: 'A. Bohy',
    publisher: 'Dunod',
    cover: '/images.jfif',
    url: '',
    note: 'Architectures neuronales, rétropropagation et descente de gradient.',
  },
  {
    id: 'alammar-2024',
    kind: 'Livre',
    authors: 'Alammar, J., & Grootendorst, M.',
    year: 2024,
    title: 'Hands-On Large Language Models',
    subtitle: 'Language understanding and generation',
    edition: '1ʳᵉ éd.',
    publisher: 'O’Reilly Media',
    cover: '/llm.jfif',
    url: '',
    note: 'Compréhension des concepts relatifs aux LLM.',
  },
  {
    id: 'deisenroth-2020',
    kind: 'Livre',
    authors: 'Deisenroth, M. P., Faisal, A. A., & Ong, C. S.',
    year: 2020,
    title: 'Mathematics for machine learning',
    publisher: 'Cambridge University Press',
    cover: '/images.jpeg',
    url: '',
    note: 'Algèbre linéaire, calcul différentiel et probabilités.',
  },
  {
    id: 'sanderson-2017',
    kind: 'Vidéo',
    authors: 'Sanderson, G. (3Blue1Brown)',
    year: 2017,
    title: 'But what is a neural network?',
    subtitle: 'Deep learning, chapter 1',
    medium: 'Vidéo',
    publisher: 'YouTube',
    cover: '/threeblue.jpeg',
    url: 'https://www.youtube.com/watch?v=aircAruvnKk',
    note: 'Introduction visuelle aux réseaux de neurones.',
  },
]

const props = defineProps({
  title: { type: String, default: 'Références bibliographiques' },
  entries: { type: Array, default: () => [] },
  alphabetical: { type: Boolean, default: true },
  compact: { type: Boolean, default: false },
  /** Nombre de colonnes de la grille (4 par défaut pour aligner 4 affiches sur une slide) */
  columns: { type: Number, default: 4 },
})

const brokenCovers = reactive({})

const activeEntries = computed(() =>
  props.entries.length > 0 ? props.entries : defaultEntries
)

const sortedEntries = computed(() => {
  const list = [...activeEntries.value]
  if (!props.alphabetical) return list
  return list.sort((a, b) => {
    const cmp = a.authors.localeCompare(b.authors, 'fr', { sensitivity: 'base' })
    return cmp !== 0 ? cmp : Number(a.year) - Number(b.year)
  })
})

const gridStyle = computed(() => ({
  '--cols': props.columns,
  '--rows': Math.ceil(sortedEntries.value.length / props.columns),
}))

const isVideo = (b) =>
  b.kind?.toLowerCase() === 'vidéo' || b.medium?.toLowerCase() === 'vidéo'

const fullTitle = (b) => (b.subtitle ? `${b.title} : ${b.subtitle}` : b.title)

const shortUrl = (url) => url.replace(/^https?:\/\/(www\.)?/, '')

const details = (b) => {
  const parts = [b.edition, b.translator ? `${b.translator}, trad.` : ''].filter(Boolean)
  const paren = parts.length ? ` (${parts.join(' ; ')})` : ''
  const medium = b.medium ? ` [${b.medium}]` : ''
  return paren + medium
}
</script>

<style scoped>
.apa-biblio {
  --accent: #67e8f9;
  --accent-glow: rgba(103, 232, 249, 0.22);
  --line: rgba(255, 255, 255, 0.1);
  --grid-line: rgba(255, 255, 255, 0.035);

  box-sizing: border-box;
  width: 100%;
  height: 100%;
  padding: 1.75rem clamp(1rem, 3vw, 2.5rem) 2.5rem;
  color: #f8fafc;
  background: #06080d;
  /* Quadrillage subtil en fond */
  background-image:
    linear-gradient(to right, var(--grid-line) 1px, transparent 1px),
    linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
  background-size: 32px 32px;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  overflow-y: auto;
}

/* En-tête */
.biblio-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  padding-bottom: 0.85rem;
  margin-bottom: 1.4rem;
  border-bottom: 1px solid var(--line);
  color: #06080d;
}

.biblio-title {
  margin: 0;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1.5rem;
  font-weight: 400;
  letter-spacing: -0.01em;
}

.biblio-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  color: var(--accent);
  background: rgba(103, 232, 249, 0.08);
  border: 1px solid rgba(103, 232, 249, 0.3);
}

/* Grille stricte de cartes verticales */
.biblio-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .apa-biblio:not(.compact) .biblio-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .apa-biblio:not(.compact) .biblio-grid {
    grid-template-columns: 1fr;
  }
}

/* Carte affiche verticale */
.biblio-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
  border-radius: 14px;
  background: rgba(13, 17, 26, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid var(--line);
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), border-color 0.3s ease, box-shadow 0.3s ease;

  animation: reveal 0.55s cubic-bezier(0.2, 0.7, 0.2, 1) both;
  animation-delay: calc(var(--i) * 80ms);
}

.biblio-card:hover,
.biblio-card:focus-within {
  transform: translateY(-4px);
  border-color: rgba(103, 232, 249, 0.45);
  box-shadow: 0 18px 36px -12px rgba(0, 0, 0, 0.8), 0 0 22px -6px var(--accent-glow);
}

/* Scène de couverture */
.cover-stage {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 245px;
  padding: 1.6rem 1.25rem 1.2rem;
  box-sizing: border-box;
  perspective: 900px;
  background:
    radial-gradient(circle at 50% 60%, rgba(103, 232, 249, 0.16), transparent 68%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.kind-tag {
  position: absolute;
  top: 0.7rem;
  left: 0.7rem;
  z-index: 2;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(6, 8, 13, 0.8);
  border: 1px solid rgba(103, 232, 249, 0.35);
}

/* Objet Livre 3D */
.book-showcase {
  position: relative;
  height: 100%;
  max-height: 195px;
  aspect-ratio: 2 / 2.85;
  border-radius: 3px 7px 7px 3px;
  transform: rotateY(-8deg) rotateX(2deg);
  transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s ease;
  box-shadow:
    -6px 10px 20px rgba(0, 0, 0, 0.75),
    -1px 0 0 rgba(255, 255, 255, 0.22),
    0 0 0 1px rgba(255, 255, 255, 0.08);
  overflow: hidden;
  background: #111827;
}

.book-showcase.landscape-frame {
  height: auto;
  width: 90%;
  max-height: 145px;
  aspect-ratio: 16 / 9;
  border-radius: 8px;
  transform: none;
  box-shadow:
    0 12px 24px rgba(0, 0, 0, 0.75),
    0 0 0 1px rgba(255, 255, 255, 0.14);
}

.biblio-card:hover .book-showcase {
  transform: rotateY(0deg) rotateX(0deg) scale(1.04);
}

.cover-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-sheen {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.22) 0%,
    rgba(0, 0, 0, 0.28) 4%,
    rgba(255, 255, 255, 0.1) 8%,
    transparent 24%
  );
}

.landscape-frame .book-sheen {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, transparent 45%);
}

.cover-fallback {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: linear-gradient(155deg, #1e293b, #090d16);
  color: #e2e8f0;
}

.fb-edition {
  align-self: flex-end;
  font-size: 0.62rem;
  color: var(--accent);
}

.fb-title {
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1.25;
}

.fb-author {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.65);
}

/* Référence APA sous la couverture */
.ref-body {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.1rem 1.15rem;
}

.apa-citation {
  margin: 0;
  padding-left: 1.4em;
  text-indent: -1.4em;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 0.88rem;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.9);
  overflow-wrap: anywhere;
}

.authors {
  font-weight: 600;
  color: #fff;
}

.book-title {
  font-style: italic;
  color: var(--accent);
}

.ref-url {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.ref-note {
  margin: auto 0 0;
  padding-left: 0.65rem;
  font-size: 0.78rem;
  line-height: 1.45;
  color: rgba(255, 255, 255, 0.62);
  border-left: 2px solid rgba(103, 232, 249, 0.45);
}

/* =====================================================================
   Mode compact (slides) : grille de cartes verticales côte à côte
   ===================================================================== */
.apa-biblio.compact {
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  background-color: transparent;
}

.compact .biblio-header {
  flex: none;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
}

.compact .biblio-title {
  font-size: 1.25rem;
}

.compact .biblio-grid {
  flex: 1;
  min-height: 0;
  gap: 0.85rem;
  grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
  grid-template-rows: repeat(var(--rows), minmax(0, 1fr));
}

.compact .biblio-card {
  flex-direction: column;
  min-height: 0;
}

.compact .cover-stage {
  flex: 0 0 52%;
  height: auto;
  padding: 1rem 0.75rem 0.7rem;
}

.compact .book-showcase {
  max-height: 100%;
}

.compact .book-showcase.landscape-frame {
  width: 86%;
  max-height: 85%;
}

.compact .kind-tag {
  top: 0.45rem;
  left: 0.45rem;
  font-size: 0.56rem;
  padding: 0.12rem 0.45rem;
}

.compact .ref-body {
  flex: 1;
  min-height: 0;
  justify-content: space-between;
  gap: 0.4rem;
  padding: 0.65rem 0.8rem 0.75rem;
  overflow: hidden;
}

.compact .apa-citation {
  font-size: 0.74rem;
  line-height: 1.4;
}

.compact .ref-note {
  margin: 0;
  font-size: 0.68rem;
  line-height: 1.35;
}

@keyframes reveal {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .biblio-card { animation: none; }
  .book-showcase { transform: none; }
}
</style>