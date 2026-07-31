<script setup>
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'

import AccessibilitySidebar from './components/AccessibilitySidebar.vue'
import BionicText from './components/BionicText.vue'
import DataPortability from './components/DataPortability.vue'
import SessionLogForm from './components/SessionLogForm.vue'
import SubjectManager from './components/SubjectManager.vue'
import AdhdDashboard from './views/AdhdDashboard.vue'
import StandardDashboard from './views/StandardDashboard.vue'
import { useAccessibilityStore } from './stores/accessibility'
import { useStudyStore } from './stores/study'

const study = useStudyStore()
const { analytics, loading, error } = storeToRefs(study)
const { adhdMode } = storeToRefs(useAccessibilityStore())

// The same two-branch layout switch as legacy/streamlit_app.py:151/190.
const dashboard = computed(() => (adhdMode.value ? AdhdDashboard : StandardDashboard))

const hasSessions = computed(() => (analytics.value?.kpis.session_count ?? 0) > 0)

onMounted(study.refresh)
</script>

<template>
  <div class="app">
    <AccessibilitySidebar />

    <main class="main">
      <header class="section">
        <h1>🎯 FocusForge</h1>
        <BionicText
          class="muted"
          text="An adaptive workspace analysing cognitive performance data to help high schoolers learn how they work best."
        />
      </header>

      <p v-if="error" class="alert error" role="alert">{{ error }}</p>

      <div class="grid-2 section">
        <SubjectManager />
        <SessionLogForm />
      </div>

      <hr />

      <p v-if="loading && !analytics" class="muted">Loading your telemetry…</p>
      <p v-else-if="!hasSessions" class="alert info">
        No sessions logged yet. Add one above, or restore a CSV below, and the
        charts will fill in.
      </p>
      <component :is="dashboard" v-else :analytics="analytics" />

      <hr />

      <DataPortability />
    </main>
  </div>
</template>
