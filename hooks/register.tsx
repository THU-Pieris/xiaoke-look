import type { Register } from 'claude-code'

import { DEFAULT_LOOK, LOOKS, findLook, lookArgs } from './looks'

// Xiaoke looks: one illustrated scene per look, switched with /xiaoke and
// remembered across sessions in this mod's store.
const LOOK_KEY = 'look'
// How far (CSS px) the picture keeps clear of the right edge, for a side panel
// that is open there: the app draws its side panels opaque over the backdrop.
const INSET_KEY = 'inset'
const PANEL_WIDTH = 320
const PIC_TAG = '<svg class="pic" x="0" '

async function storedInset(get: (key: string) => Promise<unknown>): Promise<number> {
  const value = await get(INSET_KEY)

  return typeof value === 'number' && Number.isFinite(value) ? value : 0
}

function listText(current: string, inset: number): string {
  const rows = Object.values(LOOKS).map(look => {
    const mark = look.id === current ? '●' : '○'

    return `${mark} ${look.id.padEnd(10)} ${look.title}（${look.mode === 'dark' ? '深色' : '浅色'}）`
  })

  return [
    '小克主题：',
    ...rows,
    '',
    '用 /xiaoke <名字> 切换，例如 /xiaoke night',
    `右侧栏让位：${inset > 0 ? `${inset}px` : '关'}（/xiaoke 右栏 开关，/xiaoke 右栏 <像素> 设宽度）`,
  ].join('\n')
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'xiaoke',
      description: '切换小克主题：afternoon / night / code / rain / snow；/xiaoke 右栏 让插画避开右侧栏',
    })
    const stored = await $.store.get(LOOK_KEY)
    const look = findLook(typeof stored === 'string' ? stored : DEFAULT_LOOK) ?? LOOKS[DEFAULT_LOOK]!

    if (look.unpainted !== undefined) {
      $.ui.toast(look.unpainted)
    }
    const set = await $.theme.set(lookArgs(look))

    if (!set.isDrawn) {
      $.ui.status(set.reason)
    }

    return next(e)
  })

  on('command.run', { command: 'xiaoke' }, async ($, e) => {
    const stored = await $.store.get(LOOK_KEY)
    const current = findLook(typeof stored === 'string' ? stored : DEFAULT_LOOK) ?? LOOKS[DEFAULT_LOOK]!
    const inset = await storedInset(key => $.store.get(key))
    const [word = '', amount] = e.args.trim().split(/\s+/)

    if (word === '') {
      return { text: listText(current.id, inset) }
    }
    if (word === '右栏' || word === '侧栏' || word === 'panel' || word === 'inset') {
      let width = inset > 0 ? 0 : PANEL_WIDTH

      if (amount !== undefined) {
        const px = Number(amount)

        if (!Number.isFinite(px) || px < 0 || px > 1200) {
          return { text: `「${amount}」不是 0 到 1200 之间的像素数。` }
        }
        width = Math.round(px)
      }
      await $.store.set(INSET_KEY, width)
      // A set of the same look draws the backdrop again with the new inset.
      await $.theme.set(lookArgs(current))

      return {
        text: width > 0 ? `插画现在给右侧栏让出 ${width}px。` : '插画不再给右侧栏让位，贴着窗口右边。',
      }
    }
    const look = findLook(word)

    if (look === undefined) {
      return { text: `没有叫「${word}」的主题。\n\n${listText(current.id, inset)}` }
    }
    await $.store.set(LOOK_KEY, look.id)
    const set = await $.theme.set(lookArgs(look))

    if (!set.isDrawn) {
      return { text: `已记住「${look.title}」，但这里不显示主题：${set.reason}` }
    }

    return { text: `已换成「${look.title}」。之后新开的会话也会用它。` }
  })

  on('ui.render', { component: 'Backdrop' }, async ($, e, next) => {
    const look = LOOKS[e.props.scene]

    if (look === undefined || (e.surface !== 'desktop' && e.surface !== 'mobile')) {
      return next(e)
    }
    const { Svg } = $.ui.resolve(e)
    // Phones have no side panel.
    const inset = e.surface === 'desktop' ? await storedInset(key => $.store.get(key)) : 0
    const source = inset > 0 ? look.scene.replace(PIC_TAG, `<svg class="pic" x="-${inset}" `) : look.scene

    return <Svg source={source} alt={look.alt} isInteractive />
  })
}
