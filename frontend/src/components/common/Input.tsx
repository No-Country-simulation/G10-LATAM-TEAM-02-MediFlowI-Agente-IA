import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from '@fortawesome/free-regular-svg-icons';
import cn from "../../utils/cn";

interface InputProps {
  type: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url' | 'search' | 'date' | 'time' | 'datetime-local';
  name: string;
  value: string;
  onChange: (name: string, value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label: string;
  inputMode?: "numeric" | "decimal" | "tel" | "email" | "url" | "search" | "text";
  maxLength?: number;
}

const fieldCardBase =
  'flex flex-col items-start px-3.5 py-1.5 rounded-lg border transition-all shadow-[0_2px_8px_rgba(31,32,65,0.03)]';
const fieldCardEnabled = cn(
  "bg-white border-[#2c5282] text-[rgba(31,32,65,0.5)] cursor-text",
  'hover:border-[#2c5282] focus-within:text-[#2c5282] focus-within:border-[#2c5282] focus-within:ring-2 focus-within:ring-[#2c5282]'
);
const fieldCardDisabled = 'bg-[#e9ecef] border-[rgba(31,32,65,0.08)] opacity-80 cursor-not-allowed';
const fieldCardError = cn(
  'bg-white border-[#F72C2C] text-[#F72C2C] cursor-text',
  "hover:border-[#F72C2C]",
  "focus-within:border-[#F72C2C] focus-within:ring-2 focus-within:ring-[#F72C2C]"
);
const inputBase =
  'w-full font-medium text-xs sm:text-sm placeholder:text-[rgba(31,32,65,0.35)] outline-none bg-transparent pt-0.5';


const Input = ({ type = "text", name = "inputText", value = "", onChange, placeholder = "", label = "Label", error = "", disabled = false, inputMode = "text", maxLength = 30 }: InputProps) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className={cn(`flex flex-col w-full ${type === "password" ? 'gap-1' : ''}`)}>
      <label
        htmlFor={name}
        className={`${fieldCardBase} ${disabled ? fieldCardDisabled : error?.trim() ? fieldCardError : fieldCardEnabled
          }`}
      >
        <div className="flex items-center w-full">
          <div className="flex flex-col w-full">
            <span
              className="font-bold text-[10px] sm:text-[11px] tracking-[0.06px] uppercase"
              style={{ fontFamily: "'Montserrat', sans-serif" }}
            >
              {label}
            </span>
            <input
              id={name}
              name={name}
              type={type === "password" ? (showPassword ? 'text' : 'password') : type}
              value={value}
              autoComplete="off"
              disabled={disabled}
              inputMode={inputMode}
              maxLength={maxLength}
              placeholder={placeholder}
              onChange={inputMode === "numeric" ? (e) => onChange(name, e.target.value.replace(/\D/g, '')) : (e) => onChange(name, e.target.value)}
              className={`${inputBase} ${disabled ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'
                }`}
              style={{ fontFamily: "'Quicksand', sans-serif" }}
            />
          </div>
          {type === "password" && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              disabled={disabled}
              aria-label={showPassword ? 'Ocultar contraseña' : 'Ver contraseña'}
              className="bg-transparent flex items-center text-slate-400 hover:text-slate-600 focus:outline-none p-1 shrink-0"
            >
              {showPassword ? (
                <FontAwesomeIcon icon={faEye} />
              ) : (
                <FontAwesomeIcon icon={faEyeSlash} />
              )}
            </button>
          )}
        </div>
      </label>
      {error?.trim() && (
        <p className="text-red-500 text-xs mt-1 text-left font-normal pl-1">
          {error}
        </p>
      )}
    </div>
  )
}

export default Input;