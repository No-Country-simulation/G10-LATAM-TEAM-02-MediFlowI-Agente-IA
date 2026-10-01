import { Component, type ErrorInfo, type ReactNode } from 'react'
import { FaExclamationTriangle, FaRedo, FaHome } from 'react-icons/fa'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary capturó un fallo no controlado en React:', error, errorInfo)
    this.setState({ errorInfo })
  }

  handleReload = () => {
    window.location.reload()
  }

  handleGoDashboard = () => {
    window.location.href = '/dashboard'
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light p-4">
          <div
            className="card border-0 shadow-lg rounded-4 overflow-hidden text-center p-4 p-md-5"
            style={{ maxWidth: '580px', width: '100%' }}
            role="alert"
          >
            <div className="d-inline-flex p-3 bg-danger bg-opacity-10 text-danger rounded-circle mb-3 mx-auto">
              <FaExclamationTriangle size={48} />
            </div>

            <h3 className="fw-bold text-dark mb-2">Interrupción en la Interfaz Clínica</h3>
            <p className="text-muted mb-4 small">
              Se detectó un error inesperado al renderizar el módulo clínico. Los datos en el
              servidor están seguros. Por favor, reintente la acción o regrese al panel principal.
            </p>

            <div className="d-flex flex-column flex-sm-row justify-content-center gap-2 mb-4">
              <button
                type="button"
                className="btn btn-primary d-flex align-items-center justify-content-center gap-2 px-4 py-2 rounded-3 shadow-sm fw-semibold"
                onClick={this.handleReload}
              >
                <FaRedo size={14} /> Recargar Módulo
              </button>
              <button
                type="button"
                className="btn btn-outline-secondary d-flex align-items-center justify-content-center gap-2 px-4 py-2 rounded-3 fw-semibold"
                onClick={this.handleGoDashboard}
              >
                <FaHome size={14} /> Ir al Dashboard
              </button>
            </div>

            {this.state.error && (
              <details className="text-start mt-2 border rounded-3 p-3 bg-white small text-muted">
                <summary className="cursor-pointer fw-semibold text-secondary">
                  Detalles técnicos del incidente
                </summary>
                <p className="mt-2 text-danger font-monospace mb-1 small">
                  {this.state.error.toString()}
                </p>
                {this.state.errorInfo?.componentStack && (
                  <pre
                    className="overflow-auto p-2 bg-light rounded text-dark font-monospace mb-0"
                    style={{ maxHeight: '140px', fontSize: '0.75rem' }}
                  >
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
