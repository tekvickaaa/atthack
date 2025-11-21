export default defineEventHandler(async () => {
  try {
    const data = await $fetch('http://13.60.191.32:8000/meeting', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    return data
  } catch (error: any) {
    console.error('Error fetching meetings:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.message || 'Failed to fetch meetings'
    })
  }
})

