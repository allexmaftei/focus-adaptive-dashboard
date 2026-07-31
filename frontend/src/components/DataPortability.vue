<script setup>
import { ref } from 'vue'

import BionicText from './BionicText.vue'
import { api } from '../api/client'
import { useStudyStore } from '../stores/study'

// legacy/streamlit_app.py:250-285. Now a backup feature rather than the only
// way to keep data between visits.
const store = useStudyStore()

const fileInput = ref(null)
const notice = ref('')
const busy = ref(false)

async function onFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return

  notice.value = ''
  busy.value = true
  const result = await store.importCsv(file)
  busy.value = false

  if (result) notice.value = result.message
  // Allow re-selecting the same file after a failed attempt.
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<template>
  <section class="section">
    <h3>💾 3. Keep &amp; Manage Your Data Files</h3>
    <BionicText
      class="muted"
      text="Your sessions are stored in the FocusForge database, but you can still export a copy as a backup or restore one from another machine."
    />

    <div class="grid-2">
      <div class="card">
        <h4>Export</h4>
        <p class="muted">Download every logged session as a CSV.</p>
        <a class="download" :href="api.exportUrl" download>
          📥 Download FocusForge Database (.csv)
        </a>
      </div>

      <div class="card">
        <h4>Restore</h4>
        <p class="muted">
          Replaces all current sessions with the file's contents. Nothing is
          written unless every row is valid.
        </p>
        <label class="field">
          <span>Upload a FocusForge CSV</span>
          <input
            ref="fileInput"
            type="file"
            accept=".csv"
            :disabled="busy"
            @change="onFileChange"
          />
        </label>
        <p v-if="busy" class="muted">Importing…</p>
        <p v-if="notice" class="alert success">{{ notice }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.download {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  background: var(--accent);
  color: var(--accent-contrast);
  font-weight: 600;
  text-decoration: none;
}

h4 {
  margin: 0 0 0.4rem;
}
</style>
