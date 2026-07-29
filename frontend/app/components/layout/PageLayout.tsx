interface PageLayoutProps {
  children: React.ReactNode;
  maxWidth?: string;
}

export function PageLayout({ children, maxWidth = "max-w-4xl" }: PageLayoutProps) {
  return (
    <div className="min-h-screen w-full bg-white px-4 py-8 dark:bg-gray-950">
      <div className={`mx-auto w-full ${maxWidth}`}>{children}</div>
    </div>
  );
}