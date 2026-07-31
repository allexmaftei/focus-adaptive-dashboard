<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import PlotlyChart from '../PlotlyChart.vue'
import { useAccessibilityStore } from '../../stores/accessibility'
import { subjectColorMap } from '../../theme/palettes'

// Total minutes per course — legacy/streamlit_app.py:213-221, where the values
// were never actually summed. The API aggregates them now.
const props = defineProps({
  rows: { type: Array, default: () => [] },
})

const { palette } = storeToRefs(useAccessibilityStore())

const data = computed(() => {
  const colors = subjectColorMap(
    props.rows.map((row) => row.subject),
    palette.value,
  )
  return [
    {
      type: 'bar',
      x: props.rows.map((row) => row.subject),
      y: props.rows.map((row) => row.duration_min),
      marker: { color: props.rows.map((row) => colors[row.subject]) },
      hovertemplate: '%{x}<br>%{y} minutes total<extra></extra>',
    },
  ]
})

const layout = {
  title: { text: 'Total Combined Minutes Studied' },
  yaxis: { title: { text: 'Minutes' } },
  xaxis: { title: { text: 'Course' } },
  showlegend: false,
}
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" />
</template>
