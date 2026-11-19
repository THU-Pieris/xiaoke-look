// Which look `/xiaoke auto` shows at a given moment: one slot per part of the
// day, filled by season, and varied by day so the same slot is not always the
// same picture. Northern-hemisphere seasons.

export type Slot = 'morning' | 'day' | 'dusk' | 'evening' | 'late'

export const SLOT_NAMES: Record<Slot, string> = {
  morning: '清晨',
  day: '白天',
  dusk: '黄昏',
  evening: '夜晚',
  late: '深夜',
}

export type Moment = {
  hour: number
  minute: number
  month: number // 1-12
  date: number // 1-31
  dayNumber: number // days since the epoch, local
}

export function localMoment(ms: number, offsetMinutes: number): Moment {
  const local = new Date(ms + offsetMinutes * 60_000)

  return {
    hour: local.getUTCHours(),
    minute: local.getUTCMinutes(),
    month: local.getUTCMonth() + 1,
    date: local.getUTCDate(),
    dayNumber: Math.floor((ms + offsetMinutes * 60_000) / 86_400_000),
  }
}

export function slotOf(hour: number): Slot {
  if (hour >= 5 && hour < 9) {
    return 'morning'
  }
  if (hour >= 9 && hour < 16) {
    return 'day'
  }
  if (hour >= 16 && hour < 19) {
    return 'dusk'
  }
  if (hour >= 19 && hour < 23) {
    return 'evening'
  }

  return 'late'
}

function isHolidays(m: Moment): boolean {
  return (m.month === 12 && m.date >= 20) || (m.month === 1 && m.date <= 6)
}

function seasonOf(month: number): 'spring' | 'summer' | 'autumn' | 'winter' {
  if (month >= 3 && month <= 5) {
    return 'spring'
  }
  if (month >= 6 && month <= 8) {
    return 'summer'
  }
  if (month >= 9 && month <= 11) {
    return 'autumn'
  }

  return 'winter'
}

const pick = <T>(list: readonly T[], day: number): T => list[((day % list.length) + list.length) % list.length]!

// Candidate looks for a moment, best first; the caller takes the first one it has.
export function candidates(m: Moment): string[] {
  const slot = slotOf(m.hour)
  const season = seasonOf(m.month)
  // The day of a late-night slot is the evening it began on.
  const day = slot === 'late' && m.hour < 5 ? m.dayNumber - 1 : m.dayNumber

  switch (slot) {
    case 'morning':
      return ['morning', 'afternoon']
    case 'day': {
      const seasonal = { spring: 'spring', summer: undefined, autumn: 'autumn', winter: 'snow' }[season]
      const everyday = pick(['afternoon', 'cafe', 'rain'], Math.floor(day / 2))
      // Every other day the season's own picture, when it has one.
      const first = seasonal !== undefined && day % 2 === 0 ? seasonal : everyday

      return [first, everyday, 'afternoon']
    }
    case 'dusk':
      return ['dusk', 'afternoon']
    case 'evening':
      if (isHolidays(m)) {
        return ['holiday', 'night']
      }
      if (season === 'summer' && day % 2 === 0) {
        return ['festival', 'night']
      }

      return ['night']
    case 'late':
      return [pick(['code', 'detective'], day), 'code']
  }
}

export function autoLookId(m: Moment, has: (id: string) => boolean): string {
  return candidates(m).find(has) ?? 'afternoon'
}

// "+8", "-5", "+5:30", "UTC+8" -> minutes east of UTC.
export function parseOffset(text: string): number | undefined {
  const match = /^(?:utc|gmt)?([+-])(\d{1,2})(?::?(\d{2}))?$/i.exec(text.trim())

  if (match === null) {
    return undefined
  }
  const minutes = Number(match[2]) * 60 + Number(match[3] ?? 0)

  if (minutes > 14 * 60) {
    return undefined
  }

  return match[1] === '-' ? -minutes : minutes
}

export function formatOffset(minutes: number): string {
  const sign = minutes < 0 ? '-' : '+'
  const abs = Math.abs(minutes)
  const mm = abs % 60

  return `UTC${sign}${Math.floor(abs / 60)}${mm === 0 ? '' : `:${String(mm).padStart(2, '0')}`}`
}
