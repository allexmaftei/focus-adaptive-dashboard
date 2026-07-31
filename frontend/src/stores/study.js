import { ref } from 'vue'
import { defineStore } from 'pinia'

import { api } from '../api/client'

/** Courses, logged sessions and the server-computed analytics. */
export const useStudyStore = defineStore('study', () => {
  const subjects = ref([])
  const sessions = ref([])
  const analytics = ref(null)
  const loading = ref(false)
  const error = ref('')

  /** Run an action, surfacing any API error instead of throwing at the caller. */
  async function run(action) {
    error.value = ''
    try {
      return await action()
    } catch (err) {
      error.value = err.message
      return null
    }
  }

  async function refresh() {
    loading.value = true
    await run(async () => {
      const [nextSubjects, nextSessions, nextAnalytics] = await Promise.all([
        api.listSubjects(),
        api.listSessions(),
        api.summary(),
      ])
      subjects.value = nextSubjects
      sessions.value = nextSessions
      analytics.value = nextAnalytics
    })
    loading.value = false
  }

  const addSubject = (name) =>
    run(async () => {
      const subject = await api.createSubject(name)
      subjects.value = [...subjects.value, subject].sort((a, b) =>
        a.name.localeCompare(b.name),
      )
      return subject
    })

  const removeSubject = (id) =>
    run(async () => {
      await api.deleteSubject(id)
      await refresh() // its sessions cascade away, so the charts change too
    })

  const addSession = (payload) =>
    run(async () => {
      const session = await api.createSession(payload)
      await refresh()
      return session
    })

  const removeSession = (id) =>
    run(async () => {
      await api.deleteSession(id)
      await refresh()
    })

  const importCsv = (file) =>
    run(async () => {
      const result = await api.importCsv(file)
      await refresh()
      return result
    })

  return {
    subjects,
    sessions,
    analytics,
    loading,
    error,
    refresh,
    addSubject,
    removeSubject,
    addSession,
    removeSession,
    importCsv,
  }
})
