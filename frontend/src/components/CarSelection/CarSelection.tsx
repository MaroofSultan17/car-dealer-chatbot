import { useState, type FormEvent } from 'react'
import type { CarResponseDto, DealerResponseDto } from '../../types/dto'
import { formatCents } from '../../utils/money'
import { CalendarIcon, PhoneIcon } from '../icons/icons'
import styles from './CarSelection.module.scss'

type CarSelectionProps = {
  car: CarResponseDto
}

type OpenPanel = 'none' | 'dealer' | 'call'

const appointmentFormatter = new Intl.DateTimeFormat('en-GB', {
  dateStyle: 'long',
  timeStyle: 'short',
})

function todayAsInputValue(): string {
  const today = new Date()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  const inputValue = `${today.getFullYear()}-${month}-${day}`

  return inputValue
}

export function CarSelection({ car }: CarSelectionProps) {
  const [openPanel, setOpenPanel] = useState<OpenPanel>('none')

  return (
    <section className={styles.panel} aria-labelledby="selection-heading">
      <h2 id="selection-heading" className={styles.title}>
        Your selection
      </h2>

      <div className={styles.car}>
        <p className={styles.carName}>
          {car.year} {car.make} {car.model}
        </p>
        <p className={styles.muted}>Variant: {car.variant}</p>
        <p className={styles.muted}>Price: {formatCents(car.priceInCents)}</p>
      </div>

      {car.dealer === null && (
        <p className={styles.error} role="alert">
          Dealer information is unavailable for this vehicle.
        </p>
      )}

      {car.dealer !== null && (
        <>
          <p>
            This vehicle is available through <strong>{car.dealer.name}</strong> in{' '}
            {car.dealer.city}.
          </p>

          <div className={styles.actions}>
            <button
              type="button"
              className={styles.actionButton}
              onClick={() => setOpenPanel('dealer')}
              aria-pressed={openPanel === 'dealer'}
            >
              <PhoneIcon />
              Dealer details
            </button>
            <button
              type="button"
              className={styles.actionButton}
              onClick={() => setOpenPanel('call')}
              aria-pressed={openPanel === 'call'}
            >
              <CalendarIcon />
              Schedule a call
            </button>
          </div>

          {openPanel === 'dealer' && <DealerDetails dealer={car.dealer} />}
          {openPanel === 'call' && <ScheduleCall dealer={car.dealer} />}
        </>
      )}
    </section>
  )
}

type DealerDetailsProps = {
  dealer: DealerResponseDto
}

function DealerDetails({ dealer }: DealerDetailsProps) {
  return (
    <dl className={styles.details}>
      <dt>Name</dt>
      <dd>{dealer.name}</dd>
      <dt>City</dt>
      <dd>{dealer.city}</dd>
      <dt>Phone</dt>
      <dd>
        <a href={`tel:${dealer.phone}`}>{dealer.phone}</a>
      </dd>
      <dt>Email</dt>
      <dd>
        <a href={`mailto:${dealer.email}`}>{dealer.email}</a>
      </dd>
    </dl>
  )
}

type ScheduleCallProps = {
  dealer: DealerResponseDto
}

function ScheduleCall({ dealer }: ScheduleCallProps) {
  const [appointment, setAppointment] = useState<Date | null>(null)

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const callDate = String(formData.get('callDate'))
    const callTime = String(formData.get('callTime'))
    setAppointment(new Date(`${callDate}T${callTime}`))
  }

  if (appointment) {
    return (
      <div className={styles.confirmation} role="status">
        <p className={styles.confirmationTitle}>Call request confirmed!</p>
        <p>
          <strong>Dealer:</strong> {dealer.name}
        </p>
        <p>
          <strong>Phone:</strong> {dealer.phone}
        </p>
        <p>
          <strong>Requested time:</strong> {appointmentFormatter.format(appointment)}
        </p>
        <p className={styles.muted}>
          This is a demonstration only. No external booking has been created.
        </p>
      </div>
    )
  }

  return (
    <form className={styles.scheduleForm} onSubmit={handleSubmit}>
      <label>
        Preferred date
        <input name="callDate" type="date" min={todayAsInputValue()} required />
      </label>
      <label>
        Preferred time
        <input name="callTime" type="time" required />
      </label>
      <button type="submit" className={styles.confirmButton}>
        Confirm call
      </button>
    </form>
  )
}
