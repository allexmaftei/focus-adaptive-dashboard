<script setup>
import { reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'

import BionicText from './BionicText.vue'
import { useStudyStore } from '../stores/study'

// legacy/streamlit_app.py:116-140. Input ranges match the backend BOUNDS table.
const store = useStudyStore()
const { subjects } = storeToRefs(store)

const today = () => new Date().toISOString().slice(0, 10)

const defaults = () => ({
  subject_id: subjects.value[0]?.id ?? null,
  date: today(),
  hour: 15,
  duration_min: 30,
  distractions: 2,
  focus_rating: 4,
})

const form = reactive(defaults())
const notice = ref('')

// The first load arrives after mount, so adopt a default course when it does.
watch(subjects, (list) => {
  if (form.subject_id === null && list.length) form.subject_id = list[0].id
})

async function submit() {
  if (form.subject_id === null) return

  const created = await store.addSession({ ...form })
  if (created) {
    notice.value = 'Session data successfully saved!'
    Object.assign(form, defaults(), { subject_id: form.subject_id })
  } else {
    notice.value = ''
  }
}
</script>

<template>
  <section class="card">
    <h3>✏️ 2. Log a Study Session</h3>
    <BionicText
      class="muted"
      text="When you finish a study sprint, record your focus variables to log the raw telemetry data."
    />

    <form @submit.prevent="submit">
      <label class="field">
        <span>Subject</span>
        <select v-model.number="form.subject_id" :disabled="!subjects.length">
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
      </label>

      <label class="field">
        <span>Date</span>
        <input v-model="form.date" type="date" required />
      </label>

      <label class="field">
        <span>Time of day (hour starting): {{ form.hour }}:00</span>
        <input v-model.number="form.hour" type="range" min="0" max="23" step="1" />
      </label>

      <label class="field">
        <span>Session duration (minutes)</span>
        <input
          v-model.number="form.duration_min"
          type="number"
          min="5"
          max="240"
          step="5"
          required
        />
      </label>

      <label class="field">
        <span>Distraction count (clicks away / tab changes)</span>
        <input
          v-model.number="form.distractions"
          type="number"
          min="0"
          max="50"
          required
        />
      </label>

      <label class="field">
        <span>
          Focus level: {{ form.focus_rating }} / 5
          <em class="muted">(1 = scattered, 5 = hyperfocus)</em>
        </span>
        <input v-model.number="form.focus_rating" type="range" min="1" max="5" step="1" />
      </label>

      <button type="submit" :disabled="!subjects.length">Submit Data Entry</button>
      <p v-if="!subjects.length" class="muted">Add a course first.</p>
    </form>

    <p v-if="notice" class="alert success">{{ notice }}</p>
  </section>
</template>
