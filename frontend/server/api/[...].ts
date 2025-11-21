export default defineEventHandler(async (event) => {
  const path = event.path.replace(/^\/api/, '')
  const target = `http://13.60.191.32:8000${path}`
  
  return proxyRequest(event, target)
})
