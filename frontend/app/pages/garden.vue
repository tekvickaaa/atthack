<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Application, Assets, Container, Sprite, Graphics, Texture, Text, TextStyle, TilingSprite } from 'pixi.js'


const pixiContainer = ref<HTMLElement | null>(null)
const buildLimit = ref(10)
const selectedType = ref<'house' | 'person' | 'eraser' | 'tree' | 'solar' | 'wind' | 'garden'>('house')

function getCartoonSvg(key: string) {
  let content = ''
  switch(key) {
    case 'ground': content = '<rect width="64" height="64" fill="#8BC34A"/><circle cx="16" cy="16" r="4" fill="#AED581"/><circle cx="48" cy="48" r="6" fill="#AED581"/><circle cx="50" cy="10" r="3" fill="#AED581"/>'; break
    case 'house': content = '<rect x="12" y="24" width="40" height="32" fill="#FFF8E1" stroke="#5D4037" stroke-width="2"/><path d="M8 24 L32 4 L56 24 Z" fill="#E53935" stroke="#B71C1C" stroke-width="2"/><rect x="26" y="36" width="12" height="20" fill="#795548" rx="2"/>'; break
    case 'person': content = '<circle cx="32" cy="20" r="10" fill="#FFCC80"/><path d="M16 60 L16 40 Q16 30 32 30 Q48 30 48 40 L48 60" fill="#2196F3" stroke="#1565C0" stroke-width="2"/>'; break
    case 'tree': content = '<rect x="26" y="40" width="12" height="24" fill="#795548"/><circle cx="32" cy="28" r="20" fill="#4CAF50" stroke="#2E7D32" stroke-width="2"/><circle cx="24" cy="20" r="8" fill="#66BB6A"/>'; break
    case 'solar': content = '<rect x="8" y="20" width="48" height="32" fill="#1565C0" stroke="#0D47A1" stroke-width="2" rx="4"/><line x1="8" y1="36" x2="56" y2="36" stroke="#64B5F6" stroke-width="2"/><line x1="24" y1="20" x2="24" y2="52" stroke="#64B5F6" stroke-width="2"/><line x1="40" y1="20" x2="40" y2="52" stroke="#64B5F6" stroke-width="2"/><rect x="28" y="52" width="8" height="12" fill="#9E9E9E"/>'; break
    case 'wind': content = '<rect x="28" y="32" width="8" height="32" fill="#ECEFF1" stroke="#CFD8DC" stroke-width="2"/><circle cx="32" cy="32" r="4" fill="#455A64"/><path d="M32 32 L32 6" stroke="#ECEFF1" stroke-width="6" stroke-linecap="round"/><path d="M32 32 L54 46" stroke="#ECEFF1" stroke-width="6" stroke-linecap="round"/><path d="M32 32 L10 46" stroke="#ECEFF1" stroke-width="6" stroke-linecap="round"/>'; break
    case 'garden': content = '<rect x="4" y="16" width="56" height="40" fill="#795548" rx="4"/><circle cx="16" cy="24" r="6" fill="#4CAF50"/><circle cx="32" cy="36" r="8" fill="#4CAF50"/><circle cx="48" cy="24" r="6" fill="#4CAF50"/><path d="M32 36 L32 20" stroke="#4CAF50" stroke-width="2"/>'; break
    case 'sheep': content = '<circle cx="32" cy="32" r="18" fill="#FFFFFF" stroke="#E0E0E0" stroke-width="2"/><circle cx="44" cy="28" r="8" fill="#212121"/><rect x="20" y="44" width="6" height="12" fill="#212121"/><rect x="38" y="44" width="6" height="12" fill="#212121"/>'; break
    case 'food': content = '<circle cx="32" cy="36" r="14" fill="#F44336" stroke="#B71C1C" stroke-width="2"/><path d="M32 22 L32 14" stroke="#795548" stroke-width="2"/><path d="M32 22 Q40 14 40 22" fill="#4CAF50"/>'; break
    case 'eraser': content = '<rect x="16" y="16" width="32" height="32" fill="#F48FB1" stroke="#C2185B" stroke-width="2" rx="4"/><rect x="16" y="16" width="12" height="32" fill="#F06292" rx="4"/>'; break
    default: content = '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="24">?</text>';
  }
  return 'data:image/svg+xml;utf8,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">${content}</svg>`)
}

