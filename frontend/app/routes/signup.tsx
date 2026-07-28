/**
 * /signup route module
 *
 * - clientAction: handles form submission (email + password + confirm → auth service → redirect)
 * - meta: sets browser tab title
 * - default export: renders SignupForm with any action errors
 */

import { redirect, useActionData, useNavigation } from "react-router";
import { signup, storeTokens } from "~/lib/auth";
import { SignupForm } from "~/components/SignupForm";
import type { Route } from "./+types/signup";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Sign up" },
    { name: "description", content: "Create a new account" },
  ];
}

export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData();
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const confirmPassword = formData.get("confirm_password") as string;

  // Client-side validation: passwords must match
  if (password !== confirmPassword) {
    return { error: "Passwords do not match." };
  }

  try {
    const tokens = await signup(email, password, confirmPassword);
    storeTokens(tokens);
    return redirect("/");
  } catch (err) {
    return {
      error: err instanceof Error ? err.message : "Something went wrong",
    };
  }
}

export default function SignupRoute() {
  const actionData = useActionData<typeof clientAction>();
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";

  return (
    <SignupForm
      error={actionData && "error" in actionData ? actionData.error : undefined}
      isSubmitting={isSubmitting}
    />
  );
}
