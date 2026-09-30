import type { CarResponseDto } from '../../types/dto'
import { formatCents } from '../../utils/money'
import styles from './CarList.module.scss'

type CarListProps = {
  cars: CarResponseDto[]
  selectedCarId: string | null
  onSelectCar: (car: CarResponseDto) => void
}

export function CarList({ cars, selectedCarId, onSelectCar }: CarListProps) {
  return (
    <ul className={styles.list}>
      {cars.map((car) => {
        const isSelected = car.carId === selectedCarId

        return (
          <li key={car.carId} className={styles.card} data-selected={isSelected}>
            <div className={styles.info}>
              <h3 className={styles.name}>
                {car.year} {car.make} {car.model}
              </h3>
              <span className={styles.variant}>{car.variant}</span>
            </div>

            <div className={styles.buy}>
              <span className={styles.price}>{formatCents(car.priceInCents)}</span>
              <button
                type="button"
                className={styles.selectButton}
                onClick={() => onSelectCar(car)}
                aria-pressed={isSelected}
              >
                {isSelected ? 'Selected' : 'Select'}
              </button>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
