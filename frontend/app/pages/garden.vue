<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { Application, Assets, Container, Sprite, Graphics, Texture, Text, TextStyle, TilingSprite } from 'pixi.js'
import { useGameState, type SpriteData, PRODUCTION_TIMES, PRODUCTION_REWARDS } from '~/composables/useGameState'
import { useCredit } from '~/composables/useCredit'


const pixiContainer = ref<HTMLElement | null>(null)
const { credits, fetchCredits, subtractCredits } = useCredit()
const { loadState, saveState } = useGameState()
const gameState = ref(loadState())

const buildLimit = computed(() => gameState.value.buildLimit)
const maxHouses = computed(() => Math.floor(credits.value / 100))
const selectedType = ref<string>('house')
const showShop = ref(false)
const showRedemptionShop = ref(false)
const showEcoShop = ref(false)
const showDebugPanel = ref(false)
const petTargetSprite = ref<Sprite | null>(null)
const petHoldStart = ref(0)

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
    case 'cow': content = '<ellipse cx="32" cy="36" rx="20" ry="16" fill="#FFFFFF" stroke="#212121" stroke-width="2"/><ellipse cx="28" cy="32" rx="8" ry="10" fill="#212121"/><ellipse cx="40" cy="32" rx="8" ry="10" fill="#212121"/><circle cx="32" cy="20" r="12" fill="#FFFFFF" stroke="#212121" stroke-width="2"/><rect x="20" y="48" width="6" height="12" fill="#212121"/><rect x="38" y="48" width="6" height="12" fill="#212121"/>'; break
    case 'chicken': content = '<ellipse cx="32" cy="36" rx="14" ry="16" fill="#FFFFFF" stroke="#FF9800" stroke-width="2"/><circle cx="32" cy="22" r="10" fill="#FFFFFF" stroke="#FF9800" stroke-width="2"/><path d="M28 22 L22 18 L28 18 Z" fill="#F44336"/><circle cx="28" cy="20" r="2" fill="#212121"/><circle cx="36" cy="20" r="2" fill="#212121"/><path d="M32 24 L28 26 L32 26 Z" fill="#FF9800"/>'; break
    case 'pig': content = '<ellipse cx="32" cy="36" rx="18" ry="14" fill="#FFC0CB" stroke="#FF69B4" stroke-width="2"/><circle cx="32" cy="22" r="11" fill="#FFC0CB" stroke="#FF69B4" stroke-width="2"/><circle cx="32" cy="24" r="6" fill="#FFB6C1"/><circle cx="28" cy="24" r="2" fill="#8B4513"/><circle cx="36" cy="24" r="2" fill="#8B4513"/><rect x="22" y="46" width="5" height="10" fill="#FF69B4"/><rect x="37" y="46" width="5" height="10" fill="#FF69B4"/>'; break
    case 'fence': content = '<rect x="8" y="8" width="48" height="48" fill="none" stroke="#8B4513" stroke-width="4"/><rect x="12" y="12" width="40" height="40" fill="none" stroke="#A0522D" stroke-width="2"/>'; break
    case 'food': content = '<circle cx="32" cy="36" r="14" fill="#F44336" stroke="#B71C1C" stroke-width="2"/><path d="M32 22 L32 14" stroke="#795548" stroke-width="2"/><path d="M32 22 Q40 14 40 22" fill="#4CAF50"/>'; break
    case 'eraser': content = '<rect x="16" y="16" width="32" height="32" fill="#F48FB1" stroke="#C2185B" stroke-width="2" rx="4"/><rect x="16" y="16" width="12" height="32" fill="#F06292" rx="4"/>'; break
    case 'broom': content = '<rect x="26" y="8" width="12" height="36" fill="#795548" rx="2"/><path d="M20 44 L20 56 L44 56 L44 44 Z" fill="#FFD54F" stroke="#F57C00" stroke-width="2"/><line x1="20" y1="44" x2="44" y2="44" stroke="#F57C00" stroke-width="2"/>'; break
    case 'pet': content = '<circle cx="32" cy="32" r="20" fill="#FF69B4" stroke="#C2185B" stroke-width="2"/><path d="M22 28 Q22 24 26 24 Q28 24 28 28" fill="#8B0000"/><path d="M36 28 Q36 24 40 24 Q42 24 42 28" fill="#8B0000"/><path d="M20 36 Q32 44 44 36" fill="none" stroke="#8B0000" stroke-width="3" stroke-linecap="round"/>'; break
    default: content = '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="24">?</text>';
  }
  return 'data:image/svg+xml;utf8,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">${content}</svg>`)
}

// Define costs for each decoration type (in credits)
const decorationCosts: { [key: string]: number } = {
  house: 0,      // Houses don't cost credits
  person: 0,     // People don't cost credits
  fence: 5,
  tree: 10,
  solar: 20,
  wind: 25,
  garden: 15,
  sheep: 30,
  cow: 40,
  chicken: 20,
  pig: 35,
  food: 0,       // Tools don't cost credits
  broom: 0,
  pet: 0,
  eraser: 0
}

