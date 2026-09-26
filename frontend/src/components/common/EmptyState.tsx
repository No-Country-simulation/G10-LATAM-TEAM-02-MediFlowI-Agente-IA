import { FaFolderOpen } from "react-icons/fa";

interface EmptyStateProps {
  title?: string
  message?: string
  actionLabel?: string
  onAction?: () => void
}

const EmptyState = ({
  title = "No se encontraron registros",
  message = "No hay documentos disponibles para mostrar en este momento.",
  actionLabel,
  onAction
}: EmptyStateProps) => {
  return (
    <div className="clinical-state">
      <div className="clinical-state__content">
        <div className="clinical-state__icon"><FaFolderOpen aria-hidden="true" /></div>
        <h2 className="clinical-state__title">{title}</h2>
        <p className="clinical-state__message">{message}</p>
      {actionLabel && onAction && (
        <button type="button" className="btn btn-primary mt-3 px-4" onClick={onAction}>
          {actionLabel}
        </button>
      )}
      </div>
    </div>
  );
};

export default EmptyState;
