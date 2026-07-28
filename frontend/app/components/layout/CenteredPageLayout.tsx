/**
 * Shared page layout — centered card on a full-height background.
 *
 * Used by login, signup, health, and any future standalone pages.
 */

interface CenteredPageLayoutProps {
  children: React.ReactNode;
  /** Tailwind max-width class, defaults to "max-w-sm" */
  maxWidth?: string;
}

export function CenteredPageLayout({
  children,
  maxWidth = "max-w-sm",
}: CenteredPageLayoutProps) {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-white px-4 dark:bg-gray-950">
      <div
        className={`w-full ${maxWidth} rounded-xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-900`}
      >
        {children}
      </div>
    </div>
  );
}