const types = [
  { key: 'house', label: 'House', img: getCartoonSvg('house'), cost: 0 },
  { key: 'person', label: 'Person', img: getCartoonSvg('person'), cost: 0 },
  { key: 'fence', label: 'Fence', img: getCartoonSvg('fence'), cost: 5 },
  { key: 'tree', label: 'Tree', img: getCartoonSvg('tree'), cost: 10 },
  { key: 'solar', label: 'Solar', img: getCartoonSvg('solar'), cost: 20 },
  { key: 'wind', label: 'Windmill', img: getCartoonSvg('wind'), cost: 25 },
  { key: 'garden', label: 'Garden', img: getCartoonSvg('garden'), cost: 15 },
  { key: 'sheep', label: 'Sheep', img: getCartoonSvg('sheep'), cost: 30 },
  { key: 'cow', label: 'Cow', img: getCartoonSvg('cow'), cost: 40 },
  { key: 'chicken', label: 'Chicken', img: getCartoonSvg('chicken'), cost: 20 },
  { key: 'pig', label: 'Pig', img: getCartoonSvg('pig'), cost: 35 },
  { key: 'food', label: 'Feed', img: getCartoonSvg('food'), cost: 0 },
  { key: 'broom', label: 'Clean', img: getCartoonSvg('broom'), cost: 0 },
  { key: 'pet', label: 'Pet', img: getCartoonSvg('pet'), cost: 0 },
  { key: 'eraser', label: 'Eraser', img: getCartoonSvg('eraser'), cost: 0 }
]
const textures = ref<{ [key: string]: string }>({
  ground: getCartoonSvg('ground'),
  house: getCartoonSvg('house'),
  person: getCartoonSvg('person'),
  fence: getCartoonSvg('fence'),
  tree: getCartoonSvg('tree'),
  solar: getCartoonSvg('solar'),
  wind: getCartoonSvg('wind'),
  garden: getCartoonSvg('garden'),
  sheep: getCartoonSvg('sheep'),
  cow: getCartoonSvg('cow'),
  chicken: getCartoonSvg('chicken'),
  pig: getCartoonSvg('pig'),
  food: getCartoonSvg('food'),
  broom: getCartoonSvg('broom'),
  pet: getCartoonSvg('pet'),
  eraser: getCartoonSvg('eraser')
})

function selectTool(key: string) {
  selectedType.value = key
  if (app && app.canvas) {
    if (key === 'eraser') app.canvas.style.cursor = 'crosshair'
    else if (key === 'broom') app.canvas.style.cursor = 'pointer'
    else if (key === 'pet') app.canvas.style.cursor = 'grab'
    else app.canvas.style.cursor = 'default'
  }
}

let app: Application | null = null
let gardenContainer: Container | null = null
let backgroundSprite: TilingSprite | null = null
let loadedTextures: { [key: string]: Texture | any } = {}

const score = computed(() => gameState.value.gold)
const energy = computed(() => gameState.value.energy)
const envScore = computed(() => gameState.value.env)
const villageLevel = computed(() => gameState.value.villageLevel)
const xp = computed(() => gameState.value.xp)
const xpToNext = computed(() => gameState.value.xpToNext)
const currentMission = ref({ text: 'Build 3 Houses', type: 'build', target: 'house', count: 3, current: 0, reward: 50 })

// Map to track sprite ID to Sprite object
const spriteMap = new Map<string, Sprite>()
let spriteIdCounter = 0

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

function addGold(amount: number) {
  gameState.value.gold += amount
  saveState(gameState.value)
}

function addEnv(amount: number) {
  gameState.value.env += amount
  saveState(gameState.value)
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
        { text: 'Collect 50 Gold', type: 'collect', target: 'gold', count: 50, reward: 40 },
        { text: 'Restore Nature (30 Env)', type: 'collect', target: 'env', count: 30, reward: 50 },
        { text: 'Stockpile 200 Gold', type: 'collect', target: 'gold', count: 200, reward: 150 },
      ]
      const next = missions[Math.floor(Math.random() * missions.length)]
      currentMission.value = { ...next, current: 0 }
    }
  }
}

