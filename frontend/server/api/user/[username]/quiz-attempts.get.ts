export default defineEventHandler(async (event) => {
  const username = getRouterParam(event, 'username')
  const query = getQuery(event)
  const quiz_id = query.quiz_id

  try {
    let url = `http://13.60.191.32:8000/user/${username}/quiz-attempts`
    if (quiz_id) {
      url += `?quiz_id=${quiz_id}`
    }

    const data = await $fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Username': username || 'alice' // Forward username or default to alice
      }
    })
    return data
  } catch (error: any) {
    console.error(`Error fetching quiz attempts for user ${username}:`, error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.message || 'Failed to fetch quiz attempts'
    })
  }
})
