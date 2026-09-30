import { useState } from 'react'
import { getErrorMessages, isUnauthorized } from '../api.js'
import Alert from './Alert.jsx'
import Button from './Button.jsx'
import Input from './Input.jsx'
import Modal from './Modal.jsx'

const emptyValues = {
  symbol: '',
  company_name: '',
  market: '',
  sector: '',
  notes: '',
}

// Edit mode starts with the stock's current values. The backend uses null for
// an empty sector or notes, but inputs need strings.
function toFormValues(stock) {
  if (!stock) {
    return emptyValues
  }

  return {
    symbol: stock.symbol,
    company_name: stock.company_name,
    market: stock.market,
    sector: stock.sector ?? '',
    notes: stock.notes ?? '',
  }
}

function validateStock(values) {
  const errors = {}

  if (!values.symbol.trim()) {
    errors.symbol = 'Symbol is required.'
  }

  if (!values.company_name.trim()) {
    errors.company_name = 'Company name is required.'
  }

  if (!values.market.trim()) {
    errors.market = 'Market is required.'
  }

  return errors
}

// Shapes the form values into what POST and PUT /stocks expect.
// Empty optional fields are sent as null, which the backend stores as "no value".
function toStockData(values) {
  return {
    symbol: values.symbol.trim().toUpperCase(),
    company_name: values.company_name.trim(),
    market: values.market.trim(),
    sector: values.sector.trim() || null,
    notes: values.notes.trim() || null,
  }
}

// Add mode when `stock` is not given; edit mode when it is.
function StockFormModal({ stock, onSubmit, onClose, onUnauthorized }) {
  const isEditing = Boolean(stock)
  const [values, setValues] = useState(() => toFormValues(stock))
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target

    setValues((current) => ({ ...current, [name]: value }))
    setFieldErrors((current) => ({ ...current, [name]: '' }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    if (isSubmitting) {
      return
    }

    setFormError('')

    const errors = validateStock(values)
    setFieldErrors(errors)

    if (Object.keys(errors).length > 0) {
      return
    }

    setIsSubmitting(true)

    try {
      await onSubmit(toStockData(values))
    } catch (error) {
      if (isUnauthorized(error)) {
        onUnauthorized()
        return
      }

      const { message, fieldErrors: apiFieldErrors } = getErrorMessages(error)
      setFormError(message)
      setFieldErrors(apiFieldErrors)
    } finally {
      setIsSubmitting(false)
    }
  }

  let submitLabel = isEditing ? 'Save Changes' : 'Add Stock'

  if (isSubmitting) {
    submitLabel = isEditing ? 'Saving...' : 'Adding...'
  }

  return (
    <Modal titleId="stock-form-title" onClose={onClose} isBusy={isSubmitting}>
      <form className="modal-body" onSubmit={handleSubmit}>
        <div className="modal-header">
          <h2 id="stock-form-title">{isEditing ? `Edit ${stock.symbol}` : 'Add Stock'}</h2>
          <p>Symbol, company name and market are required.</p>
        </div>

        <Input
          label="Symbol"
          name="symbol"
          value={values.symbol}
          onChange={handleChange}
          placeholder="AAPL"
          maxLength={10}
          error={fieldErrors.symbol}
          required
        />
        <Input
          label="Company Name"
          name="company_name"
          value={values.company_name}
          onChange={handleChange}
          placeholder="Apple Inc."
          maxLength={100}
          error={fieldErrors.company_name}
          required
        />
        <Input
          label="Market"
          name="market"
          value={values.market}
          onChange={handleChange}
          placeholder="NASDAQ"
          maxLength={50}
          error={fieldErrors.market}
          required
        />
        <Input
          label="Sector (optional)"
          name="sector"
          value={values.sector}
          onChange={handleChange}
          placeholder="Technology"
          maxLength={100}
          error={fieldErrors.sector}
        />
        <Input
          label="Notes (optional)"
          name="notes"
          value={values.notes}
          onChange={handleChange}
          placeholder="Why are you watching this stock?"
          maxLength={500}
          error={fieldErrors.notes}
        />

        {formError && <Alert>{formError}</Alert>}

        <div className="modal-actions">
          <Button className="btn-secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {submitLabel}
          </Button>
        </div>
      </form>
    </Modal>
  )
}

export default StockFormModal