function addXp(amount: number) {
  gameState.value.xp += amount
  if (gameState.value.xp >= gameState.value.xpToNext) {
    gameState.value.xp -= gameState.value.xpToNext
    gameState.value.villageLevel++
    gameState.value.xpToNext = Math.floor(gameState.value.xpToNext * 1.5)
    gameState.value.buildLimit += 3
    spawnFloatingText(app!.screen.width / 2, app!.screen.height / 2, 'VILLAGE LEVEL UP!', '#FFD700')
    spawnFloatingText(app!.screen.width / 2, (app!.screen.height / 2) + 40, '+3 BUILDS!', '#FFFFFF')
  }
  saveState(gameState.value)
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

function hasWorkerNearby(sprite: Sprite): boolean {
  const range = 96 // 3 tiles
  for (const child of gardenContainer!.children) {
    if (!(child instanceof Sprite) || child['customType'] !== 'person') continue
    const dx = child.x - sprite.x
    const dy = child.y - sprite.y
    const dist = Math.sqrt(dx*dx + dy*dy)
    if (dist <= range) return true
  }
  return false
}

function updateSpriteState(sprite: Sprite, spriteData: SpriteData) {
  const type = sprite['customType']
  
  // Update visual state based on data
  if (spriteData.state === 'DIRTY') {
    sprite.tint = 0x8B4513 // Brown tint
  } else if (spriteData.state === 'HUNGRY') {
    sprite.tint = 0xFF6B6B // Red tint
  } else if (spriteData.state === 'READY') {
    sprite.tint = 0xFFFF00 // Yellow glow
  } else {
    sprite.tint = 0xFFFFFF // Normal
  }
  
  // Update hunger bar for animals
  const animals = ['sheep', 'cow', 'chicken', 'pig']
  if (animals.includes(type) && spriteData.hunger !== undefined) {
    // Find or create hunger bar
    let barFg = sprite.children.find(c => c instanceof Graphics && (c as any).isHungerBar) as Graphics
    if (!barFg) {
      const barBg = new Graphics()
      barBg.rect(-16, -28, 32, 4)
      barBg.fill(0x000000)
      sprite.addChild(barBg)
      
      barFg = new Graphics()
      ;(barFg as any).isHungerBar = true
      sprite.addChild(barFg)
    }
    
    barFg.clear()
    const pct = Math.max(0, spriteData.hunger / 100)
    barFg.rect(-15, -27, 30 * pct, 2)
    barFg.fill(pct > 0.3 ? 0x00FF00 : 0xFF0000)
  }
  
  // Show ready indicator
  if (spriteData.state === 'READY') {
    showReadyIndicator(sprite, spriteData.type)
  } else {
    hideReadyIndicator(sprite)
  }
}

function showReadyIndicator(sprite: Sprite, type: string) {
  // Remove existing indicator
  hideReadyIndicator(sprite)
  
  const reward = PRODUCTION_REWARDS[type as keyof typeof PRODUCTION_REWARDS]
  if (!reward) return
  
  const style = new TextStyle({
    fontFamily: 'Arial',
    fontSize: 32,
    fontWeight: 'bold',
  })
  const indicator = new Text({ text: reward.icon, style })
  indicator.anchor.set(0.5)
  indicator.y = -40
  ;(indicator as any).isReadyIndicator = true
  
  // Bobbing animation
  sprite.addChild(indicator)
}

function hideReadyIndicator(sprite: Sprite) {
  const indicator = sprite.children.find(c => (c as any).isReadyIndicator)
  if (indicator) sprite.removeChild(indicator)
}

function startProduction(spriteData: SpriteData) {
  const sprite = spriteMap.get(spriteData.id)
  if (!sprite) return
  
  spriteData.state = 'PRODUCING'
  spriteData.productionStartTime = Date.now()
  
  const idx = gameState.value.sprites.findIndex(s => s.id === spriteData.id)
  if (idx >= 0) gameState.value.sprites[idx] = spriteData
  
  saveState(gameState.value)
  updateSpriteState(sprite, spriteData)
  
  spawnFloatingText(sprite.x, sprite.y, 'Working...', '#4CAF50')
}

function collectProduction(spriteData: SpriteData) {
  const sprite = spriteMap.get(spriteData.id)
  if (!sprite) return
  
  const reward = PRODUCTION_REWARDS[spriteData.type as keyof typeof PRODUCTION_REWARDS]
  if (!reward) return
  
  // Give rewards
  const multiplier = Math.pow(1.5, spriteData.level - 1) * (spriteData.happiness || 1)
  const goldAmount = Math.round(reward.gold * multiplier)
  const xpAmount = Math.round(reward.xp * multiplier)
  
  addGold(goldAmount)
  addXp(xpAmount)
  checkMission('collect', 'gold', goldAmount)
  
  spawnFloatingText(sprite.x, sprite.y, `+${goldAmount} 🪙`, '#FFD700')
  
  // Transition to next state
  const animals = ['sheep', 'cow', 'chicken', 'pig']
  if (animals.includes(spriteData.type)) {
    // Animals need care after collection
    if (Math.random() > 0.5) {
      spriteData.state = 'DIRTY'
    } else {
      spriteData.state = 'IDLE'
    }
    spriteData.hunger = Math.max(0, (spriteData.hunger || 100) - 20)
  } else {
    spriteData.state = 'IDLE'
  }
  
  spriteData.lastCollectTime = Date.now()
  
  const idx = gameState.value.sprites.findIndex(s => s.id === spriteData.id)
  if (idx >= 0) gameState.value.sprites[idx] = spriteData
  
  saveState(gameState.value)
  updateSpriteState(sprite, spriteData)
}

function cleanSprite(spriteData: SpriteData) {
  const sprite = spriteMap.get(spriteData.id)
  if (!sprite) return
  
  if (gameState.value.gold < 2) {
    spawnFloatingText(sprite.x, sprite.y, 'Need 2🪙!', '#FF0000')
    return
  }
  
  gameState.value.gold -= 2
  spriteData.state = 'IDLE'
  
  const idx = gameState.value.sprites.findIndex(s => s.id === spriteData.id)
  if (idx >= 0) gameState.value.sprites[idx] = spriteData
  
  saveState(gameState.value)
  updateSpriteState(sprite, spriteData)
  spawnFloatingText(sprite.x, sprite.y, '✨ Clean!', '#00FFFF')
}

function feedSprite(spriteData: SpriteData) {
  const sprite = spriteMap.get(spriteData.id)
  if (!sprite) return
  
  spriteData.hunger = 100
  spriteData.state = 'IDLE'
  
  const idx = gameState.value.sprites.findIndex(s => s.id === spriteData.id)
  if (idx >= 0) gameState.value.sprites[idx] = spriteData
  
  saveState(gameState.value)
  updateSpriteState(sprite, spriteData)
  spawnFloatingText(sprite.x, sprite.y, 'Yum! 🍎', '#FF69B4')
}

function startPetting(sprite: Sprite) {
  petTargetSprite.value = sprite
  petHoldStart.value = Date.now()
}

function cancelPetting() {
  petTargetSprite.value = null
  petHoldStart.value = 0
}

function completePetting(spriteData: SpriteData) {
  const sprite = spriteMap.get(spriteData.id)
  if (!sprite) return
  
  spriteData.happiness = 1.1 // 10% bonus
  
  const idx = gameState.value.sprites.findIndex(s => s.id === spriteData.id)
  if (idx >= 0) gameState.value.sprites[idx] = spriteData
  
  saveState(gameState.value)
  
  // Show hearts
  for (let i = 0; i < 5; i++) {
    setTimeout(() => {
      spawnFloatingText(
        sprite.x + (Math.random() - 0.5) * 30,
        sprite.y - 20 - i * 10,
        '💖',
        '#FF1493'
      )
    }, i * 100)
  }
  
  cancelPetting()
}

const redemptionItems = [
  { id: 'pto', name: '1 Day PTO', icon: '🏖️', cost: 100, description: 'Take a day off!' },
  { id: 'bottle', name: 'Company Bottle', icon: '🍾', cost: 50, description: 'Stay hydrated in style' },
  { id: 'tshirt', name: 'Company T-Shirt', icon: '👕', cost: 75, description: 'Wear your pride' },
  { id: 'mug', name: 'Coffee Mug', icon: '☕', cost: 30, description: 'Morning motivation' },
  { id: 'snacks', name: 'Snack Box', icon: '🍿', cost: 25, description: 'Fuel for coding' }
]

const redeemedItems = ref<string[]>([])
const totalDonated = ref(0)

function redeemItem(item: typeof redemptionItems[0]) {
  if (gameState.value.gold < item.cost) {
    alert(`Not enough gold! You need ${item.cost} 🪙`)
    return
  }
  
  gameState.value.gold -= item.cost
  redeemedItems.value.push(item.name)
  saveState(gameState.value)
  
  alert(`✅ Redeemed: ${item.name}!`)
}

function donateToCharity() {
  if (gameState.value.env < 100) {
    alert(`Not enough eco points! You need 100 🌿`)
    return
  }
  
  gameState.value.env -= 100
  totalDonated.value += 2
  saveState(gameState.value)
  
  alert(`✅ Donated 2€ to ecological charity! 🌍\nTotal donated: ${totalDonated.value}€`)
}

function mergeSprites(source: Sprite, target: Sprite) {
  const sourceData = gameState.value.sprites.find(s => s.id === source['spriteId'])
  const targetData = gameState.value.sprites.find(s => s.id === target['spriteId'])
  
  if (!sourceData || !targetData) return
  
  // Upgrade target
  targetData.level = (targetData.level || 1) + 1
  
  // Visual upgrade
  target.tint = 0xFFFF00 // Gold tint
  target.scale.set((target.scale.x || 1) * 1.1)
  
  // Remove source
  const sourceIdx = gameState.value.sprites.findIndex(s => s.id === sourceData.id)
  if (sourceIdx >= 0) gameState.value.sprites.splice(sourceIdx, 1)
  
  spriteMap.delete(sourceData.id)
  gardenContainer!.removeChild(source)
  
  saveState(gameState.value)
  updateSpriteState(target, targetData)
  
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
  await fetchCredits()
  app = new Application()
  await app.init({ width: window.innerWidth, height: window.innerHeight, backgroundAlpha: 0 })

  if (pixiContainer.value) {
    pixiContainer.value.appendChild(app.canvas)
    resizeApp()
  }

  gardenContainer = new Container()
  app.stage.addChild(gardenContainer)

  const groundTexture = await Assets.load(textures.value.ground)
  backgroundSprite = new TilingSprite({
    texture: groundTexture,
    width: app.screen.width,
    height: app.screen.height
  })
  app.stage.addChildAt(backgroundSprite, 0)

  // Load all textures
  for (const key in textures.value) {
    try {
      loadedTextures[key] = await Assets.load(textures.value[key])
    } catch (err) {
      console.error(`Failed to load texture ${key}:`, err)
    }
  }

  // Restore saved sprites
  for (const spriteData of gameState.value.sprites) {
    const sprite = new Sprite(loadedTextures[spriteData.type])
    sprite.anchor.set(0.5)
    sprite.x = spriteData.x
    sprite.y = spriteData.y
    sprite.interactive = true
    sprite.cursor = 'grab'
    sprite['customType'] = spriteData.type
    sprite['spriteId'] = spriteData.id
    ;(sprite as any).targetPos = { x: spriteData.x, y: spriteData.y }
    
    gardenContainer.addChild(sprite)
    spriteMap.set(spriteData.id, sprite)
    updateSpriteState(sprite, spriteData)
  }

  // Game Loop
  let lastWanderTime = Date.now()
  app.ticker.add((ticker) => {
    if (!gardenContainer) return
    const delta = ticker.deltaTime
    const now = Date.now()
    
    // Smooth movement
    for (const child of gardenContainer.children) {
      if (child instanceof Sprite) {
        const target = (child as any).targetPos
        if (target && !(child as any).dragging) {
          child.x += (target.x - child.x) * 0.1 * delta
          child.y += (target.y - child.y) * 0.1 * delta
          
          if (Math.abs(target.x - child.x) < 0.1) child.x = target.x
          if (Math.abs(target.y - child.y) < 0.1) child.y = target.y
        }
        
        // Bob ready indicators
        const indicator = child.children.find(c => (c as any).isReadyIndicator)
        if (indicator) {
          indicator.y = -40 + Math.sin(now / 200) * 5
        }
      }
    }
    
    // Wandering behavior (every 2 seconds)
    if (now - lastWanderTime > 2000) {
      lastWanderTime = now
      const wanderers = ['person', 'sheep', 'cow', 'chicken', 'pig']
      
      for (const child of gardenContainer.children) {
        if (!(child instanceof Sprite)) continue
        if (!wanderers.includes(child['customType'])) continue
        if ((child as any).dragging) continue
        
        const spriteId = child['spriteId']
        const spriteData = gameState.value.sprites.find(s => s.id === spriteId)
        if (!spriteData) continue
        
        // Check if inside a fence area
        let fenceArea: { minX: number, maxX: number, minY: number, maxY: number } | null = null
        
        // Find if sprite is within any fence boundary
        const fences = gardenContainer.children.filter(c => c instanceof Sprite && c['customType'] === 'fence')
        if (fences.length >= 4) {
          // Simple fence detection: if surrounded by fences
          const nearbyFences = fences.filter(f => {
            const dx = Math.abs((f as Sprite).x - child.x)
            const dy = Math.abs((f as Sprite).y - child.y)
            return dx <= 96 && dy <= 96
          })
          
          if (nearbyFences.length >= 3) {
            const fencePositions = nearbyFences.map(f => ({ x: (f as Sprite).x, y: (f as Sprite).y }))
            fenceArea = {
              minX: Math.min(...fencePositions.map(p => p.x)),
              maxX: Math.max(...fencePositions.map(p => p.x)),
              minY: Math.min(...fencePositions.map(p => p.y)),
              maxY: Math.max(...fencePositions.map(p => p.y))
            }
          }
        }
        
        // Random wander
        if (Math.random() > 0.6) {
          const dirs = [[-32, 0], [32, 0], [0, -32], [0, 32]]
          const choice = dirs[Math.floor(Math.random() * dirs.length)]
          let nx = child.x + choice[0]
          let ny = child.y + choice[1]
          
          // Keep within fence if inside one
          if (fenceArea) {
            nx = Math.max(fenceArea.minX + 16, Math.min(fenceArea.maxX - 16, nx))
            ny = Math.max(fenceArea.minY + 16, Math.min(fenceArea.maxY - 16, ny))
          } else {
            // Keep within canvas bounds
            nx = Math.max(32, Math.min(app!.renderer.width - 32, nx))
            ny = Math.max(32, Math.min(app!.renderer.height - 32, ny))
          }
          
          // Check collision with houses/persons
          let blocked = false
          for (const other of gardenContainer.children) {
            if (!(other instanceof Sprite) || other === child) continue
            if (['house', 'person'].includes(other['customType']) && 
                Math.abs(other.x - nx) < 32 && Math.abs(other.y - ny) < 32) {
              blocked = true
              break
            }
          }
          
          if (!blocked) {
            ;(child as any).targetPos = { x: nx, y: ny }
          }
        }
      }
    }
    
    // Check production timers
    let stateChanged = false
    for (const spriteData of gameState.value.sprites) {
      if (spriteData.state === 'PRODUCING' && spriteData.productionStartTime) {
        const duration = PRODUCTION_TIMES[spriteData.type as keyof typeof PRODUCTION_TIMES]
        if (duration && now - spriteData.productionStartTime >= duration) {
          spriteData.state = 'READY'
          const sprite = spriteMap.get(spriteData.id)
          if (sprite) updateSpriteState(sprite, spriteData)
          stateChanged = true
        }
      }
    }
    
    if (stateChanged) {
      saveState(gameState.value)
    }
    
    // Check petting hold duration
    if (petTargetSprite.value && petHoldStart.value > 0) {
      const holdDuration = now - petHoldStart.value
      if (holdDuration >= 5000) {
        const spriteId = petTargetSprite.value['spriteId']
        const spriteData = gameState.value.sprites.find(s => s.id === spriteId)
        if (spriteData) {
          completePetting(spriteData)
        }
      }
    }
  })

  app.view.addEventListener('contextmenu', (ev) => ev.preventDefault())
  app.canvas.style.touchAction = 'none'

  // Click handler
  app.canvas.addEventListener('pointerdown', (e) => {
    // Right-click: delete
    if (e.button === 2) {
      const rect = app!.canvas.getBoundingClientRect()
      const px = e.clientX - rect.left
      const py = e.clientY - rect.top
      
      for (let i = gardenContainer!.children.length - 1; i >= 0; i--) {
        const child = gardenContainer!.children[i]
        if (child instanceof Sprite && child['customType']) {
          const b = child.getBounds()
          if (px >= b.x && px <= b.x + b.width && py >= b.y && py <= b.y + b.height) {
            const spriteId = child['spriteId']
            const idx = gameState.value.sprites.findIndex(s => s.id === spriteId)
            if (idx >= 0) {
              gameState.value.sprites.splice(idx, 1)
              gameState.value.buildLimit++
            }
            spriteMap.delete(spriteId)
            gardenContainer!.removeChild(child)
            saveState(gameState.value)
            break
          }
        }
      }
      return
    }

    const rect = app!.canvas.getBoundingClientRect()
    const rawX = e.clientX - rect.left
    const rawY = e.clientY - rect.top
    let x = Math.round(rawX / 32) * 32
    let y = Math.round(rawY / 32) * 32

    // Find clicked sprite
    let clickedSprite: Sprite | null = null
    for (let i = gardenContainer!.children.length - 1; i >= 0; i--) {
      const child = gardenContainer!.children[i]
      if (!(child instanceof Sprite) || !child['customType']) continue
      const bounds = child.getBounds()
      const inside = rawX >= bounds.x && rawX <= bounds.x + bounds.width && 
                     rawY >= bounds.y && rawY <= bounds.y + bounds.height
      if (inside) {
        clickedSprite = child
        break
      }
    }

    if (clickedSprite) {
      const spriteId = clickedSprite['spriteId']
      const spriteData = gameState.value.sprites.find(s => s.id === spriteId)
      if (!spriteData) return

      // Tool interactions
      if (selectedType.value === 'eraser') {
        const idx = gameState.value.sprites.findIndex(s => s.id === spriteId)
        if (idx >= 0) {
          const removedType = gameState.value.sprites[idx].type
          gameState.value.sprites.splice(idx, 1)
          // Only increment buildLimit for non-house buildings
          if (removedType !== 'house') {
            gameState.value.buildLimit++
          }
        }
        spriteMap.delete(spriteId)
        gardenContainer!.removeChild(clickedSprite)
        saveState(gameState.value)
        return
      }

      if (selectedType.value === 'food') {
        feedSprite(spriteData)
        return
      }

      if (selectedType.value === 'broom') {
        if (spriteData.state === 'DIRTY') {
          cleanSprite(spriteData)
        }
        return
      }

      if (selectedType.value === 'pet') {
        const animals = ['sheep', 'cow', 'chicken', 'pig']
        if (animals.includes(spriteData.type)) {
          startPetting(clickedSprite)
        }
        return
      }

      // State interactions (click sprite directly)
      if (spriteData.state === 'READY') {
        collectProduction(spriteData)
        return
      }

      if (spriteData.state === 'IDLE') {
        startProduction(spriteData)
        return
      }

      // Drag sprite
      clickedSprite.cursor = 'grabbing'
      clickedSprite.dragging = true
      clickedSprite.alpha = 0.7
      
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
        clickedSprite!.alpha = 1
        
        const finalX = Math.round(clickedSprite!.x / 32) * 32
        const finalY = Math.round(clickedSprite!.y / 32) * 32
        clickedSprite!.x = finalX
        clickedSprite!.y = finalY
        ;(clickedSprite as any).targetPos = { x: finalX, y: finalY }

        // Update position in state
        if (spriteData) {
          spriteData.x = finalX
          spriteData.y = finalY
          saveState(gameState.value)
        }

        // Check for merge
        for (const child of gardenContainer!.children) {
          if (child === clickedSprite) continue
          if (child instanceof Sprite && child['customType'] === clickedSprite!['customType']) {
            if (Math.abs(child.x - finalX) < 5 && Math.abs(child.y - finalY) < 5) {
              mergeSprites(clickedSprite!, child)
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

    // Place new sprite
    if (['food', 'broom', 'pet', 'eraser'].includes(selectedType.value)) return
    
    const cost = decorationCosts[selectedType.value] || 0

    // Check credits
    if (cost > 0 && credits.value < cost) {
      spawnFloatingText(x, y, `Need ${cost} credits!`, '#FF0000')
      return
    }

    // Check house limit (only limited by credits, not buildLimit)
    if (selectedType.value === 'house') {
      const currentHouses = gameState.value.sprites.filter(s => s.type === 'house').length
      if (currentHouses >= maxHouses.value) {
        spawnFloatingText(x, y, `Max ${maxHouses.value} houses!`, '#FF0000')
        return
      }
    } else {
      // Only non-house buildings use buildLimit
      if (gameState.value.buildLimit <= 0) {
        spawnFloatingText(x, y, 'Build limit reached!', '#FF0000')
        return
      }
    }
    
    // Check person limit (must have houses)
    if (selectedType.value === 'person') {
      const currentPeople = gameState.value.sprites.filter(s => s.type === 'person').length
      const currentHouses = gameState.value.sprites.filter(s => s.type === 'house').length
      if (currentPeople >= currentHouses) {
        spawnFloatingText(x, y, 'Need more houses!', '#FF0000')
        return
      }
    }

    // Check overlap
    for (const child of gardenContainer!.children) {
      if (child instanceof Sprite && child.x === x && child.y === y) {
        if (['house', 'person'].includes(child['customType']) && 
            ['house', 'person'].includes(selectedType.value)) {
          return
        }
      }
    }

    const sprite = new Sprite(loadedTextures[selectedType.value])
    const newId = `sprite-${Date.now()}-${spriteIdCounter++}`
    
    sprite.anchor.set(0.5)
    sprite.x = x
    sprite.y = y
    sprite.interactive = true
    sprite.cursor = 'grab'
    sprite['customType'] = selectedType.value
    sprite['spriteId'] = newId
    ;(sprite as any).targetPos = { x, y }

    gardenContainer!.addChild(sprite)
    spriteMap.set(newId, sprite)

    // Deduct credits
    if (cost > 0) {
      subtractCredits(cost)
      spawnFloatingText(x, y, `-${cost} credits`, '#FF0000')
    }

    const animals = ['sheep', 'cow', 'chicken', 'pig']
    const newSpriteData: SpriteData = {
      id: newId,
      type: selectedType.value,
      x,
      y,
      level: 1,
      state: 'IDLE',
      hunger: animals.includes(selectedType.value) ? 100 : undefined,
    }

    gameState.value.sprites.push(newSpriteData)
    // Only decrement buildLimit for non-house buildings
    if (selectedType.value !== 'house') {
      gameState.value.buildLimit--
    }
    saveState(gameState.value)
    updateSpriteState(sprite, newSpriteData)
    checkMission('build', selectedType.value)
  })

  app.canvas.addEventListener('pointerup', () => {
    if (petTargetSprite.value) {
      cancelPetting()
    }
  })

  window.addEventListener('resize', resizeApp)
})

onBeforeUnmount(() => {
  if (app) {
    app.destroy(true, { children: true })
    app = null
  }
  window.removeEventListener('resize', resizeApp)
  spriteMap.clear()
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
          :disabled="(buildLimit <= 0 && type.key !== 'eraser' && type.key !== 'house') || (type.key === 'house' && gameState.sprites.filter(s => s.type === 'house').length >= maxHouses)"
          @click="selectTool(type.key)"
          :class="[
            'rounded shadow border-2 flex flex-col items-center justify-center p-1 tool-button flex-shrink-0',
            selectedType === type.key ? 'border-green-600 bg-green-100 selected-tool' : 'border-green-200 bg-white',
            ((buildLimit <= 0 && type.key !== 'eraser' && type.key !== 'house') || (type.key === 'house' && gameState.sprites.filter(s => s.type === 'house').length >= maxHouses)) ? 'opacity-50 cursor-not-allowed' : 'hover:border-green-400 hover:bg-green-50'
          ]"
          :title="type.label"
          :aria-pressed="selectedType === type.key"
          style="width: 48px; height: 48px;"
        >
          <img :src="type.img" :alt="type.label" style="width: 32px; height: 32px; object-fit: contain;" />
          <span class="text-[10px] mt-0.5 text-green-800 leading-none flex flex-col items-center">
            <span>{{ type.label }}</span>
            <span v-if="type.cost > 0" class="text-[8px] text-blue-600 font-bold">{{ type.cost }}cr</span>
          </span>
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
        <div class="text-yellow-700 bg-yellow-50 rounded p-1 cursor-pointer hover:bg-yellow-100" @click="showRedemptionShop = !showRedemptionShop" title="Click to open shop">🪙 {{ score }}</div>
        <div class="text-blue-700 bg-blue-50 rounded p-1">Credits: {{ credits }}</div>
        <div class="text-green-800 bg-green-100 rounded p-1 cursor-pointer hover:bg-green-200" @click="showEcoShop = !showEcoShop" title="Click to donate eco points">🌿 {{ envScore }}</div>
      </div>

      <!-- Housing Info -->
      <div class="grid grid-cols-2 gap-2 text-xs font-bold w-full max-w-md px-4 mb-2 pointer-events-auto">
        <div class="text-purple-700 bg-purple-50 rounded p-1">
          Houses: {{ gameState.sprites.filter(s => s.type === 'house').length }}/{{ maxHouses }}
        </div>
        <div class="text-indigo-700 bg-indigo-50 rounded p-1">
          People: {{ gameState.sprites.filter(s => s.type === 'person').length }}/{{ gameState.sprites.filter(s => s.type === 'house').length }}
        </div>
      </div>

      <div class="mb-1 text-black text-[10px] text-center px-4 pointer-events-auto">
        Click IDLE items to start production • Click READY items to collect
      </div>

      <!-- Debug Button -->
      <button 
        @click="showDebugPanel = !showDebugPanel"
        class="mt-2 px-3 py-1 bg-purple-500 hover:bg-purple-600 text-white text-xs font-bold rounded pointer-events-auto"
      >
        🐛 Debug Panel
      </button>

      <!-- Debug Panel -->
      <div v-if="showDebugPanel" class="mt-2 bg-purple-100 border-2 border-purple-500 rounded-lg p-3 w-full max-w-md pointer-events-auto">
        <h3 class="text-sm font-bold text-purple-800 mb-2">Debug Tools</h3>
        <div class="grid grid-cols-2 gap-2">
          <button @click="addGold(100)" class="px-3 py-2 bg-yellow-500 hover:bg-yellow-600 text-white text-xs font-bold rounded">
            +100 🪙 Gold
          </button>
          <button @click="addEnv(100)" class="px-3 py-2 bg-green-500 hover:bg-green-600 text-white text-xs font-bold rounded">
            +100 🌿 Eco
          </button>
          <button @click="addXp(100)" class="px-3 py-2 bg-yellow-400 hover:bg-yellow-500 text-white text-xs font-bold rounded">
            +100 ⭐ XP
          </button>
          <button @click="gameState.buildLimit += 10; saveState(gameState)" class="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-xs font-bold rounded">
            +10 Builds
          </button>
        </div>
      </div>
    </div>

    <!-- Eco Donation Shop Modal -->
    <div v-if="showEcoShop" class="absolute inset-0 z-20 flex items-center justify-center bg-black/50 pointer-events-auto" @click="showEcoShop = false">
      <div class="bg-white rounded-lg shadow-2xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto" @click.stop>
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold text-gray-800">🌍 Eco Donation Center</h2>
          <button @click="showEcoShop = false" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>
        <p class="text-sm text-gray-600 mb-4">Convert your eco points into real donations to ecological charities!</p>
        
        <div class="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-lg p-6 mb-4">
          <div class="text-center">
            <div class="text-6xl mb-3">🌱</div>
            <h3 class="text-xl font-bold text-gray-800 mb-2">Donate to Ecological Charity</h3>
            <p class="text-gray-700 mb-4">Exchange 100 🌿 Eco Points for a 2€ donation to environmental organizations</p>
            <div class="flex items-center justify-center gap-4 mb-4">
              <div class="bg-white rounded-lg px-4 py-2 shadow">
                <div class="text-xs text-gray-500">Your Eco Points</div>
                <div class="text-2xl font-bold text-green-600">{{ envScore }} 🌿</div>
              </div>
              <div class="text-3xl">→</div>
              <div class="bg-white rounded-lg px-4 py-2 shadow">
                <div class="text-xs text-gray-500">Donation Value</div>
                <div class="text-2xl font-bold text-blue-600">2€</div>
              </div>
            </div>
            <button 
              @click="donateToCharity()"
              :disabled="envScore < 100"
              :class="[
                'px-6 py-3 rounded-lg font-bold text-lg transition-all transform hover:scale-105',
                envScore >= 100 
                  ? 'bg-green-500 hover:bg-green-600 text-white cursor-pointer shadow-lg' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              ]"
            >
              {{ envScore >= 100 ? '💚 Donate 2€ Now' : '🔒 Need 100 Eco Points' }}
            </button>
          </div>
        </div>
        
        <div v-if="totalDonated > 0" class="bg-blue-50 border-2 border-blue-300 rounded-lg p-4 text-center">
          <div class="text-sm text-blue-600 font-bold mb-1">🎉 Total Impact</div>
          <div class="text-3xl font-bold text-blue-700">{{ totalDonated }}€</div>
          <div class="text-xs text-gray-600 mt-1">donated to ecological charities</div>
        </div>
        
        <div class="mt-6 bg-gray-50 rounded-lg p-4">
          <h4 class="font-bold text-gray-700 mb-2">🌍 About Our Charity Partners</h4>
          <p class="text-sm text-gray-600">Your donations support verified environmental organizations working on:</p>
          <ul class="text-sm text-gray-600 mt-2 space-y-1">
            <li>🌲 Reforestation and forest conservation</li>
            <li>🌊 Ocean cleanup and marine protection</li>
            <li>♻️ Renewable energy and sustainability projects</li>
            <li>🐾 Wildlife habitat preservation</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Redemption Shop Modal -->
    <div v-if="showRedemptionShop" class="absolute inset-0 z-20 flex items-center justify-center bg-black/50 pointer-events-auto" @click="showRedemptionShop = false">
      <div class="bg-white rounded-lg shadow-2xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto" @click.stop>
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold text-gray-800">🎁 Redemption Shop</h2>
          <button @click="showRedemptionShop = false" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>
        <p class="text-sm text-gray-600 mb-4">Spend your gold coins on employee perks and rewards!</p>
        
        <div class="space-y-3">
          <div v-for="item in redemptionItems" :key="item.id" 
               class="border rounded-lg p-4 flex items-center justify-between hover:bg-gray-50 transition">
            <div class="flex items-center gap-3">
              <span class="text-4xl">{{ item.icon }}</span>
              <div>
                <h3 class="font-bold text-gray-800">{{ item.name }}</h3>
                <p class="text-sm text-gray-600">{{ item.description }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="font-bold text-yellow-600">{{ item.cost }} 🪙</span>
              <button 
                @click="redeemItem(item)"
                :disabled="score < item.cost"
                :class="[
                  'px-4 py-2 rounded-lg font-bold transition',
                  score >= item.cost 
                    ? 'bg-green-500 hover:bg-green-600 text-white cursor-pointer' 
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                ]"
              >
                Redeem
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="redeemedItems.length > 0" class="mt-6 pt-4 border-t">
          <h3 class="font-bold text-gray-700 mb-2">✨ Your Redeemed Items:</h3>
          <div class="flex flex-wrap gap-2">
            <span v-for="(item, idx) in redeemedItems" :key="idx" 
                  class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
              {{ item }}
            </span>
          </div>
        </div>
      </div>
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