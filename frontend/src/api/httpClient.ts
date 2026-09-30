import type { ErrorResponseDto } from '../types/dto'

const API_BASE_URL = '/api/v1'

export class ApiError extends Error {}

export function toErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }

  return 'Something went wrong.'
}

async function readErrorMessage(response: Response): Promise<string> {
  const retryAfterSeconds = Number(response.headers.get('Retry-After'))
  if (response.status === 429 && retryAfterSeconds > 0) {
    return `Too many requests. Please try again in ${retryAfterSeconds} seconds.`
  }

  const errorResponse: Partial<ErrorResponseDto> = await response.json().catch(() => ({}))

  if (typeof errorResponse.detail === 'string') {
    return errorResponse.detail
  }

  if (Array.isArray(errorResponse.detail) && errorResponse.detail.length > 0) {
    return errorResponse.detail[0].msg
  }

  if (response.status >= 500) {
    return 'The server is unavailable right now. Please try again.'
  }

  return `Request failed with status ${response.status}.`
}

export async function post<T>(path: string, requestBody: unknown): Promise<T> {
  const url = `${API_BASE_URL}${path}`
  const options: RequestInit = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  }
  let response: Response

  try {
    response = await fetch(url, options)
  } catch {
    throw new ApiError('Could not reach the server. Is the API running?')
  }

  if (!response.ok) {
    const message = await readErrorMessage(response)
    throw new ApiError(message)
  }

  const responseBody: T = await response.json()

  return responseBody
}