const types = [
  { key: 'house', label: 'House', img: getCartoonSvg('house') },
  { key: 'person', label: 'Person', img: getCartoonSvg('person') },
  { key: 'tree', label: 'Tree', img: getCartoonSvg('tree') },
  { key: 'solar', label: 'Solar', img: getCartoonSvg('solar') },
  { key: 'wind', label: 'Windmill', img: getCartoonSvg('wind') },
  { key: 'garden', label: 'Garden', img: getCartoonSvg('garden') },
  { key: 'sheep', label: 'Sheep', img: getCartoonSvg('sheep') },
  { key: 'food', label: 'Feed', img: getCartoonSvg('food') },
  { key: 'eraser', label: 'Eraser', img: getCartoonSvg('eraser') }
]
const textures = ref<{ [key: string]: string }>({
  ground: getCartoonSvg('ground'),
  house: getCartoonSvg('house'),
  person: getCartoonSvg('person'),
  tree: getCartoonSvg('tree'),
  solar: getCartoonSvg('solar'),
  wind: getCartoonSvg('wind'),
  garden: getCartoonSvg('garden'),
  sheep: getCartoonSvg('sheep'),
  food: getCartoonSvg('food'),
  eraser: getCartoonSvg('eraser')
})

function selectTool(key: string) {
  selectedType.value = key as any
  if (app && app.canvas) {
    if (key === 'eraser') app.canvas.style.cursor = 'crosshair'
    else app.canvas.style.cursor = 'default'
  }
}

let app: Application | null = null
let gardenContainer: Container | null = null
let backgroundSprite: TilingSprite | null = null
let loadedTextures: { [key: string]: Texture | any } = {}
const score = ref(0)
const energy = ref(0)
const envScore = ref(0)
const villageLevel = ref(1)
const xp = ref(0)
const xpToNext = ref(50)
const currentMission = ref({ text: 'Build 3 Houses', type: 'build', target: 'house', count: 3, current: 0, reward: 50 })

// Unified interval tracking (map sprite -> interval id)
const intervals = new Map<Sprite, number>()

// Tooltip when hovering
const hoverLabel = ref<string | null>(null)
const hoverPos = ref({ x: 0, y: 0 })

function spawnFloatingText(x: number, y: number, text: string, color: string) {
  const style = new TextStyle({
    fontFamily: 'Arial',
    fontSize: 24,
    fontWeight: 'bold',
    fill: color,
    stroke: '#ffffff',
    strokeThickness: 4,
  })
  const t = new Text({ text, style })
  t.anchor.set(0.5)
  t.x = x
  t.y = y - 32
  gardenContainer!.addChild(t)

  let tick = 0
  const id = setInterval(() => {
    tick++
    t.y -= 1.5
    t.alpha -= 0.02
    if (tick > 50) {
      clearInterval(id)
      if (gardenContainer) gardenContainer.removeChild(t)
    }
  }, 16)
}

