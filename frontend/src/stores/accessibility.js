import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

import {
  COLORBLIND_PALETTE,
  SEQUENTIAL_COLORBLIND,
  SEQUENTIAL_STANDARD,
  STANDARD_PALETTE,
} from '../theme/palettes'

const STORAGE_KEY = 'focusforge.accessibility'

function loadPreferences() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}
  } catch {
    return {}
  }
}

/**
 * The two toggles from legacy/streamlit_app.py:40-41, but persisted so a reload
 * doesn't reset the student's setup.
 */
export const useAccessibilityStore = defineStore('accessibility', () => {
  const saved = loadPreferences()
  const adhdMode = ref(Boolean(saved.adhdMode))
  const colorblindMode = ref(Boolean(saved.colorblindMode))

  const palette = computed(() =>
    colorblindMode.value ? COLORBLIND_PALETTE : STANDARD_PALETTE,
  )
  const sequential = computed(() =>
    colorblindMode.value ? SEQUENTIAL_COLORBLIND : SEQUENTIAL_STANDARD,
  )

  watch(
    [adhdMode, colorblindMode],
    () => {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          adhdMode: adhdMode.value,
          colorblindMode: colorblindMode.value,
        }),
      )
      // Drives the typography/colour overrides in styles/adhd.css.
      document.body.classList.toggle('adhd-mode', adhdMode.value)
    },
    { immediate: true },
  )

  return { adhdMode, colorblindMode, palette, sequential }
})
