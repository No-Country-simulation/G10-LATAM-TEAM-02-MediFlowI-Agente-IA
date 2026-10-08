import Loader from '../common/Loader';

interface ButtonProps {
  text: string
  type?: 'button' | 'submit'
  loading?: boolean
  disabled?: boolean
  onClick?: () => void
}

const Button = ({ text, type = "button", loading = false, disabled = false, onClick }: ButtonProps) => {
  return (
    <button
      type={type}
      disabled={disabled}
      aria-busy={loading}
      className={`flex h-[42px] items-center justify-center w-full rounded-lg transition-colors duration-200 shadow-sm focus-visible:ring-2 focus-visible:ring-[#204a79] focus-visible:ring-offset-2 ${loading || disabled
        ? 'bg-[#8da4bf] text-white cursor-not-allowed'
        : 'bg-[#204a79] hover:bg-[#18395d] active:bg-[#122b46] text-white cursor-pointer'
        }`}
      onClick={onClick}
    >
      {loading ? (
        <Loader />
      ) : (
        <span
          className="font-bold text-white text-sm tracking-wide"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          {text}
        </span>
      )}
    </button>
  )
}

export default Button;