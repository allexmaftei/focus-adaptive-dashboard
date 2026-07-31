<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import PlotlyChart from '../PlotlyChart.vue'
import { useAccessibilityStore } from '../../stores/accessibility'

// Mean focus by hour of day, on the sequential scale that the colourblind
// toggle swaps — legacy/streamlit_app.py:239-248.
const props = defineProps({
  rows: { type: Array, default: () => [] },
})

const { sequential } = storeToRefs(useAccessibilityStore())

const data = computed(() => [
  {
    type: 'bar',
    x: props.rows.map((row) => row.hour),
    y: props.rows.map((row) => row.focus_rating),
    marker: {
      color: props.rows.map((row) => row.focus_rating),
      colorscale: sequential.value,
      cmin: 0,
      cmax: 5,
      colorbar: { title: { text: 'Focus' }, thickness: 14 },
    },
    hovertemplate: '%{x}:00<br>Average focus: %{y} / 5<extra></extra>',
  },
])

const layout = computed(() => ({
  title: { text: 'Identifying Peak Daily Focus Windows (Highest Average Rating)' },
  xaxis: {
    title: { text: 'Hour of day' },
    dtick: 1,
    range: [-0.5, 23.5],
  },
  yaxis: { title: { text: 'Average focus' }, range: [0, 5.5] },
}))
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" />
</template>
