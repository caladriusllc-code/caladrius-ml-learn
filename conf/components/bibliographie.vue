<template>
  <section class="apa-biblio" aria-label="Bibliographie au format APA">
    <header class="biblio-header">
      <h2 class="biblio-title">{{ title }}</h2>
      <span class="biblio-badge">Norme APA · 7ᵉ éd.</span>
    </header>

    <ul class="biblio-list">
      <li
        v-for="book in sortedEntries"
        :key="book.id"
        class="biblio-card"
      >
        <!-- Couverture de l'ouvrage -->
        <div class="cover-wrap">
          <img
            v-if="book.cover && !brokenCovers[book.id]"
            :src="book.cover"
            :alt="`Couverture de ${book.title}`"
            class="cover-img"
            loading="lazy"
            @error="brokenCovers[book.id] = true"
          />
          <div v-else class="cover-fallback" aria-hidden="true">
            <span class="fb-edition" v-if="book.edition">{{ book.edition }}</span>
            <span class="fb-title">{{ book.title }}</span>
            <span class="fb-author">{{ book.authors }}</span>
          </div>
        </div>

        <!-- Référence formatée selon les règles APA 7 -->
        <div class="ref-body">
          <p class="apa-citation">
            <span class="authors">{{ book.authors }}</span>
            <span class="year"> ({{ book.year }}). </span>
            <em class="book-title">
              {{ book.title }}<template v-if="book.subtitle"> : {{ book.subtitle }}</template>
            </em>
            <template v-if="book.edition || book.translator">
              <span>
                ({{ [book.edition, book.translator ? `${book.translator}, trad.` : ''].filter(Boolean).join(' ; ') }})
              </span>
            </template>
            <span>. </span>
            <span class="publisher">{{ book.publisher }}.</span>
            <a
              v-if="book.url"
              :href="book.url"
              class="ref-url"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ book.url }}
            </a>
          </p>

          <div v-if="book.note" class="ref-note">
            {{ book.note }}
          </div>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { reactive, computed } from 'vue'

/**
 * Tableau d'objets par défaut.
 * Ajoutez simplement de nouveaux objets dans ce tableau (ou passez la prop :entries).
 */
const defaultEntries = [
  {
    id: 'geron-2023',
    authors: 'Géron, A.',
    year: 2023,
    title: 'Deep Learning avec Keras et TensorFlow',
    subtitle: 'Mise en œuvre et cas concrets',
    edition: '3ᵉ éd.',
    translator: 'A. Bohy',
    publisher: 'Dunod',
    cover: '/images.jfif', // Placer images.jfif dans public/ (ou importer l'asset)
    url: '',
    note: 'Référence principale : architectures neuronales, rétropropagation et descente de gradient.',
  },
  {
    id: 'geron-2024',
    authors: 'Allamar, J. & Grootendorst, M',
    year: 2024,
    title: 'Hands-On Large Language Models',
    subtitle: 'language understanding and generation',
    edition: '1ᵉ éd.',
    publisher: 'Dunod',
    cover: '/llm.jfif', // Placer images.jfif dans public/ (ou importer l'asset)
    url: '',
    note: 'Compréhension des concepts relatifs aux LLM',
  },
  // Exemple prêt à décommenter pour ajouter un second ouvrage :
  // {
  //   id: 'goodfellow-2016',
  //   authors: 'Goodfellow, I., Bengio, Y., & Courville, A.',
  //   year: 2016,
  //   title: 'Deep Learning',
  //   subtitle: '',
  //   edition: '',
  //   translator: '',
  //   publisher: 'MIT Press',
  //   cover: '/goodfellow.jpg',
  //   url: 'https://www.deeplearningbook.org',
  //   note: 'Fondements mathématiques de l’apprentissage profond.',
  // },
]

const props = defineProps({
  title: {
    type: String,
    default: 'Références bibliographiques',
  },
  entries: {
    type: Array,
    default: () => [],
  },
  alphabetical: {
    type: Boolean,
    default: true,
  },
})

const brokenCovers = reactive({})

const activeEntries = computed(() =>
  props.entries.length > 0 ? props.entries : defaultEntries
)

// Tri alphabétique conforme à la norme APA (par nom du premier auteur, puis année)
const sortedEntries = computed(() => {
  const list = [...activeEntries.value]
  if (!props.alphabetical) return list
  return list.sort((a, b) => {
    const cmp = a.authors.localeCompare(b.authors, 'fr', { sensitivity: 'base' })
    return cmp !== 0 ? cmp : Number(a.year) - Number(b.year)
  })
})
</script>

<style scoped>
.apa-biblio {
  box-sizing: border-box;
  width: 100%;
  padding: 1.5rem 2rem;
  color: #f8fafc;
  background: #050505;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

.biblio-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.75rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
}

.biblio-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #ffffff;
}

.biblio-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  color: #67e8f9;
  background: rgba(103, 232, 249, 0.1);
  border: 1px solid rgba(103, 232, 249, 0.35);
}

.biblio-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.biblio-card {
  display: grid;
  grid-template-columns: 76px 1fr;
  gap: 1.25rem;
  align-items: center;
  padding: 0.95rem 1.15rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: border-color 0.2s ease, background 0.2s ease;
}

.biblio-card:hover {
  border-color: rgba(103, 232, 249, 0.45);
  background: rgba(255, 255, 255, 0.05);
}

/* Vignette de couverture */
.cover-wrap {
  width: 76px;
  height: 104px;
  border-radius: 5px;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.55);
  flex-shrink: 0;
}

.cover-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-fallback {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  padding: 0.45rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: linear-gradient(155deg, #111827, #090d16);
  color: #e2e8f0;
}

.fb-edition {
  align-self: flex-end;
  font-size: 0.55rem;
  color: #67e8f9;
}

.fb-title {
  font-size: 0.62rem;
  font-weight: 600;
  line-height: 1.2;
}

.fb-author {
  font-size: 0.55rem;
  color: rgba(255, 255, 255, 0.65);
}

/* Typographie APA 7 avec retrait négatif (hanging indent) */
.ref-body {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.apa-citation {
  margin: 0;
  padding-left: 2em;
  text-indent: -2em;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1.02rem;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.92);
}

.authors {
  font-weight: 600;
  color: #ffffff;
}

.book-title {
  font-style: italic;
  color: #67e8f9;
}

.ref-url {
  margin-left: 0.35rem;
  color: #67e8f9;
  text-decoration: underline;
  text-underline-offset: 3px;
  word-break: break-all;
}

.ref-note {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.58);
  padding-left: 0.65rem;
  border-left: 2px solid rgba(103, 232, 249, 0.45);
}
</style>