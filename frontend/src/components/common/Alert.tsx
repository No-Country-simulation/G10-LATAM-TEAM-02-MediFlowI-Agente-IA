import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faExclamationTriangle, faInfoCircle, faXmark } from "@fortawesome/free-solid-svg-icons";

interface AlertProps {
  title: string;
  message?: string;
  onClose?: () => void;
  type: 'success' | 'error' | 'warning' | 'info';
}

const borderColors = {
  success: 'bg-[var(--green)]',
  error: 'bg-[var(--error)]',
  warning: 'bg-[var(--orange)]',
  info: 'bg-[var(--blue)]',
};

const backgroundColors = {
  success: 'bg-[#F6FFF9]',
  error: 'bg-[#FFF5F3]',
  warning: 'bg-[#F7D9A4]',
  info: 'bg-[#F5F9FF]',
};

const icon = {
  success: faCheck,
  error: faXmark,
  warning: faExclamationTriangle,
  info: faInfoCircle,
}

const iconBackgroundColors = {
  success: 'bg-[var(--green)]',
  error: 'bg-[var(--error)]',
  warning: 'bg-[var(--orange)]',
  info: 'bg-[var(--blue)]',
};

const titleColors = {
  success: 'text-[#065f46]',
  error: 'text-[#991b1b]',
  warning: 'text-[#78350f]',
  info: 'text-[#1e3a8a]',
};

const messageColors = {
  success: 'text-[#047857]',
  error: 'text-[#991b1b]',
  warning: 'text-[#78350f]',
  info: 'text-[#1e3a8a]',
};

const Alert = ({ title, message, type = "success", onClose }: AlertProps) => {
  return (
    <div
      role="alert"
      aria-live="polite"
      className={`w-full flex items-start justify-between gap-3 p-3 rounded-xl border ${borderColors[type]} ${backgroundColors[type]} transition-all`}
    >
      <div className="flex items-start gap-2.5">
        <div className={`w-5 h-5 rounded-full ${iconBackgroundColors[type]} flex items-center justify-center shrink-0 mt-0.5`}>
          <FontAwesomeIcon icon={icon[type]} size='2xs' color='#FFF' />
        </div>
        <div className="flex flex-col text-left">
          <h3 className={`font-bold text-xs sm:text-sm ${titleColors[type]}`} style={{ fontFamily: "'Montserrat', sans-serif" }}>
            {title}
          </h3>
          <p className={`text-[11px] sm:text-xs ${messageColors[type]} mt-0.5 leading-snug`}>
            {message}
          </p>
        </div>
      </div>
      <button
        type="button"
        onClick={onClose}
        aria-label="Cerrar notificación"
        className="flex items-center text-slate-400 hover:text-slate-600 transition-colors p-0.5 bg-transparent"
      >
        <FontAwesomeIcon icon={faXmark} size='2xs' color='var(--dark-shade-25)' />
      </button>
    </div>
  )
}

export default Alert;