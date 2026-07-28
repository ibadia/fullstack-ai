/**
 * /login route module
 *
 * - clientAction: handles form submission (email + password → auth service → redirect)
 * - meta: sets browser tab title
 * - default export: renders LoginForm with any action errors
 *
 * Uses clientAction (not server action) because storeTokens uses sessionStorage (browser-only).
 */

import { redirect, useActionData, useNavigation } from "react-router";
import { login, storeTokens } from "~/lib/auth";
import { LoginForm } from "~/components/LoginForm";
import type { Route } from "./+types/login";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Log in" },
    { name: "description", content: "Log in to your account" },
  ];
}

export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData();
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  try {
    const tokens = await login(email, password);
    storeTokens(tokens);
    return redirect("/");
  } catch (err) {
    return {
      error: err instanceof Error ? err.message : "Something went wrong",
    };
  }
}

export default function LoginRoute() {
  const actionData = useActionData<typeof clientAction>();
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";

  return (
    <LoginForm
      error={actionData && "error" in actionData ? actionData.error : undefined}
      isSubmitting={isSubmitting}
    />
  );
}
