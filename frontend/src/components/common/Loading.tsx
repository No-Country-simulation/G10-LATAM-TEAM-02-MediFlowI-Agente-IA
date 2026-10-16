import Loader from "./Loader";

interface LoadingProps { message?: string }

const Loading = ({ message = "Cargando información..." }: LoadingProps) => {
  return (
    <div className="clinical-state" role="status" aria-live="polite" aria-busy="true">
      <div className="clinical-state__content">
        <div className="clinical-state__icon">
          <Loader size="lg" />
        </div>
        <h2 className="text-2xl font-bold text-[var(--primary)]">Preparando información</h2>
        <p className="text-lg font-medium">{message}</p>
        <span className="visually-hidden">Cargando</span>
      </div>
    </div>
  );
};

export default Loading;