function checkMission(action: string, type?: string, amount: number = 1) {
  if (currentMission.value.type === action) {
    let progress = false
    if (action === 'build' && type === currentMission.value.target) {
      currentMission.value.current += amount
      progress = true
    } else if (action === 'collect' && type === currentMission.value.target) {
      currentMission.value.current += amount
      progress = true
    }

    if (progress && currentMission.value.current >= currentMission.value.count) {
      // Reward
      addXp(currentMission.value.reward)
      spawnFloatingText(app!.screen.width / 2, app!.screen.height / 2, 'MISSION COMPLETE!', '#00FF00')
      
      // Generate new mission
      const missions = [
        // Build Missions
        { text: 'Plant 3 Trees', type: 'build', target: 'tree', count: 3, reward: 40 },
        { text: 'Build 2 Windmills', type: 'build', target: 'wind', count: 2, reward: 60 },
        { text: 'Place 2 Solar Panels', type: 'build', target: 'solar', count: 2, reward: 50 },
        { text: 'Build a Garden', type: 'build', target: 'garden', count: 1, reward: 30 },
        { text: 'Expand Village (3 Houses)', type: 'build', target: 'house', count: 3, reward: 80 },
        { text: 'Plant a Forest (5 Trees)', type: 'build', target: 'tree', count: 5, reward: 100 },
        { text: 'Solar Farm (4 Panels)', type: 'build', target: 'solar', count: 4, reward: 120 },
        
        // Collect Missions
        { text: 'Collect 50 Gold', type: 'collect', target: 'score', count: 50, reward: 40 },
        { text: 'Generate 100 Energy', type: 'collect', target: 'energy', count: 100, reward: 60 },
        { text: 'Restore Nature (30 Env)', type: 'collect', target: 'env', count: 30, reward: 50 },
        { text: 'Stockpile 200 Gold', type: 'collect', target: 'score', count: 200, reward: 150 },
        { text: 'Power Surge (150 Energy)', type: 'collect', target: 'energy', count: 150, reward: 100 },
      ]
      const next = missions[Math.floor(Math.random() * missions.length)]
      currentMission.value = { ...next, current: 0 }
    }
  }
}

function addXp(amount: number) {
  xp.value += amount
  if (xp.value >= xpToNext.value) {
    xp.value -= xpToNext.value
    villageLevel.value++
    xpToNext.value = Math.floor(xpToNext.value * 1.5)
    buildLimit.value += 3
    spawnFloatingText(app!.screen.width / 2, app!.screen.height / 2, 'VILLAGE LEVEL UP!', '#FFD700')
    spawnFloatingText(app!.screen.width / 2, (app!.screen.height / 2) + 40, '+3 BUILDS!', '#FFFFFF')
  }
}

function getSynergyBonus(sprite: Sprite): number {
  let bonus = 0
  const type = sprite['customType']
  const range = 64 // 2 blocks radius

  for (const child of gardenContainer!.children) {
    if (child === sprite || !(child instanceof Sprite)) continue
    const dx = child.x - sprite.x
    const dy = child.y - sprite.y
    const dist = Math.sqrt(dx*dx + dy*dy)
    
    if (dist <= range) {
      const neighbor = child['customType']
      // House loves Nature
      if (type === 'house' && (neighbor === 'tree' || neighbor === 'garden')) {
        bonus += 0.5
      }
      // Solar loves Solar (Efficiency array)
      if (type === 'solar' && neighbor === 'solar') {
        bonus += 0.1
      }
    }
  }
  return bonus
}

