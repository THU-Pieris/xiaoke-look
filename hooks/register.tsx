import type { Register, ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'
import { PAPER, SCENE } from './scene'

// Claude-chan, afternoon: warm cream paper, dark-brown ink, her orange as the accent.
// The backdrop is made for a light room, so the look is light only.
const { theme, problems } = makeColors({
  label: 'Claude娘 · 午后',
  only: 'light',
  roles: { accent: '#c8561f', danger: '#b3392f', success: '#5a7d3a', warning: '#a86f14', pro: '#7a4f8a' },
  light: {
    gray: {
      anchors: {
        'surface-0': PAPER as `#${string}`,
        'surface-1': '#f6eee2',
        'surface-2': '#faf5ec',
        'text-primary': '#2b1c15',
        'text-secondary': '#553e31',
        'text-muted': '#6b5545',
      },
    },
  },
})

const SCENE_NAME = 'afternoon'

const LOOK: ThemeSetArgs = {
  colors: theme,
  backdrop: { scene: SCENE_NAME, glass: { blur: 18, tint: '#f6eee2', opacity: 0.62 } },
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))

    if (unpainted !== undefined) {
      $.ui.toast(unpainted)
    }
    const set = await $.theme.set(LOOK)

    if (!set.isDrawn) {
      $.ui.status(set.reason)
    }

    return next(e)
  })

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    if (e.props.scene !== SCENE_NAME || (e.surface !== 'desktop' && e.surface !== 'mobile')) {
      return next(e)
    }
    const { Svg } = $.ui.resolve(e)

    return (
      <Svg
        source={SCENE}
        alt="Claude-chan reading by a sunny window, the picture fading into blank paper"
        isInteractive
      />
    )
  })
}
