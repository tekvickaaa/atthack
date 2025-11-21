export interface SpriteData {
  id: string
  type: string
  x: number
  y: number
  level: number
  state: 'IDLE' | 'PRODUCING' | 'READY' | 'DIRTY' | 'HUNGRY'
  productionStartTime?: number // timestamp when production started
  lastCollectTime?: number // timestamp of last collection
  hunger?: number // for animals
  happiness?: number // bonus from petting
}

export interface GameState {
  sprites: SpriteData[]
  gold: number
  env: number
  energy: number
  villageLevel: number
  xp: number
  xpToNext: number
  buildLimit: number
  lastSaveTime: number
}

const STORAGE_KEY = 'garden-game-state'

// Production durations in milliseconds
export const PRODUCTION_TIMES = {
  sheep: 2 * 60 * 60 * 1000, // 2 hours
  cow: 3 * 60 * 60 * 1000, // 3 hours
  chicken: 1 * 60 * 60 * 1000, // 1 hour
  pig: 2.5 * 60 * 60 * 1000, // 2.5 hours
  garden: 4 * 60 * 60 * 1000, // 4 hours
} as const

// Production rewards
export const PRODUCTION_REWARDS = {
  sheep: { gold: 15, xp: 5, icon: '🧶' },
  cow: { gold: 20, xp: 7, icon: '🥛' },
  chicken: { gold: 8, xp: 2, icon: '🥚' },
  pig: { gold: 18, xp: 6, icon: '🥓' },
  garden: { gold: 10, xp: 3, icon: '🥬' },
} as const

export const useGameState = () => {
  const defaultState = (): GameState => ({
    sprites: [],
    gold: 0,
    env: 0,
    energy: 0,
    villageLevel: 1,
    xp: 0,
    xpToNext: 50,
    buildLimit: 10,
    lastSaveTime: Date.now(),
  })

  const loadState = (): GameState => {
    if (typeof window === 'undefined') return defaultState()
    
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return defaultState()
    
    try {
      const state = JSON.parse(saved) as GameState
      
      // Calculate offline production
      const now = Date.now()
      const offlineTime = now - state.lastSaveTime
      
      console.log(`Offline for ${Math.floor(offlineTime / 1000 / 60)} minutes`)
      
      // Process each sprite's production during offline time
      state.sprites = state.sprites.map(sprite => {
        if (sprite.state === 'PRODUCING' && sprite.productionStartTime) {
          const productionDuration = PRODUCTION_TIMES[sprite.type as keyof typeof PRODUCTION_TIMES]
          if (productionDuration) {
            const elapsed = now - sprite.productionStartTime
            if (elapsed >= productionDuration) {
              // Production completed while offline
              return { ...sprite, state: 'READY' as const }
            }
          }
        }
        
        // Handle hunger decay for animals
        if (sprite.type === 'sheep' && sprite.hunger !== undefined) {
          const hoursPassed = offlineTime / (60 * 60 * 1000)
          const hungerLoss = Math.floor(hoursPassed * 5) // 5 hunger per hour
          sprite.hunger = Math.max(0, sprite.hunger - hungerLoss)
          
          if (sprite.hunger <= 0) {
            // Animal would have died - mark as HUNGRY instead of removing
            sprite.state = 'HUNGRY'
          }
        }
        
        return sprite
      })
      
      return state
    } catch (err) {
      console.error('Failed to load game state:', err)
      return defaultState()
    }
  }

  const saveState = (state: GameState) => {
    if (typeof window === 'undefined') return
    
    state.lastSaveTime = Date.now()
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  }

  const clearState = () => {
    if (typeof window === 'undefined') return
    localStorage.removeItem(STORAGE_KEY)
  }

  return {
    loadState,
    saveState,
    clearState,
    defaultState,
  }
}
