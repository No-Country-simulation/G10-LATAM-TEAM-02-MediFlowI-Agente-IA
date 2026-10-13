import "../../styles/loader.css";

interface LoaderProps {
  size?: "xs" | "sm" | "md" | "lg";
}

const Loader = ({ size = "md" }: LoaderProps) => {
  return (
    <div aria-live="assertive" aria-hidden="true" role="alert" className={`loader loader--${size}`}></div>
  )
}

export default Loader;