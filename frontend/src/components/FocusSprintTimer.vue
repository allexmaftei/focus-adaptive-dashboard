<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'

import BionicText from './BionicText.vue'

/**
 * A real countdown. The Streamlit version (legacy/streamlit_app.py:165-173)
 * blocked the script for 100 × 10ms, so a "25 minute" sprint finished in about
 * a second and froze the whole page while it ran.
 */
const minutes = ref(25)
const remaining = ref(minutes.value * 60)
const running = ref(false)
const finished = ref(false)

let intervalId = null
let deadline = 0

const total = computed(() => minutes.value * 60)
const percent = computed(() =>
  total.value ? Math.min(100, ((total.value - remaining.value) / total.value) * 100) : 0,
)
const display = computed(() => {
  const mins = Math.floor(remaining.value / 60)
  const secs = remaining.value % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

function clear() {
  if (intervalId !== null) {
    clearInterval(intervalId)
    intervalId = null
  }
}

// Recomputed from a deadline rather than decremented, so a throttled background
// tab doesn't make the timer drift.
function secondsLeft() {
  return Math.max(0, Math.round((deadline - Date.now()) / 1000))
}

function tick() {
  remaining.value = secondsLeft()
  if (remaining.value === 0) {
    clear()
    running.value = false
    finished.value = true
  }
}

function start() {
  if (running.value) return
  if (remaining.value <= 0) remaining.value = total.value
  deadline = Date.now() + remaining.value * 1000
  running.value = true
  finished.value = false
  intervalId = setInterval(tick, 250)
}

function pause() {
  if (!running.value) return
  clear()
  remaining.value = secondsLeft()
  running.value = false
}

function reset() {
  clear()
  running.value = false
  finished.value = false
  remaining.value = total.value
}

// Changing the length while idle re-arms the clock.
watch(minutes, () => {
  if (!running.value) reset()
})

onBeforeUnmount(clear)
</script>

<template>
  <section class="card">
    <h3>⏱️ Quick Focus Sprint Timer</h3>
    <BionicText
      class="muted"
      text="Use this to block external visual distractions. Run a study sprint right inside your workspace."
    />

    <label class="field">
      <span>Sprint duration (minutes)</span>
      <input
        v-model.number="minutes"
        type="number"
        min="1"
        max="120"
        :disabled="running"
      />
    </label>

    <p class="clock" role="timer" :aria-label="`${display} remaining`">{{ display }}</p>
    <div class="track"><div class="fill" :style="{ width: `${percent}%` }" /></div>

    <div class="actions">
      <button v-if="!running" type="button" @click="start">
        {{ remaining < total && remaining > 0 ? 'Resume' : 'Activate Focus Block' }}
      </button>
      <button v-else type="button" @click="pause">Pause</button>
      <button class="secondary" type="button" @click="reset">Reset</button>
    </div>

    <p v-if="running" class="alert info">Focus mode locked. {{ display }} to go.</p>
    <p v-else-if="finished" class="alert success">
      🎉 Excellent study block! Time to stretch.
    </p>
  </section>
</template>

<style scoped>
.clock {
  font-size: 3rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--accent);
  margin: 0.5rem 0;
}

.track {
  height: 10px;
  border-radius: 999px;
  background: var(--border);
  overflow: hidden;
}

.fill {
  height: 100%;
  background: var(--accent);
  transition: width 0.25s linear;
}

.actions {
  display: flex;
  gap: 0.6rem;
  margin: 1rem 0;
}
</style>
