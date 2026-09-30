function EmptyState({ title, message, children }) {
  return (
    <div className="state-panel">
      <span className="state-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24">
          <path d="M4 19h16" />
          <path d="M5 15l4-4 3 3 7-7" />
        </svg>
      </span>
      <p className="state-title">{title}</p>
      <p>{message}</p>
      {children}
    </div>
  )
}

export default EmptyState
