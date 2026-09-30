function Loading({ label = 'Loading...' }) {
  return (
    <div className="loading" role="status">
      <span className="loading-spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export default Loading
