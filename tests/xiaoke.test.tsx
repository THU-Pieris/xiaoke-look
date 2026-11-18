import type { On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

type SetCall = { backdrop?: { scene?: string } }

// Hooks that stand for the engine: command registry, theme, store.
function engine(on: On, sets: SetCall[]) {
  on('command.register', () => ({ value: { command: 'xiaoke' } }))
  on('theme.set', (_, e) => {
    sets.push(e as SetCall)

    return { value: { isDrawn: true, requestId: 'backdrop' } }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  const kept = new Map<string, unknown>()
  on('store.get', (_, e) => ({ value: kept.get((e as { key: string }).key) }))
  on('store.set', (_, e) => {
    const { key, value } = e as { key: string; value: unknown }
    kept.set(key, value)

    return { value: undefined }
  })

  return kept
}

const typed = (args: string) => ({
  command: 'xiaoke',
  args,
  origin: { kind: 'composer' as const },
  presentation: { isFullscreen: false, columns: 80 },
})

test('starts with the afternoon look, switches and remembers', async ($, on) => {
  const sets: SetCall[] = []
  const kept = engine(on, sets)

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(sets.at(-1)?.backdrop?.scene).toBe('afternoon')

  const listed = await $.command.run(typed(''))
  expect(listed.text).toContain('● afternoon')
  expect(listed.text).toContain('night')

  const switched = await $.command.run(typed('夜读'))
  expect(switched.text).toContain('夜读·台灯')
  expect(sets.at(-1)?.backdrop?.scene).toBe('night')
  expect(kept.get('look')).toBe('night')

  const unknown = await $.command.run(typed('beach'))
  expect(unknown.text).toContain('没有叫')

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(sets.at(-1)?.backdrop?.scene).toBe('night')
})

const backdrop = (scene: string) =>
  ({
    plugin: 'xiaoke-look',
    component: 'Backdrop',
    requestId: 'backdrop',
    surface: 'desktop',
    props: { scene, plugin: 'xiaoke-look', glass: { blur: 14, opacity: 0.42 } },
  }) as const

test('every look draws its own scene on the desktop', async ($, on) => {
  engine(on, [])
  for (const scene of ['afternoon', 'night', 'code', 'rain', 'snow']) {
    const ui = await $.ui.mount(backdrop(scene))
    const svg = await ui.find({ type: 'Svg' })
    expect(svg).toBeDefined()
    expect(JSON.stringify(svg)).toContain('class=\\"pic\\" x=\\"0\\"')
    await ui.unmount()
  }
})

test('the right-panel inset moves the picture left and toggles off', async ($, on) => {
  const sets: SetCall[] = []
  const kept = engine(on, sets)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const on1 = await $.command.run(typed('右栏'))
  expect(on1.text).toContain('320px')
  expect(kept.get('inset')).toBe(320)
  const ui = await $.ui.mount(backdrop('afternoon'))
  expect(JSON.stringify(await ui.find({ type: 'Svg' }))).toContain('x=\\"-320\\"')
  await ui.unmount()

  const custom = await $.command.run(typed('panel 280'))
  expect(custom.text).toContain('280px')
  expect(kept.get('inset')).toBe(280)

  const off = await $.command.run(typed('右栏'))
  expect(off.text).toContain('不再')
  expect(kept.get('inset')).toBe(0)

  const bad = await $.command.run(typed('右栏 abc'))
  expect(bad.text).toContain('不是')
})
