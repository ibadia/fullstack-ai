interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function Button({
  variant = "primary",
  className = "",
  children,
  ...rest
}: ButtonProps) {
  const baseStyles =
    "rounded-lg py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60";

  const variantStyles = {
    primary:
      "bg-gray-900 text-white hover:bg-gray-700 dark:bg-gray-100 dark:text-gray-900 dark:hover:bg-gray-300",
    secondary:
      "border border-gray-300 text-gray-900 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-100 dark:hover:bg-gray-900",
  };

  return (
    <button className={`${baseStyles} ${variantStyles[variant]} ${className}`} {...rest}>
      {children}
    </button>
  );
}