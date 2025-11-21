export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')

  try {
    const data = await $fetch(`http://13.60.191.32:8000/meeting/${id}/outro-quiz`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    return data
  } catch (error: any) {
    console.error(`Error fetching outro quiz for meeting ${id}:`, error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.message || 'Failed to fetch outro quiz'
    })
  }
})

