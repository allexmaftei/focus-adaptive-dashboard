<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
// The basic bundle carries the scatter/bar traces every chart here uses, at
// roughly a third of the full plotly.js-dist-min payload.
import Plotly from 'plotly.js-basic-dist-min'

import { useAccessibilityStore } from '../stores/accessibility'

const props = defineProps({
  data: { type: Array, required: true },
  layout: { type: Object, default: () => ({}) },
})

const { adhdMode } = storeToRefs(useAccessibilityStore())

const container = ref(null)
let resizeObserver = null

const FONT_STACK =
  "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
const CONFIG = { displayModeBar: false, responsive: true }

function baseLayout() {
  return {
    margin: { l: 55, r: 20, t: 50, b: 55 },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    // Chart text scales with ADHD mode, same as the rest of the page.
    font: { family: FONT_STACK, size: adhdMode.value ? 15 : 12 },
    title: { font: { size: adhdMode.value ? 19 : 16 } },
    hoverlabel: { font: { family: FONT_STACK } },
  }
}

function render() {
  if (!container.value) return
  const layout = { ...baseLayout(), ...props.layout }
  // react() diffs against the current figure, so updates don't rebuild the DOM.
  Plotly.react(container.value, props.data, layout, CONFIG)
}

onMounted(() => {
  render()
  resizeObserver = new ResizeObserver(() => {
    if (container.value) Plotly.Plots.resize(container.value)
  })
  resizeObserver.observe(container.value)
})

watch(() => [props.data, props.layout, adhdMode.value], render, { deep: true })

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  if (container.value) Plotly.purge(container.value)
})
</script>

<template>
  <div ref="container" class="plot" />
</template>
