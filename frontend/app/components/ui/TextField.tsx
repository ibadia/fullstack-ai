/**
 * Reusable text input with proper accessibility.
 *
 * - Renders <label htmlFor> + <input id name> for a11y
 * - Uses name + defaultValue (uncontrolled) so React Router <Form> can read via formData
 * - Supports an optional error message
 */

interface TextFieldProps {
  label: string;
  name: string;
  id?: string;
  type?: React.HTMLInputTypeAttribute;
  required?: boolean;
  defaultValue?: string;
  error?: string;
  autoComplete?: string;
}

export function TextField({
  label,
  name,
  id,
  type = "text",
  required = false,
  defaultValue,
  error,
  autoComplete,
}: TextFieldProps) {
  const fieldId = id ?? name;

  return (
    <div>
      <label
        htmlFor={fieldId}
        className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        {label}
      </label>
      <input
        id={fieldId}
        name={name}
        type={type}
        required={required}
        defaultValue={defaultValue}
        autoComplete={autoComplete}
        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 outline-none transition focus:border-gray-900 focus:ring-1 focus:ring-gray-900 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-100 dark:focus:border-gray-100 dark:focus:ring-gray-100"
      />
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
}
