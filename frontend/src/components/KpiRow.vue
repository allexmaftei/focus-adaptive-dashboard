<script setup>
import { computed } from 'vue'

// legacy/streamlit_app.py:199-205.
const props = defineProps({
  kpis: { type: Object, default: null },
})

const cards = computed(() => {
  const kpis = props.kpis || {
    total_hours: 0,
    avg_distractions: 0,
    avg_focus: 0,
  }
  return [
    { label: 'Total Study Investment', value: `${kpis.total_hours} Hours` },
    {
      label: 'Average Distraction Frequency',
      value: `${kpis.avg_distractions} per Session`,
    },
    { label: 'Overall Focus Accuracy', value: `${kpis.avg_focus} / 5.0` },
  ]
})
</script>

<template>
  <div class="grid-3">
    <div v-for="card in cards" :key="card.label" class="card kpi">
      <span class="muted">{{ card.label }}</span>
      <strong>{{ card.value }}</strong>
    </div>
  </div>
</template>

<style scoped>
.kpi {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.kpi strong {
  font-size: 1.7em;
  line-height: 1.2;
  color: var(--accent);
}
</style>
