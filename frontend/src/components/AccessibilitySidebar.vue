<script setup>
import { storeToRefs } from 'pinia'

import { useAccessibilityStore } from '../stores/accessibility'

// legacy/streamlit_app.py:36-41, now persisted across reloads.
const { adhdMode, colorblindMode } = storeToRefs(useAccessibilityStore())
</script>

<template>
  <aside class="sidebar">
    <h2>♿ Accessibility</h2>
    <p class="muted">Customise your layout workflow:</p>

    <label class="toggle">
      <input v-model="adhdMode" type="checkbox" />
      <span>🧠 ADHD Focus Mode</span>
    </label>
    <p class="muted small">
      Switches to a low-friction layout with a sprint timer, larger type and
      bionic reading.
    </p>

    <label class="toggle">
      <input v-model="colorblindMode" type="checkbox" />
      <span>👁️ Colourblind Safe Mode</span>
    </label>
    <p class="muted small">
      Repaints every chart in the Okabe–Ito barrier-free palette.
    </p>

    <hr />
    <p class="muted small">Your settings are saved in this browser.</p>
  </aside>
</template>

<style scoped>
.small {
  font-size: 0.85em;
  margin: -0.4rem 0 1.2rem;
}
</style>
