<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import PlotlyChart from '../PlotlyChart.vue'
import { useAccessibilityStore } from '../../stores/accessibility'
import { subjectColorMap } from '../../theme/palettes'

// Distractions vs perceived focus, bubble size = session length.
// legacy/streamlit_app.py:226-235.
const props = defineProps({
  rows: { type: Array, default: () => [] },
})

const { palette } = storeToRefs(useAccessibilityStore())

const MAX_MARKER_PX = 34

const data = computed(() => {
  const rows = props.rows
  if (!rows.length) return []

  const colors = subjectColorMap(
    rows.map((row) => row.subject),
    palette.value,
  )
  // Plotly's area sizing needs an explicit reference, otherwise bubbles from a
  // short-session dataset render huge.
  const maxDuration = Math.max(...rows.map((row) => row.duration_min), 1)
  const sizeref = (2 * maxDuration) / MAX_MARKER_PX ** 2

  // One trace per course so colour maps to a legend entry.
  return [...new Set(rows.map((row) => row.subject))].sort().map((subject) => {
    const subset = rows.filter((row) => row.subject === subject)
    return {
      type: 'scatter',
      mode: 'markers',
      name: subject,
      x: subset.map((row) => row.distractions),
      y: subset.map((row) => row.focus_rating),
      marker: {
        color: colors[subject],
        size: subset.map((row) => row.duration_min),
        sizemode: 'area',
        sizeref,
        sizemin: 5,
        opacity: 0.8,
        line: { width: 1, color: 'rgba(255,255,255,0.85)' },
      },
      customdata: subset.map((row) => row.duration_min),
      hovertemplate:
        `${subject}<br>%{x} distractions<br>Focus %{y} / 5` +
        '<br>%{customdata} min<extra></extra>',
    }
  })
})

const layout = {
  title: { text: 'The Impact of Distraction Events on Perceived Focus' },
  xaxis: { title: { text: 'Distraction events' } },
  yaxis: { title: { text: 'Focus rating' }, range: [0, 5.5] },
  legend: { orientation: 'h', y: -0.25 },
  margin: { l: 55, r: 20, t: 50, b: 80 },
}
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" />
</template>
