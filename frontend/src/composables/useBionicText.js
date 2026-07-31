/**
 * Bionic reading: bold the first half of every word so the eye can anchor.
 * Port of `format_text` (legacy/streamlit_app.py:74-82), which emitted Markdown
 * `**bold**`; here we emit <b> directly and escape everything else, so the
 * resulting string is safe to pass to v-html.
 */

const HTML_ESCAPES = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}

export function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => HTML_ESCAPES[char])
}

export function toBionic(text) {
  // Capturing the separator keeps the original whitespace intact.
  return String(text)
    .split(/(\s+)/)
    .map((chunk) => {
      if (!chunk.trim()) return escapeHtml(chunk)
      const mid = Math.max(1, Math.floor(chunk.length / 2))
      return `<b>${escapeHtml(chunk.slice(0, mid))}</b>${escapeHtml(chunk.slice(mid))}`
    })
    .join('')
}
