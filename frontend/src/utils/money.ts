const euroFormatter = new Intl.NumberFormat('en-IE', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
})

export function formatCents(cents: number): string {
  const euros = cents / 100
  const formatted = euroFormatter.format(euros)

  return formatted
}
