import { FaExclamationTriangle } from "react-icons/fa";

interface ErrorMessageProps {
  title?: string
  message?: string
  onRetry?: () => void | Promise<void>
}

const ErrorMessage = ({
  title = "Ocurrió un error",
  message = "No fue posible comunicarse con el servicio. Por favor, reintente más tarde.",
  onRetry
}: ErrorMessageProps) => {
  return (
    <div className="clinical-state" role="alert">
      <div className="clinical-state__content">
        <div className="clinical-state__icon bg-danger bg-opacity-10 text-danger">
          <FaExclamationTriangle aria-hidden="true" />
        </div>
        <h2 className="clinical-state__title">{title}</h2>
        <p className="clinical-state__message">{message}</p>
        {onRetry && (
          <button type="button" className="btn btn-outline-danger mt-3 px-4" onClick={onRetry}>
            Intentar nuevamente
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;
