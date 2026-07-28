/**
 * /health route module
 *
 * - clientLoader: fetches health status before render (no loading flash)
 * - meta: sets browser tab title
 * - default export: renders HealthCheck with loader data
 *
 * Uses clientLoader because the health check runs from the user's browser.
 */

import { useLoaderData } from "react-router";
import { checkBackendHealth } from "~/lib/health";
import { HealthCheck } from "~/components/HealthCheck";
import type { Route } from "./+types/health";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Health Check" },
    { name: "description", content: "Backend health status" },
  ];
}

export async function clientLoader({}: Route.ClientLoaderArgs) {
  return await checkBackendHealth();
}

export default function HealthRoute() {
  const data = useLoaderData<typeof clientLoader>();

  return <HealthCheck ok={data.ok} detail={data.detail} />;
}
