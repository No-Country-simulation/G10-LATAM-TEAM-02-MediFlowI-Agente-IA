
interface FooterDividerProps {
  lightText: string;
  boldText: string;
  onNavigate?: () => void;
}

const FooterDivider = ({ lightText, boldText, onNavigate }: FooterDividerProps) => {
  return (
    <div>
      <div className="flex items-center gap-3 w-full my-0.5">
        <div className="flex-1 h-px bg-[rgba(31,32,65,0.1)]" />
        <span
          className="font-bold text-xs text-[rgba(31,32,65,0.4)] tracking-wider"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          OR
        </span>
        <div className="flex-1 h-px bg-[rgba(31,32,65,0.1)]" />
      </div>

      <footer className="flex items-center justify-center gap-1.5 w-full text-xs sm:text-sm">
        <span
          className="font-normal text-[rgba(31,32,65,0.5)]"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          {lightText}
        </span>
        <button
          type="button"
          onClick={onNavigate || (() => { window.location.href = '/login'; })}
          className="bg-transparent font-bold text-[#204a79] hover:text-[#18395d] hover:underline focus-visible:underline transition-colors cursor-pointer"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          {boldText}
        </button>
      </footer>
    </div >
  )
}

export default FooterDivider;