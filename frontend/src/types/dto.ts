export type CarSearchRequestDto = {
  message: string
}

export type DealerResponseDto = {
  dealerId: string
  name: string
  phone: string
  email: string
  city: string
}

export type CarResponseDto = {
  carId: string
  make: string
  model: string
  variant: string
  year: number
  priceInCents: number
  dealer: DealerResponseDto | null
}

export type NoticeResponseDto = {
  level: 'info' | 'warning'
  text: string
}

export type CarSearchResponseDto = {
  cars: CarResponseDto[]
  notices: NoticeResponseDto[]
}

export type ErrorResponseDto = {
  detail: string | { msg: string }[]
}
