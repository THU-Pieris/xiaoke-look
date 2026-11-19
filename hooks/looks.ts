import type { ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'
import * as afternoon from './scenes/afternoon'
import * as autumn from './scenes/autumn'
import * as cafe from './scenes/cafe'
import * as code from './scenes/code'
import * as detective from './scenes/detective'
import * as dusk from './scenes/dusk'
import * as festival from './scenes/festival'
import * as holiday from './scenes/holiday'
import * as morning from './scenes/morning'
import * as night from './scenes/night'
import * as rain from './scenes/rain'
import * as snow from './scenes/snow'
import * as spring from './scenes/spring'

type Hex = `#${string}`

type Anchors = {
  'surface-0': Hex
  'surface-1': Hex
  'surface-2': Hex
  'surface-3'?: Hex
  'text-primary': Hex
  'text-secondary': Hex
  'text-muted': Hex
}

type Spec = {
  id: string
  title: string
  aliases: string[]
  mode: 'light' | 'dark'
  alt: string
  scene: { PAPER: string; SCENE: string; SIDE: string; FACE: { x: number; y: number }; ASPECT: number }
  roles: { accent: Hex; danger: Hex; success: Hex; warning: Hex; pro: Hex }
  anchors: Omit<Anchors, 'surface-0'>
  glass: { blur: number; tint: string; opacity: number }
}

export type Look = {
  id: string
  title: string
  aliases: string[]
  mode: 'light' | 'dark'
  alt: string
  scene: string
  // The edge the picture is pinned to, where its face is (fractions of the
  // picture), and the picture's height over its width.
  side: 'left' | 'right'
  face: { x: number; y: number }
  aspect: number
  args: ThemeSetArgs
  unpainted?: string
}

const SPECS: Spec[] = [
  {
    id: 'afternoon',
    title: '午后·窗边读书',
    aliases: ['午后', 'day', 'read'],
    mode: 'light',
    alt: 'Claude-chan reading by a sunny window, the picture fading into blank paper',
    scene: afternoon,
    roles: { accent: '#c8561f', danger: '#b3392f', success: '#5a7d3a', warning: '#a86f14', pro: '#7a4f8a' },
    anchors: {
      'surface-1': '#f6eee2',
      'surface-2': '#faf5ec',
      'text-primary': '#2b1c15',
      'text-secondary': '#553e31',
      'text-muted': '#6b5545',
    },
    glass: { blur: 14, tint: '#f6eee2', opacity: 0.42 },
  },
  {
    id: 'night',
    title: '夜读·台灯',
    aliases: ['夜读', 'lamp'],
    mode: 'dark',
    alt: 'Claude-chan writing in a notebook under a desk lamp at night, fading into dark paper',
    scene: night,
    roles: { accent: '#e0823f', danger: '#e06a5c', success: '#8fbf7a', warning: '#e3b25a', pro: '#b79be0' },
    anchors: {
      'surface-1': '#25203a',
      'surface-2': '#2b2641',
      'surface-3': '#2f2a46',
      'text-primary': '#f1eadf',
      'text-secondary': '#cfc6bb',
      'text-muted': '#aba3a0',
    },
    glass: { blur: 14, tint: '#231e37', opacity: 0.42 },
  },
  {
    id: 'code',
    title: '深夜·敲代码',
    aliases: ['敲代码', 'debug', 'midnight'],
    mode: 'dark',
    alt: 'Claude-chan frowning at a bug in the glow of a monitor late at night, fading into dark paper',
    scene: code,
    roles: { accent: '#e8874a', danger: '#e2675e', success: '#7fc48f', warning: '#e0b45c', pro: '#9fb3f0' },
    anchors: {
      'surface-1': '#19212d',
      'surface-2': '#1e2633',
      'surface-3': '#222a38',
      'text-primary': '#e8edf3',
      'text-secondary': '#c3cbd6',
      'text-muted': '#9aa4b2',
    },
    glass: { blur: 14, tint: '#18202b', opacity: 0.42 },
  },
  {
    id: 'rain',
    title: '雨天·窗边茶',
    aliases: ['雨天', 'tea'],
    mode: 'light',
    alt: 'Claude-chan holding a cup of tea and watching the rain, fading into grey-blue paper',
    scene: rain,
    roles: { accent: '#c25a2c', danger: '#b23a35', success: '#4f7d5b', warning: '#9c6c17', pro: '#5b5f9e' },
    anchors: {
      'surface-1': '#e3e9ef',
      'surface-2': '#edf1f5',
      'text-primary': '#1d2128',
      'text-secondary': '#3f4651',
      'text-muted': '#525a66',
    },
    glass: { blur: 14, tint: '#e3e9ef', opacity: 0.42 },
  },
  {
    id: 'snow',
    title: '冬日·初雪',
    aliases: ['冬日', '落雪', 'winter'],
    mode: 'light',
    alt: 'Claude-chan catching the first snowflake on her glove, fading into snow-white paper',
    scene: snow,
    roles: { accent: '#c8561f', danger: '#b3392f', success: '#4b7a5a', warning: '#9a6b12', pro: '#5e5a9c' },
    anchors: {
      'surface-1': '#eef3f8',
      'surface-2': '#f5f8fb',
      'text-primary': '#1f2228',
      'text-secondary': '#454953',
      'text-muted': '#575c67',
    },
    glass: { blur: 14, tint: '#eef3f8', opacity: 0.42 },
  },
  {
    id: 'morning',
    title: '清晨·睡衣早餐',
    aliases: ['清晨', '早餐', '早上', 'breakfast'],
    mode: 'light',
    alt: 'Claude-chan in pajamas, half awake, biting into toast in the morning sun, fading into blank paper',
    scene: morning,
    roles: { accent: '#c8561f', danger: '#b3392f', success: '#5a7d3a', warning: '#a86f14', pro: '#4f6ea0' },
    anchors: {
      'surface-1': '#f7efe7',
      'surface-2': '#fbf6f1',
      'text-primary': '#2b1d16',
      'text-secondary': '#55402f',
      'text-muted': '#6a5546',
    },
    glass: { blur: 14, tint: '#f7efe7', opacity: 0.42 },
  },
  {
    id: 'cafe',
    title: '咖啡店·打工',
    aliases: ['咖啡', '咖啡店', '打工', 'coffee', 'latte'],
    mode: 'light',
    alt: 'Claude-chan in an apron pouring latte art behind a cafe counter, fading into cream paper',
    scene: cafe,
    roles: { accent: '#b8561f', danger: '#a8352d', success: '#577a38', warning: '#9c6812', pro: '#7a4f6a' },
    anchors: {
      'surface-1': '#f4e8dd',
      'surface-2': '#f9f2eb',
      'text-primary': '#2a1b14',
      'text-secondary': '#533a2c',
      'text-muted': '#664d3e',
    },
    glass: { blur: 14, tint: '#f4e8dd', opacity: 0.42 },
  },
  {
    id: 'dusk',
    title: '黄昏·放学',
    aliases: ['黄昏', '放学', '制服', 'sunset', 'school'],
    mode: 'light',
    alt: 'Claude-chan in a sailor uniform leaning on a rooftop railing at sunset, fading into peach paper',
    scene: dusk,
    roles: { accent: '#bf4a1c', danger: '#a5302c', success: '#4f7536', warning: '#96600e', pro: '#6d4b8a' },
    anchors: {
      'surface-1': '#f7dfd0',
      'surface-2': '#fae9de',
      'text-primary': '#2c1a1f',
      'text-secondary': '#56383f',
      'text-muted': '#664850',
    },
    glass: { blur: 14, tint: '#f7dfd0', opacity: 0.42 },
  },
  {
    id: 'detective',
    title: '深夜·侦探推理',
    aliases: ['侦探', '推理', 'sherlock', 'mystery'],
    mode: 'dark',
    alt: 'Claude-chan in a detective coat finding the bug with a magnifying glass on a corkboard of printouts, fading into dark paper',
    scene: detective,
    roles: { accent: '#e8874a', danger: '#e2675e', success: '#86c39a', warning: '#e0b45c', pro: '#a8b4e8' },
    anchors: {
      'surface-1': '#212935',
      'surface-2': '#262e3b',
      'surface-3': '#29323f',
      'text-primary': '#e9ece8',
      'text-secondary': '#c6cbc4',
      'text-muted': '#9ea69f',
    },
    glass: { blur: 14, tint: '#1f2733', opacity: 0.42 },
  },
  {
    id: 'spring',
    title: '春日·樱花',
    aliases: ['春', '春日', '樱花', 'sakura'],
    mode: 'light',
    alt: 'Claude-chan in a cardigan under a cherry tree, petals blowing past, fading into blank paper',
    scene: spring,
    roles: { accent: '#c8561f', danger: '#b3392f', success: '#557d3c', warning: '#a86f14', pro: '#9a4f7a' },
    anchors: {
      'surface-1': '#f8eee8',
      'surface-2': '#fbf5f1',
      'text-primary': '#2e1f22',
      'text-secondary': '#5a4246',
      'text-muted': '#6e575b',
    },
    glass: { blur: 14, tint: '#f8eee8', opacity: 0.42 },
  },
  {
    id: 'festival',
    title: '夏夜·烟花祭',
    aliases: ['夏', '夏夜', '烟花', '浴衣', 'summer', 'fireworks'],
    mode: 'dark',
    alt: 'Claude-chan in a yukata with a candied apple looking up at fireworks over a festival, fading into night paper',
    scene: festival,
    roles: { accent: '#ec8a48', danger: '#e86a5e', success: '#8cc48a', warning: '#e8b85a', pro: '#b49be6' },
    anchors: {
      'surface-1': '#1f2440',
      'surface-2': '#242a47',
      'surface-3': '#282e4c',
      'text-primary': '#eef0f7',
      'text-secondary': '#c9cde0',
      'text-muted': '#a2a8c0',
    },
    glass: { blur: 14, tint: '#1e233e', opacity: 0.42 },
  },
  {
    id: 'autumn',
    title: '秋日·红叶',
    aliases: ['秋', '秋日', '红叶', 'fall', 'maple'],
    mode: 'light',
    alt: 'Claude-chan in a scarf sipping hot cider on a bench under red maples, fading into blank paper',
    scene: autumn,
    roles: { accent: '#c24e1e', danger: '#a8322a', success: '#5b7a34', warning: '#a2690f', pro: '#7a4f7a' },
    anchors: {
      'surface-1': '#f6ebe1',
      'surface-2': '#faf3ec',
      'text-primary': '#2d1a12',
      'text-secondary': '#57392b',
      'text-muted': '#6c5040',
    },
    glass: { blur: 14, tint: '#f6ebe1', opacity: 0.42 },
  },
  {
    id: 'holiday',
    title: '圣诞·新年',
    aliases: ['圣诞', '新年', 'christmas', 'xmas'],
    mode: 'dark',
    alt: 'Claude-chan in a red capelet hanging an ornament on a lit Christmas tree, fading into dark paper',
    scene: holiday,
    roles: { accent: '#ec8a48', danger: '#ec6a5e', success: '#8cc48a', warning: '#e8b85a', pro: '#c79be0' },
    anchors: {
      'surface-1': '#31222a',
      'surface-2': '#37272f',
      'surface-3': '#3a2a32',
      'text-primary': '#f3e9e4',
      'text-secondary': '#d4c4c0',
      'text-muted': '#b0a19f',
    },
    glass: { blur: 14, tint: '#2f2128', opacity: 0.42 },
  },
]

// The order /xiaoke lists them in: through the day, then the seasons.
const ORDER = [
  'morning', 'afternoon', 'cafe', 'rain', 'dusk', 'night', 'code', 'detective',
  'spring', 'festival', 'autumn', 'snow', 'holiday',
]

function build(spec: Spec): Look {
  const half = { gray: { anchors: { 'surface-0': spec.scene.PAPER as Hex, ...spec.anchors } } }
  const { theme, problems } = makeColors({
    label: `小克 · ${spec.title}`,
    only: spec.mode,
    roles: spec.roles,
    ...(spec.mode === 'light' ? { light: half } : { dark: half }),
  })
  const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))

  return {
    id: spec.id,
    title: spec.title,
    aliases: spec.aliases,
    mode: spec.mode,
    alt: spec.alt,
    scene: spec.scene.SCENE,
    side: spec.scene.SIDE === 'left' ? 'left' : 'right',
    face: spec.scene.FACE,
    aspect: spec.scene.ASPECT,
    args: { colors: theme, backdrop: { scene: spec.id, glass: spec.glass } },
    ...(unpainted === undefined ? {} : { unpainted }),
  }
}

