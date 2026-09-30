import { startTransition, useActionState } from 'react'
import { toErrorMessage } from '../api/httpClient'
import { searchCars } from '../services/carService'
import type { CarSearchResponseDto } from '../types/dto'

export type CarSearchState = {
  searchedMessage: string | null
  searchResponse: CarSearchResponseDto | null
  errorMessage: string | null
}

export type UseCarSearchResult = {
  carSearch: CarSearchState
  isSearching: boolean
  search: (message: string) => void
}

const emptySearch: CarSearchState = {
  searchedMessage: null,
  searchResponse: null,
  errorMessage: null,
}

async function runSearch(previous: CarSearchState, message: string): Promise<CarSearchState> {
  try {
    const searchResponse = await searchCars(message)
    const updatedSearch: CarSearchState = {
      searchedMessage: message,
      searchResponse,
      errorMessage: null,
    }

    return updatedSearch
  } catch (error) {
    const unchangedSearch: CarSearchState = { ...previous, errorMessage: toErrorMessage(error) }

    return unchangedSearch
  }
}

export function useCarSearch(): UseCarSearchResult {
  const [carSearch, dispatch, isSearching] = useActionState(runSearch, emptySearch)

  function search(message: string): void {
    startTransition(() => {
      dispatch(message)
    })
  }

  return { carSearch, isSearching, search }
}
