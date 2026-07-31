<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import PlotlyChart from '../PlotlyChart.vue'
import { useAccessibilityStore } from '../../stores/accessibility'
import { subjectColorMap } from '../../theme/palettes'

// Mean focus per course — legacy/streamlit_app.py:178-188.
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
      y: props.rows.map((row) => row.focus_rating),
      marker: { color: props.rows.map((row) => colors[row.subject]) },
      hovertemplate: '%{x}<br>Average focus: %{y} / 5<extra></extra>',
    },
  ]
})

const layout = {
  title: { text: 'Focus Rating by Course (Simplified View)' },
  yaxis: { title: { text: 'Average focus' }, range: [0, 5.5] },
  xaxis: { title: { text: 'Course' } },
  showlegend: false,
}
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" />
</template>
