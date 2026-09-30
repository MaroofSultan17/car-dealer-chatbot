import { post } from '../api/httpClient'
import type { CarSearchRequestDto, CarSearchResponseDto } from '../types/dto'

export async function searchCars(message: string): Promise<CarSearchResponseDto> {
  const requestBody: CarSearchRequestDto = { message }
  const searchResponse = await post<CarSearchResponseDto>('/cars/search', requestBody)

  return searchResponse
}
