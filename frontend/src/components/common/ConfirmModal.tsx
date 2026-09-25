interface ConfirmModalProps {
  show: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  variant?: 'primary' | 'danger' | 'warning' | 'success'
  onConfirm: () => void
  onCancel: () => void
  loading?: boolean
}

const ConfirmModal = ({
  show,
  title = "Confirmar Acción",
  message = "¿Está seguro de realizar esta acción?",
  confirmText = "Confirmar",
  cancelText = "Cancelar",
  variant = "primary",
  onConfirm,
  onCancel,
  loading = false
}: ConfirmModalProps) => {
  if (!show) return null;

  return (
    <div className="modal fade show d-block" tabIndex={-1} style={{ backgroundColor: "rgba(0,0,0,0.5)" }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content shadow">
          <div className="modal-header">
            <h5 className="modal-title fw-bold">{title}</h5>
            <button type="button" className="btn-close" aria-label="Close" onClick={onCancel} disabled={loading}></button>
          </div>
          <div className="modal-body">
            <p className="mb-0">{message}</p>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={loading}>
              {cancelText}
            </button>
            <button type="button" className={`btn btn-${variant}`} onClick={onConfirm} disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Procesando...
                </>
              ) : (
                confirmText
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
