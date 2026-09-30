function Alert({ variant = 'error', children }) {
  return (
    <div
      className={`alert alert-${variant}`}
      role={variant === 'error' ? 'alert' : 'status'}
    >
      {children}
    </div>
  )
}

export default Alert
