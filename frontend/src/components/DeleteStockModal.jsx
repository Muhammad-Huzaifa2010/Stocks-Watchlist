import { useState } from 'react'
import { getErrorMessages, isUnauthorized } from '../api.js'
import Alert from './Alert.jsx'
import Button from './Button.jsx'
import Modal from './Modal.jsx'

// Asks the user to confirm before a stock is deleted.
// Nothing is deleted until the red Delete button is pressed.
function DeleteStockModal({ stock, onConfirm, onClose, onUnauthorized }) {
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState('')

  async function handleDelete() {
    if (isDeleting) {
      return
    }

    setError('')
    setIsDeleting(true)

    try {
      await onConfirm(stock)
    } catch (requestError) {
      if (isUnauthorized(requestError)) {
        onUnauthorized()
        return
      }

      setError(getErrorMessages(requestError).message)
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <Modal titleId="delete-stock-title" onClose={onClose} isBusy={isDeleting}>
      <div className="modal-body">
        <div className="modal-header">
          <h2 id="delete-stock-title">Delete {stock.symbol}?</h2>
          <p>
            Are you sure you want to delete {stock.symbol} ({stock.company_name}) from
            your watchlist? This cannot be undone.
          </p>
        </div>

        {error && <Alert>{error}</Alert>}

        <div className="modal-actions">
          <Button className="btn-secondary" onClick={onClose} disabled={isDeleting}>
            Cancel
          </Button>
          <Button className="btn-danger" onClick={handleDelete} disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}

export default DeleteStockModal