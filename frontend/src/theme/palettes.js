/** Chart palettes, ported from legacy/streamlit_app.py:44-51. */

/** Okabe-Ito universal barrier-free palette. */
export const COLORBLIND_PALETTE = [
  '#0072B2',
  '#E69F00',
  '#009E73',
  '#F0E442',
  '#CC79A7',
  '#56B4E9',
  '#D55E00',
]

/** Standard high-vibrancy palette. */
export const STANDARD_PALETTE = [
  '#FF4B4B',
  '#1F77B4',
  '#2CA02C',
  '#9467BD',
  '#FF7F0E',
  '#17BECF',
  '#E377C2',
]

export const SEQUENTIAL_COLORBLIND = 'Viridis'
export const SEQUENTIAL_STANDARD = 'Oranges'

/**
 * Assign a stable colour per course, so a subject keeps the same colour across
 * every chart regardless of the order the API happened to return.
 */
export function subjectColorMap(subjectNames, palette) {
  const map = {}
  ;[...new Set(subjectNames)].sort().forEach((name, index) => {
    map[name] = palette[index % palette.length]
  })
  return map
}
