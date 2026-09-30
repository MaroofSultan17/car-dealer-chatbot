import { useState } from 'react'
import styles from './App.module.scss'
import { CarList } from './components/CarList/CarList'
import { CarSelection } from './components/CarSelection/CarSelection'
import { SearchForm } from './components/SearchForm/SearchForm'
import { useCarSearch } from './hooks/useCarSearch'
import type { CarResponseDto } from './types/dto'

export default function App() {
  const { carSearch, isSearching, search } = useCarSearch()
  const [selectedCar, setSelectedCar] = useState<CarResponseDto | null>(null)
  const searchResponse = carSearch.searchResponse
  const hasCars = searchResponse !== null && searchResponse.cars.length > 0

  function handleSearch(message: string): void {
    setSelectedCar(null)
    search(message)
  }

  return (
    <main className={styles.layout}>
      <header className={styles.header}>
        <h1 className={styles.title}>Car Dealer Assistant</h1>
        <p className={styles.muted}>
          Tell me which car you're looking for. I'll check the available inventory and connect you
          with the dealer.
        </p>
      </header>

      <SearchForm isSearching={isSearching} onSearch={handleSearch} />

      {carSearch.errorMessage && (
        <p className={styles.error} role="alert">
          {carSearch.errorMessage}
        </p>
      )}

      {carSearch.searchedMessage && (
        <p className={styles.request}>
          You asked for: <strong>{carSearch.searchedMessage}</strong>
        </p>
      )}

      {searchResponse?.notices.map((notice) => (
        <p key={notice.text} className={styles.notice} data-level={notice.level}>
          {notice.text}
        </p>
      ))}

      {hasCars && (
        <section aria-labelledby="cars-heading" aria-busy={isSearching}>
          <h2 id="cars-heading" className={styles.sectionTitle}>
            Available cars
          </h2>
          <CarList
            cars={searchResponse.cars}
            selectedCarId={selectedCar?.carId ?? null}
            onSelectCar={setSelectedCar}
          />
        </section>
      )}

      {selectedCar && <CarSelection key={selectedCar.carId} car={selectedCar} />}
    </main>
  )
}
