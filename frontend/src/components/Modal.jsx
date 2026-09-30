import { useEffect, useRef } from 'react'

// A pop-up built on the browser's <dialog> element, which already handles
// moving focus inside, the Escape key and the dark backdrop for us.
// isBusy: while a request is running, Escape does not close the pop-up.
function Modal({ titleId, onClose, isBusy = false, children }) {
  const dialogRef = useRef(null)

  useEffect(() => {
    const dialog = dialogRef.current
    const previouslyFocused = document.activeElement

    if (!dialog.open) {
      dialog.showModal()
    }

    // When the pop-up closes, put keyboard focus back on the button that opened it.
    return () => {
      dialog.close()
      previouslyFocused?.focus()
    }
  }, [])

  // Runs when the user presses Escape.
  function handleCancel(event) {
    event.preventDefault()

    if (!isBusy) {
      onClose()
    }
  }

  return (
    <dialog
      ref={dialogRef}
      className="modal"
      aria-labelledby={titleId}
      onCancel={handleCancel}
    >
      {children}
    </dialog>
  )
}

export default Modal