/**
 * HealthCheck — presentational component that displays backend health status.
 *
 * Receives data as props from the route's clientLoader.
 * No useEffect, no useState, no fetch — just renders what it's given.
 */

import { CenteredPageLayout } from "~/components/layout/CenteredPageLayout";

const statusStyles: Record<string, string> = {
  ok: "text-green-600 dark:text-green-400",
  error: "text-red-600 dark:text-red-400",
};

interface HealthCheckProps {
  ok: boolean;
  detail: string;
}

export function HealthCheck({ ok, detail }: HealthCheckProps) {
  const status = ok ? "ok" : "error";

  return (
    <CenteredPageLayout maxWidth="max-w-md">
      <h1 className="mb-4 text-center text-lg font-semibold text-gray-900 dark:text-gray-100">
        Backend health check
      </h1>

      <p className={`mb-4 text-center text-sm font-medium ${statusStyles[status]}`}>
        {ok ? "✅ Backend is healthy" : "❌ Backend unreachable"}
      </p>

      {detail && (
        <pre className="overflow-x-auto rounded-lg border border-gray-200 bg-gray-50 p-3 text-left text-xs text-gray-600 dark:border-gray-800 dark:bg-gray-950 dark:text-gray-400">
          {detail}
        </pre>
      )}
    </CenteredPageLayout>
  );
}