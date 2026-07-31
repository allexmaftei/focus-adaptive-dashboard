<script setup>
import KpiRow from '../components/KpiRow.vue'
import DurationBySubjectChart from '../components/charts/DurationBySubjectChart.vue'
import FocusByHourChart from '../components/charts/FocusByHourChart.vue'
import FrictionScatterChart from '../components/charts/FrictionScatterChart.vue'

// legacy/streamlit_app.py:190-248.
defineProps({
  analytics: { type: Object, default: null },
})
</script>

<template>
  <section class="section">
    <h2>📊 Deep Telemetry Metrics Dashboard</h2>

    <KpiRow :kpis="analytics?.kpis" />

    <div class="grid-2 charts">
      <div class="card">
        <h3>⏱️ Total Time Distribution</h3>
        <DurationBySubjectChart :rows="analytics?.duration_by_subject || []" />
      </div>
      <div class="card">
        <h3>⚡ Attention Friction Analysis</h3>
        <FrictionScatterChart :rows="analytics?.friction_scatter || []" />
      </div>
    </div>

    <div class="card">
      <h3>🕒 Cognitive Window Time Analysis</h3>
      <FocusByHourChart :rows="analytics?.focus_by_hour || []" />
    </div>
  </section>
</template>

<style scoped>
.charts {
  margin: 1.25rem 0;
}
</style>