function startSpriteInterval(sprite: Sprite) {
  // Clear existing if any
  if (intervals.has(sprite)) {
    clearInterval(intervals.get(sprite)!)
    intervals.delete(sprite)
  }

  const type = sprite['customType']
  const level = sprite['level'] || 1
  const baseMultiplier = Math.pow(1.5, level - 1)

  if (type === 'house') {
    const id = window.setInterval(() => {
      const synergy = getSynergyBonus(sprite)
      const totalMult = baseMultiplier + synergy
      const val = Math.round(1 * totalMult)
      
      score.value += val
      addXp(val)
      checkMission('collect', 'score', val)
      
      const text = synergy > 0 ? `+${val} 🪙 (❤️)` : `+${val} 🪙`
      spawnFloatingText(sprite.x, sprite.y, text, '#FFD700')
    }, 5000)
    intervals.set(sprite, id)
  }
  else if (type === 'person') {
    const id = window.setInterval(() => {
      const dirs = [ [-32,0],[32,0],[0,-32],[0,32] ]
      const choice = dirs[Math.floor(Math.random()*dirs.length)]
      const nx = sprite.x + choice[0]
      const ny = sprite.y + choice[1]
      if (nx < 0 || ny < 0 || nx > app!.renderer.width || ny > app!.renderer.height) return
      for (const child of gardenContainer!.children) {
        if (child instanceof Sprite && child !== sprite && child.x === nx && child.y === ny && (child['customType'] === 'house' || child['customType'] === 'person')) {
          return
        }
      }
      // sprite.x = nx
      // sprite.y = ny
      ;(sprite as any).targetPos = { x: nx, y: ny }
    }, 1500)
    intervals.set(sprite, id)
  }
  else if (type === 'tree') {
    const id = window.setInterval(() => {
      // Growth visual
      if (sprite.scale.x < 1.6) {
         sprite.scale.set(Math.min(1.6, sprite.scale.x + 0.05))
      }
      const val = Math.round(1 * baseMultiplier)
      envScore.value += val
      addXp(val)
      checkMission('collect', 'env', val)
      spawnFloatingText(sprite.x, sprite.y, `+${val} 🌿`, '#4CAF50')
    }, 4000)
    intervals.set(sprite, id)
  }
  else if (type === 'solar') {
    const id = window.setInterval(() => {
      const synergy = getSynergyBonus(sprite)
      const totalMult = baseMultiplier + synergy
      const val = Math.round(2 * totalMult)
      
      energy.value += val
      addXp(val)
      checkMission('collect', 'energy', val)
      
      const text = synergy > 0 ? `+${val} ⚡ (Link)` : `+${val} ⚡`
      spawnFloatingText(sprite.x, sprite.y, text, '#2196F3')
    }, 3000)
    intervals.set(sprite, id)
  }
  else if (type === 'wind') {
    const id = window.setInterval(() => {
      const val = Math.round(3 * baseMultiplier)
      energy.value += val
      addXp(val)
      checkMission('collect', 'energy', val)
      spawnFloatingText(sprite.x, sprite.y, `+${val} ⚡`, '#03A9F4')
    }, 2500)
    intervals.set(sprite, id)
  }
  else if (type === 'garden') {
    const id = window.setInterval(() => {
      const val = Math.round(2 * baseMultiplier)
      envScore.value += val
      addXp(val)
      checkMission('collect', 'env', val)
      spawnFloatingText(sprite.x, sprite.y, `+${val} 🥗`, '#8BC34A')
    }, 4500)
    intervals.set(sprite, id)
  }
  else if (type === 'sheep') {
    sprite['hunger'] = 100
    
    // Hunger Bar Background
    const barBg = new Graphics()
    barBg.beginFill(0x000000)
    barBg.drawRect(-16, -24, 32, 6)
    barBg.endFill()
    sprite.addChild(barBg)
    
    // Hunger Bar Foreground
    const barFg = new Graphics()
    sprite.addChild(barFg)
    
    const id = window.setInterval(() => {
      sprite['hunger'] -= 5
      
      // Update Bar
      barFg.clear()
      const pct = Math.max(0, sprite['hunger'] / 100)
      barFg.beginFill(pct > 0.3 ? 0x00FF00 : 0xFF0000)
      barFg.drawRect(-15, -23, 30 * pct, 4)
      barFg.endFill()
      
      if (sprite['hunger'] <= 0) {
         // Die
         if (intervals.has(sprite)) {
            clearInterval(intervals.get(sprite)!)
            intervals.delete(sprite)
         }
         gardenContainer!.removeChild(sprite)
         spawnFloatingText(sprite.x, sprite.y, '💀 Starved!', '#FF0000')
         return
      }
      
      // Produce Wool if healthy
      if (sprite['hunger'] > 50 && Math.random() > 0.6) {
         const val = Math.round(5 * baseMultiplier)
         score.value += val
         addXp(val)
         checkMission('collect', 'score', val)
         spawnFloatingText(sprite.x, sprite.y, `+${val} 🧶`, '#FFFFFF')
      }
      
      // Wander
      if (Math.random() > 0.4) {
        const dirs = [ [-32,0],[32,0],[0,-32],[0,32] ]
        const choice = dirs[Math.floor(Math.random()*dirs.length)]
        const nx = sprite.x + choice[0]
        const ny = sprite.y + choice[1]
        if (nx >= 0 && ny >= 0 && nx <= app!.renderer.width && ny <= app!.renderer.height) {
           let blocked = false
           for (const child of gardenContainer!.children) {
             if (child instanceof Sprite && child !== sprite && child.x === nx && child.y === ny && (child['customType'] === 'house' || child['customType'] === 'person')) {
               blocked = true; break;
             }
           }
           if (!blocked) {
             // sprite.x = nx
             // sprite.y = ny
             // Use targetPos for smooth movement
             ;(sprite as any).targetPos = { x: nx, y: ny }
           }
        }
      }
    }, 1000)
    intervals.set(sprite, id)
  }
}

