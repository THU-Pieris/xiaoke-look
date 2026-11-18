import type { ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'
import * as afternoon from './scenes/afternoon'
import * as code from './scenes/code'
import * as night from './scenes/night'
import * as rain from './scenes/rain'
import * as snow from './scenes/snow'

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
  scene: { PAPER: string; SCENE: string }
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
    args: { colors: theme, backdrop: { scene: spec.id, glass: spec.glass } },
    ...(unpainted === undefined ? {} : { unpainted }),
  }
}

export const LOOKS: Record<string, Look> = Object.fromEntries(SPECS.map(spec => [spec.id, build(spec)]))

export const DEFAULT_LOOK = 'afternoon'

export function findLook(name: string): Look | undefined {
  const key = name.trim().toLowerCase()

  return Object.values(LOOKS).find(look => look.id === key || look.aliases.includes(key) || look.title.includes(key))
}

export function lookArgs(look: Look): ThemeSetArgs {
  return look.args
}
