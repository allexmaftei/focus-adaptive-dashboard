<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import { useAccessibilityStore } from '../stores/accessibility'
import { escapeHtml, toBionic } from '../composables/useBionicText'

const props = defineProps({
  text: { type: String, required: true },
  tag: { type: String, default: 'p' },
})

const { adhdMode } = storeToRefs(useAccessibilityStore())

// Both branches escape the input, so the only markup ever injected is our <b>.
const html = computed(() =>
  adhdMode.value ? toBionic(props.text) : escapeHtml(props.text),
)
</script>

<template>
  <component :is="tag" class="bionic" v-html="html" />
</template>