const rank = (id: string) => ORDER.indexOf(id)

export const LOOKS: Record<string, Look> = Object.fromEntries(
  [...SPECS].sort((a, b) => rank(a.id) - rank(b.id)).map(spec => [spec.id, build(spec)]),
)

export const DEFAULT_LOOK = 'afternoon'

export function findLook(name: string): Look | undefined {
  const key = name.trim().toLowerCase()

  return Object.values(LOOKS).find(look => look.id === key || look.aliases.includes(key) || look.title.includes(key))
}

export const DEFAULT_VEIL = 0.42

// The look's theme with the conversation's veil at `veil` (0 clear to 1 solid);
// a clear veil drops the blur too, so nothing is laid over the picture.
export function lookArgs(look: Look, veil = DEFAULT_VEIL): ThemeSetArgs {
  const backdrop = look.args.backdrop

  if (backdrop === undefined || !('scene' in backdrop) || backdrop.scene === undefined || backdrop.glass === false) {
    return look.args
  }

  return {
    ...look.args,
    backdrop: { ...backdrop, glass: { ...backdrop.glass, opacity: veil, blur: veil === 0 ? 0 : (backdrop.glass?.blur ?? 14) } },
  }
}

// Where the conversation sits: side panels open on the left and right, and the
// width the app keeps the transcript column at, all in CSS px.
export type Layout = { left: number; right: number }
const TRANSCRIPT = 760
// Keep the face this far inside a gap's edge.
const MARGIN = 100

const n = (value: number) => Number(value.toFixed(3))

// A CSS translateX for the picture's group that puts the face in the middle of
// the gap between the transcript column and the side panel on the picture's
// side. The window's size is only known to the scene itself, so this is a
// calc() over vw and vh; the picture is laid out at min(100vh, aspect * 100vw)
// tall.
export function faceShift(look: Look, layout: Layout): string {
  const { left: L, right: R } = layout
  const tall = `min(100vh, ${n(look.aspect * 100)}vw)`

  if (look.side === 'right') {
    // gap centre = (transcript right + panel left) / 2 = 75vw + (L - 3R + T) / 4
    const c = n((L - 3 * R + TRANSCRIPT) / 4)
    const k = n((1 - look.face.x) / look.aspect)

    return `translateX(calc(min(-25vw + ${c}px, ${-R - MARGIN}px) + ${k} * ${tall}))`
  }
  // gap centre = (panel right + transcript left) / 2 = 25vw + (3L - R - T) / 4
  const c = n((3 * L - R - TRANSCRIPT) / 4)
  const k = n(look.face.x / look.aspect)

  return `translateX(calc(max(25vw + ${c}px, ${L + MARGIN}px) - ${k} * ${tall}))`
}
