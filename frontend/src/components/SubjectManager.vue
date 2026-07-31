<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'

import BionicText from './BionicText.vue'
import { useStudyStore } from '../stores/study'

// legacy/streamlit_app.py:94-110, plus removal, which the prototype lacked.
const store = useStudyStore()
const { subjects } = storeToRefs(store)

const newSubject = ref('')
const notice = ref('')

async function submit() {
  const name = newSubject.value.trim()
  if (!name) return

  const created = await store.addSubject(name)
  if (created) {
    notice.value = `Added ${created.name} to your program!`
    newSubject.value = ''
  } else {
    notice.value = ''
  }
}

async function remove(subject) {
  const warning = subject.session_count
    ? `Delete ${subject.name}? Its ${subject.session_count} logged session(s) will be removed too.`
    : `Delete ${subject.name}?`
  if (!window.confirm(warning)) return

  notice.value = ''
  await store.removeSubject(subject.id)
}
</script>

<template>
  <section class="card">
    <h3>📚 1. Manage Your Subjects</h3>
    <BionicText
      class="muted"
      text="Add your academic courses below to customise your metrics telemetry."
    />

    <form @submit.prevent="submit">
      <label class="field">
        <span>Add a new course name</span>
        <input
          v-model="newSubject"
          type="text"
          placeholder="e.g. Biology, Calculus"
          maxlength="80"
        />
      </label>
      <button type="submit" :disabled="!newSubject.trim()">
        Add Course to Database
      </button>
    </form>

    <p v-if="notice" class="alert success">{{ notice }}</p>

    <p v-if="!subjects.length" class="muted">No courses yet.</p>
    <ul v-else class="chip-list">
      <li v-for="subject in subjects" :key="subject.id" class="chip">
        {{ subject.name }}
        <span class="muted count">({{ subject.session_count }})</span>
        <button
          class="link-danger"
          type="button"
          :aria-label="`Delete ${subject.name}`"
          @click="remove(subject)"
        >
          ✕
        </button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.count {
  font-size: 0.85em;
}
</style>
