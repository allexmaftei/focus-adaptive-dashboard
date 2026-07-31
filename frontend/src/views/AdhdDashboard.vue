<script setup>
import FocusSprintTimer from '../components/FocusSprintTimer.vue'
import FocusBySubjectChart from '../components/charts/FocusBySubjectChart.vue'

// legacy/streamlit_app.py:151-188.
defineProps({
  analytics: { type: Object, default: null },
})
</script>

<template>
  <section class="section">
    <h2>🧠 ADHD Minimalist Study Lounge</h2>
    <p class="alert info">
      Reduced clutter mode active. Multi-column metric walls and competitive
      graphs are hidden — one timer, one chart.
    </p>

    <div class="grid-2">
      <FocusSprintTimer />

      <div class="card">
        <h3>📊 Your Core Focus Windows</h3>
        <FocusBySubjectChart :rows="analytics?.focus_by_subject || []" />
      </div>
    </div>
  </section>
</template>
