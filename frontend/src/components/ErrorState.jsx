import Button from './Button.jsx'

function ErrorState({ title = 'Something went wrong', message, onRetry }) {
  return (
    <div className="state-panel" role="alert">
      <span className="state-icon state-icon-error" aria-hidden="true">
        <svg viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7.5v5" />
          <path d="M12 16.5h.01" />
        </svg>
      </span>
      <p className="state-title">{title}</p>
      <p>{message}</p>
      <Button className="btn-secondary" onClick={onRetry}>
        Try Again
      </Button>
    </div>
  )
}

export default ErrorState
