// Temporary cuthentication checking tab

import type { Route } from "./+types/authenticated";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Authenticated" },
    { name: "description", content: "User is authenticated" },
  ];
}

export default function AuthenticatedRoute() {
  return <p>You are authenticated.</p>;
}