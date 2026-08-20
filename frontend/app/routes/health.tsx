/**
 * /health route module
 *
 * - React Query: fetches and caches backend health status
 * - meta: sets browser tab title
 * - default export: renders HealthCheck with query data
 *
 * Uses React Query because the health check runs from the user's browser.
 */

import { useQuery } from "@tanstack/react-query";
import { checkBackendHealth } from "~/lib/health";
import { HealthCheck } from "~/components/HealthCheck";
import type { Route } from "./+types/health";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Health Check" },
    { name: "description", content: "Backend health status" },
  ];
}

export default function HealthRoute() {
  const { data, isPending } = useQuery({
    queryKey: ["backend-health"],
    queryFn: checkBackendHealth,
  });

  return (
    <HealthCheck
      ok={data?.ok ?? false}
      detail={data?.detail ?? ""}
      isLoading={isPending}
    />
  );
}
