import type { FormEvent } from 'react'
import { SearchIcon } from '../icons/icons'
import styles from './SearchForm.module.scss'

type SearchFormProps = {
  isSearching: boolean
  onSearch: (message: string) => void
}

const MESSAGE_MAX_LENGTH = 500

export function SearchForm({ isSearching, onSearch }: SearchFormProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const message = String(formData.get('message') ?? '').trim()

    if (message) {
      onSearch(message)
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} aria-busy={isSearching}>
      <label htmlFor="message" className={styles.label}>
        Which car are you looking for?
      </label>
      <div className={styles.row}>
        <input
          id="message"
          name="message"
          type="text"
          className={styles.input}
          placeholder="For example: I'm looking for a Toyota Corolla hybrid"
          maxLength={MESSAGE_MAX_LENGTH}
          required
          disabled={isSearching}
        />
        <button type="submit" className={styles.submitButton} disabled={isSearching}>
          <SearchIcon />
          {isSearching ? 'Searching…' : 'Search'}
        </button>
      </div>
    </form>
  )
}
