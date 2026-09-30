import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createStock, deleteStock, getStocks, isUnauthorized, updateStock } from '../api.js'
import Alert from '../components/Alert.jsx'
import Button from '../components/Button.jsx'
import DeleteStockModal from '../components/DeleteStockModal.jsx'
import EmptyState from '../components/EmptyState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import Loading from '../components/Loading.jsx'
import StockFormModal from '../components/StockFormModal.jsx'
import { useAuth } from '../context/AuthContext.js';
const columns = ['Symbol', 'Company', 'Market', 'Sector', 'Notes', 'Actions']

// Counts different values, ignoring empty ones and upper/lower case ("NASDAQ" = "nasdaq").
function countDistinct(values) {
  const cleaned = values
    .map((value) => (value ?? '').trim().toLowerCase())
    .filter((value) => value !== '')

  return new Set(cleaned).size
}

function Dashboard() {
  const { token, logout } = useAuth()
  const navigate = useNavigate()
  const [stocks, setStocks] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'error' | 'success'
  const [reloadCount, setReloadCount] = useState(0)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingStock, setEditingStock] = useState(null) // null = the form adds a new stock
  const [deletingStock, setDeletingStock] = useState(null) // stock waiting for delete confirmation
  const [notice, setNotice] = useState('')

  // 401 = the backend no longer accepts this token, so end the session.
  const endSession = useCallback(() => {
    logout()
    navigate('/login', { replace: true })
  }, [logout, navigate])

  useEffect(() => {
    // If the page closes before the request finishes, ignore the late response.
    let ignore = false

    async function loadStocks() {
      try {
        const data = await getStocks(token)

        if (!ignore) {
          setStocks(data)
          setStatus('success')
        }
      } catch (error) {
        if (ignore) {
          return
        }

        if (isUnauthorized(error)) {
          endSession()
          return
        }

        setStatus('error')
      }
    }

    loadStocks()

    return () => {
      ignore = true
    }
  }, [token, reloadCount, endSession])

  // Changing reloadCount makes the effect above fetch the stocks again.
  function handleRetry() {
    setStatus('loading')
    setReloadCount((count) => count + 1)
  }

  function openAddForm() {
    setNotice('')
    setEditingStock(null)
    setIsFormOpen(true)
  }

  function openEditForm(stock) {
    setNotice('')
    setEditingStock(stock)
    setIsFormOpen(true)
  }

  function closeForm() {
    setIsFormOpen(false)
    setEditingStock(null)
  }

  // Called by the form. If the request fails, the error goes back to the form,
  // which stays open and shows it.
  async function handleSaveStock(stockData) {
    if (editingStock) {
      const stock = await updateStock(token, editingStock.id, stockData)
      setNotice(`${stock.symbol} was updated.`)
    } else {
      const stock = await createStock(token, stockData)
      setNotice(`${stock.symbol} was added to your watchlist.`)
    }

    closeForm()
    setReloadCount((count) => count + 1)
  }

  function openDeleteDialog(stock) {
    setNotice('')
    setDeletingStock(stock)
  }

  function closeDeleteDialog() {
    setDeletingStock(null)
  }

  // Called by the confirmation pop-up. If the request fails, the error is shown
  // there and the stock stays in the list.
  async function handleDeleteStock(stock) {
    await deleteStock(token, stock.id)

    setDeletingStock(null)
    setNotice(`${stock.symbol} was deleted from your watchlist.`)
    setReloadCount((count) => count + 1)
  }

  const hasData = status === 'success'

  const summaryCards = [
    {
      label: 'Total Stocks',
      value: stocks.length,
      hint: 'Stocks in your watchlist',
    },
    {
      label: 'Markets',
      value: countDistinct(stocks.map((stock) => stock.market)),
      hint: 'Different markets',
    },
    {
      label: 'Sectors',
      value: countDistinct(stocks.map((stock) => stock.sector)),
      hint: 'Different sectors',
    },
  ]

  // Text shown inside the table instead of rows. null means "show the rows".
  let watchlistMessage = null

  if (status === 'loading') {
    watchlistMessage = <Loading label="Loading your watchlist..." />
  } else if (status === 'error') {
    watchlistMessage = (
      <ErrorState
        message="Unable to load your watchlist. Please try again."
        onRetry={handleRetry}
      />
    )
  } else if (stocks.length === 0) {
    watchlistMessage = (
      <EmptyState
        title="Your watchlist is empty"
        message="Add stocks to start tracking the companies you're interested in."
      >
        <Button onClick={openAddForm}>Add Stock</Button>
      </EmptyState>
    )
  }

  return (
    <section className="dashboard">
      <div className="page-header">
        <div className="page-header-text">
          <h1>My Watchlist</h1>
          <p>Track and manage the stocks you&apos;re watching.</p>
        </div>
        <Button onClick={openAddForm}>
          <span aria-hidden="true">+</span> Add Stock
        </Button>
      </div>

      <section aria-label="Watchlist summary">
        <dl className="summary-grid">
          {summaryCards.map((card) => (
            <div key={card.label} className="card summary-card">
              <dt>{card.label}</dt>
              <dd className="summary-value">{hasData ? card.value : '—'}</dd>
              <dd className="summary-hint">{card.hint}</dd>
            </div>
          ))}
        </dl>
      </section>

      {notice && <Alert variant="success">{notice}</Alert>}

      <section className="card watchlist" aria-labelledby="watchlist-heading">
        <div className="watchlist-header">
          <h2 id="watchlist-heading">Stocks</h2>
          <p>Stocks you add will appear in this table.</p>
        </div>

        <div className="table-wrapper">
          <table className="watchlist-table" aria-labelledby="watchlist-heading">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column} scope="col">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {watchlistMessage ? (
                <tr>
                  <td className="watchlist-message" colSpan={columns.length}>
                    {watchlistMessage}
                  </td>
                </tr>
              ) : (
                stocks.map((stock) => (
                  <tr key={stock.id} className="stock-row">
                    <td className="stock-symbol">{stock.symbol}</td>
                    <td>{stock.company_name}</td>
                    <td>{stock.market}</td>
                    <td>{stock.sector || '—'}</td>
                    <td className="stock-notes">{stock.notes || '—'}</td>
                    <td>
                      <div className="row-actions">
                        <Button
                          className="btn-secondary btn-small"
                          onClick={() => openEditForm(stock)}
                        >
                          Edit<span className="visually-hidden"> {stock.symbol}</span>
                        </Button>
                        <Button
                          className="btn-secondary btn-small"
                          onClick={() => openDeleteDialog(stock)}
                        >
                          Delete<span className="visually-hidden"> {stock.symbol}</span>
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      {isFormOpen && (
        <StockFormModal
          stock={editingStock}
          onSubmit={handleSaveStock}
          onClose={closeForm}
          onUnauthorized={endSession}
        />
      )}

      {deletingStock && (
        <DeleteStockModal
          stock={deletingStock}
          onConfirm={handleDeleteStock}
          onClose={closeDeleteDialog}
          onUnauthorized={endSession}
        />
      )}
    </section>
  )
}

export default Dashboard
