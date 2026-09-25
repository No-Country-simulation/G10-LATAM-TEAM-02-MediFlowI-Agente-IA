interface LoadingProps { message?: string }

const Loading = ({ message = "Cargando información..." }: LoadingProps) => {
  return (
    <div className="clinical-state" role="status" aria-live="polite" aria-busy="true">
      <div className="clinical-state__content">
        <div className="clinical-state__icon">
          <div className="spinner-border spinner-border-sm" aria-hidden="true" />
        </div>
        <h2 className="clinical-state__title">Preparando información</h2>
        <p className="clinical-state__message">{message}</p>
        <span className="visually-hidden">Cargando</span>
      </div>
    </div>
  );
};

export default Loading;