function mergeSprites(source: Sprite, target: Sprite) {
  // Upgrade target
  target['level'] = (target['level'] || 1) + 1
  
  // Visual upgrade
  target.tint = 0xFFFF00 // Gold tint
  target.scale.set((target.scale.x || 1) * 1.1)
  
  // Restart interval with new level
  startSpriteInterval(target)
  
  // Remove source
  if (intervals.has(source)) {
    clearInterval(intervals.get(source)!)
    intervals.delete(source)
  }
  gardenContainer!.removeChild(source)
  
  spawnFloatingText(target.x, target.y, 'LEVEL UP!', '#FF00FF')
}

function resizeApp() {
  if (app && pixiContainer.value) {
    const width = pixiContainer.value.offsetWidth
    const height = pixiContainer.value.offsetHeight
    app.renderer.resize(width, height)
    if (backgroundSprite) {
      backgroundSprite.width = width
      backgroundSprite.height = height
    }
  }
}

onMounted(async () => {
  app = new Application()
  // Initialize with window size, will be resized to container immediately
  await app.init({ width: window.innerWidth, height: window.innerHeight, backgroundAlpha: 0 })

  if (pixiContainer.value) {
    pixiContainer.value.appendChild(app.canvas)
    resizeApp()
  }

  gardenContainer = new Container()
  app.stage.addChild(gardenContainer)

  // Create infinite scrolling background
  const groundTexture = await Assets.load(textures.value.ground)
  backgroundSprite = new TilingSprite({
    texture: groundTexture,
    width: app.screen.width,
    height: app.screen.height
  })
  app.stage.addChildAt(backgroundSprite, 0)

  // Game Loop for smooth animations
  app.ticker.add((ticker) => {
    if (!gardenContainer) return
    const delta = ticker.deltaTime
    for (const child of gardenContainer.children) {
      if (child instanceof Sprite) {
        const target = (child as any).targetPos
        if (target && !(child as any).dragging) {
           // Smooth lerp movement (0.1 speed)
           child.x += (target.x - child.x) * 0.1 * delta
           child.y += (target.y - child.y) * 0.1 * delta
           
           // Snap if very close to avoid micro-jitter
           if (Math.abs(target.x - child.x) < 0.1) child.x = target.x
           if (Math.abs(target.y - child.y) < 0.1) child.y = target.y
        }
      }
    }
  })

  // Load image textures (existing assets) and create procedural textures for new elements
  for (const key in textures.value) {
    try {
      loadedTextures[key] = await Assets.load(textures.value[key])
    } catch (err) {
      // ignore — we'll create procedural textures for missing assets
    }
  }

  // Prevent the browser context menu on right-click
  app.view.addEventListener('contextmenu', (ev) => ev.preventDefault())
  app.canvas.style.touchAction = 'none' // Prevent scrolling on mobile

  // Listen for placing new element
  app.canvas.addEventListener('pointerdown', (e) => {
    // Right-click (button === 2) -> delete clicked sprite
    if (e.button === 2) {
      const rect = app!.canvas.getBoundingClientRect()
      const px = e.clientX - rect.left
      const py = e.clientY - rect.top
      // Find top-most sprite at that position and remove (use bounds, not strict equality)
      for (let i = gardenContainer!.children.length - 1; i >= 0; i--) {
        const child = gardenContainer!.children[i]
        if (child instanceof Sprite) {
          if (!child['customType']) continue
          const b = child.getBounds()
          if (px >= b.x && px <= b.x + b.width && py >= b.y && py <= b.y + b.height) {
            if (intervals.has(child)) {
              clearInterval(intervals.get(child))
              intervals.delete(child)
            }
            gardenContainer!.removeChild(child)
            buildLimit.value++
            break
          }
        }
      }
      return
    }

    // Allow using the eraser tool even when build limit is exhausted
    if (buildLimit.value <= 0 && selectedType.value !== 'eraser') return

    const rect = app!.canvas.getBoundingClientRect()
    // raw mouse position (not snapped)
    const rawX = e.clientX - rect.left
    const rawY = e.clientY - rect.top
    // snapped grid position
    let x = Math.round(rawX / 32) * 32
    let y = Math.round(rawY / 32) * 32

    // Check if click is on an existing sprite (use raw coords + snapped fallback)
    let clickedSprite: Sprite | null = null
    for (let i = gardenContainer!.children.length - 1; i >= 0; i--) {
      const child = gardenContainer!.children[i]
      if (!(child instanceof Sprite)) continue
      if (!child['customType']) continue
      const bounds = child.getBounds()
      const insideRaw = rawX >= bounds.x && rawX <= bounds.x + bounds.width && rawY >= bounds.y && rawY <= bounds.y + bounds.height
      const insideSnapped = x >= bounds.x && x <= bounds.x + bounds.width && y >= bounds.y && y <= bounds.y + bounds.height
      if (insideRaw || insideSnapped) {
        clickedSprite = child
        break
      }
    }

    if (clickedSprite) {
      // If eraser tool is selected, delete the clicked sprite immediately
      if (selectedType.value === 'eraser') {
        if (intervals.has(clickedSprite)) {
          clearInterval(intervals.get(clickedSprite)!)
          intervals.delete(clickedSprite)
        }
        gardenContainer!.removeChild(clickedSprite)
        buildLimit.value++
        return
      }

      // If food tool is selected, feed the animal
      if (selectedType.value === 'food') {
        if (clickedSprite['customType'] === 'sheep') {
           if (score.value >= 5) {
               score.value -= 5
               clickedSprite['hunger'] = 100
               spawnFloatingText(clickedSprite.x, clickedSprite.y, 'Yum! 🍎', '#FF69B4')
           } else {
               spawnFloatingText(clickedSprite.x, clickedSprite.y, 'Need 5 🪙!', '#FF0000')
           }
        }
        return
      }

      // Start dragging the sprite
      clickedSprite.cursor = 'grabbing'
      clickedSprite.data = { getLocalPosition: () => ({ x: clickedSprite.x, y: clickedSprite.y }) }
      clickedSprite.dragging = true
      clickedSprite.alpha = 0.7
      // Listen for mousemove and mouseup on window
      const moveHandler = (ev: MouseEvent) => {
        const rect = app!.canvas.getBoundingClientRect()
        let nx = ev.clientX - rect.left
        let ny = ev.clientY - rect.top
        nx = Math.round(nx / 32) * 32
        ny = Math.round(ny / 32) * 32
        clickedSprite!.x = nx
        clickedSprite!.y = ny
      }
      const upHandler = () => {
        clickedSprite!.cursor = 'grab'
        clickedSprite!.dragging = false
        clickedSprite!.data = null
        clickedSprite!.alpha = 1
        
        const finalX = Math.round(clickedSprite!.x / 32) * 32
        const finalY = Math.round(clickedSprite!.y / 32) * 32
        clickedSprite!.x = finalX
        clickedSprite!.y = finalY
        ;(clickedSprite as any).targetPos = { x: finalX, y: finalY }

        // Check for merge
        let merged = false
        for (const child of gardenContainer!.children) {
          if (child === clickedSprite) continue
          if (child instanceof Sprite && child['customType'] === clickedSprite!['customType']) {
             // If dropped exactly on top of another sprite of same type
             if (Math.abs(child.x - finalX) < 5 && Math.abs(child.y - finalY) < 5) {
                 mergeSprites(clickedSprite!, child)
                 merged = true
                 break
             }
          }
        }

        window.removeEventListener('mousemove', moveHandler)
        window.removeEventListener('mouseup', upHandler)
      }
      window.addEventListener('mousemove', moveHandler)
      window.addEventListener('mouseup', upHandler)
      return
    }

    // Collision check before placing
    let overlap = false
    if (selectedType.value === 'ground') {
      // Prevent overlapping ground tiles
      for (const child of gardenContainer!.children) {
        if (
          child instanceof Sprite &&
          child.x === x && child.y === y &&
          child['customType'] === 'ground'
        ) {
          overlap = true
          break
        }
      }
    } else if (selectedType.value === 'house' || selectedType.value === 'person') {
      // Prevent overlapping houses/persons
      for (const child of gardenContainer!.children) {
        if (
          child instanceof Sprite &&
          child.x === x && child.y === y &&
          (child['customType'] === 'house' || child['customType'] === 'person')
        ) {
          overlap = true
          break
        }
      }
    }
    if (overlap) return // Do not place if overlap detected

    if (selectedType.value === 'food') return // Cannot build food

    // Otherwise, spawn a new sprite
    const sprite = new Sprite(loadedTextures[selectedType.value])
    sprite['customType'] = selectedType.value // Mark type for collision
    sprite.anchor.set(0.5)
    sprite.x = x
    sprite.y = y
    ;(sprite as any).targetPos = { x, y } // Initialize target for smooth movement

    sprite.interactive = true
    sprite.cursor = 'grab'
    sprite['level'] = 1

    // Drag and drop logic
    let lastValidX = sprite.x
    let lastValidY = sprite.y
    sprite
      .on('pointerdown', (event) => {
        sprite.cursor = 'grabbing'
        sprite.data = event.data
        sprite.dragging = true
        sprite.alpha = 0.7
        lastValidX = sprite.x
        lastValidY = sprite.y
      })
      .on('pointerup', () => {
        sprite.cursor = 'grab'
        sprite.dragging = false
        sprite.data = null
        sprite.alpha = 1
        sprite.x = Math.round(sprite.x / 32) * 32
        sprite.y = Math.round(sprite.y / 32) * 32
        lastValidX = sprite.x
        lastValidY = sprite.y
      })
      .on('pointerupoutside', () => {
        sprite.cursor = 'grab'
        sprite.dragging = false
        sprite.data = null
        sprite.alpha = 1
        sprite.x = Math.round(sprite.x / 32) * 32
        sprite.y = Math.round(sprite.y / 32) * 32
        lastValidX = sprite.x
        lastValidY = sprite.y
      })
      .on('pointermove', () => {
        if (sprite.dragging) {
          const newPosition = sprite.data.getLocalPosition(gardenContainer)
          const nx = Math.round(newPosition.x / 32) * 32
          const ny = Math.round(newPosition.y / 32) * 32
          let canMove = true
          if (sprite['customType'] === 'ground') {
            // Check if another ground tile exists at target position
            for (const child of gardenContainer!.children) {
              if (
                child instanceof Sprite &&
                child !== sprite &&
                child.x === nx && child.y === ny &&
                child['customType'] === 'ground'
              ) {
                canMove = false
                break
              }
            }
          }
          if (canMove) {
            sprite.x = nx
            sprite.y = ny
            ;(sprite as any).targetPos = { x: nx, y: ny }
            lastValidX = nx
            lastValidY = ny
          } else {
            // Stay at last valid position
            sprite.x = lastValidX
            sprite.y = lastValidY
          }
        }
      })

    if (selectedType.value === 'ground') {
      gardenContainer!.addChildAt(sprite, 0)
    } else {
      gardenContainer!.addChild(sprite)
    }
    
    // Start behaviors
    startSpriteInterval(sprite)
    checkMission('build', selectedType.value)

    buildLimit.value--
  })

  // Responsive resize
  window.addEventListener('resize', () => {
    resizeApp()
  })
})

