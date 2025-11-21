export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)

  try {
    const data = await $fetch(`http://13.60.191.32:8000/quiz/${id}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Username': body.user_username || 'alice'
      },
      body: body
    })
    return data
  } catch (error: any) {
    console.error(`Error submitting quiz ${id}:`, error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.message || 'Failed to submit quiz'
    })
  }
})