onBeforeUnmount(() => {
  if (app) {
    app.destroy(true, { children: true })
    app = null
  }
  window.removeEventListener('resize', resizeApp)
  // Clear any running intervals
  for (const id of intervals.values()) clearInterval(id)
  intervals.clear()
})
</script>

<template>
  <div class="relative w-full h-screen overflow-hidden">
    <!-- Pixi Container (Background) -->
    <div ref="pixiContainer" class="absolute inset-0 z-0 touch-none"></div>

    <!-- Top UI Container (Overlay) -->
    <div class="absolute top-0 left-0 w-full z-10 flex flex-col items-center pb-2 pointer-events-none">
      <!-- Toolbar -->
      <div class="flex gap-2 mb-2 pt-2 w-full overflow-x-auto px-4 pb-2 justify-start md:justify-center no-scrollbar pointer-events-auto">
        <button
          v-for="type in types"
          :key="type.key"
          :disabled="(buildLimit <= 0) && type.key !== 'eraser'"
          @click="selectTool(type.key)"
          :class="[
            'rounded shadow border-2 flex flex-col items-center justify-center p-1 tool-button flex-shrink-0',
            selectedType === type.key ? 'border-green-600 bg-green-100 selected-tool' : 'border-green-200 bg-white',
            (buildLimit <= 0) && type.key !== 'eraser' ? 'opacity-50 cursor-not-allowed' : 'hover:border-green-400 hover:bg-green-50'
          ]"
          :title="type.label"
          :aria-pressed="selectedType === type.key"
          style="width: 48px; height: 48px;"
        >
          <img :src="type.img" :alt="type.label" style="width: 32px; height: 32px; object-fit: contain;" />
          <span class="text-[10px] mt-0.5 text-green-800 leading-none">{{ type.label }}</span>
        </button>
      </div>
      
      <!-- Level Progress Bar -->
      <div class="w-full max-w-md mb-2 px-4 pointer-events-auto">
        <div class="flex justify-between text-xs font-bold text-gray-700 mb-1">
          <span>Lvl {{ villageLevel }}</span>
          <span>{{ xp }}/{{ xpToNext }} XP</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3 border border-gray-300">
          <div 
            class="bg-yellow-400 h-full rounded-full transition-all duration-500 ease-out"
            :style="{ width: `${Math.min(100, (xp / xpToNext) * 100)}%` }"
          ></div>
        </div>
      </div>

      <!-- Mission Box -->
      <div class="bg-white/80 backdrop-blur p-2 rounded-lg shadow-lg border-l-4 border-blue-500 mb-2 flex flex-col items-start animate-pulse w-[90%] max-w-md pointer-events-auto">
        <span class="text-[10px] font-bold text-blue-600 uppercase tracking-wider">Mission</span>
        <span class="font-bold text-sm text-gray-800">{{ currentMission.text }}</span>
        <div class="w-full bg-gray-200 h-1.5 rounded-full mt-1">
          <div class="bg-blue-500 h-full rounded-full transition-all" :style="{ width: `${(currentMission.current / currentMission.count) * 100}%` }"></div>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-4 gap-2 text-xs font-bold w-full max-w-md px-4 mb-2 text-center pointer-events-auto">
        <div class="text-green-700 bg-green-50 rounded p-1">Builds: {{ buildLimit }}</div>
        <div class="text-yellow-700 bg-yellow-50 rounded p-1">🪙 {{ score }}</div>
        <div class="text-blue-700 bg-blue-50 rounded p-1">⚡ {{ energy }}</div>
        <div class="text-green-800 bg-green-100 rounded p-1">🌿 {{ envScore }}</div>
      </div>

      <div class="mb-1 text-green-500 text-[10px] text-center px-4 pointer-events-auto">Tip: Merge items to Level Up!</div>
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>