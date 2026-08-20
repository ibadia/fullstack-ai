/**
 * /signup route module
 *
 * - clientAction: handles form submission (email + password + confirm → auth service → redirect)
 * - meta: sets browser tab title
 * - default export: renders SignupForm with any action errors
 */

import { redirect, useActionData, useNavigation } from "react-router";
import { signup, storeTokens } from "~/lib/auth";
import { signupSchema } from "~/lib/validation";
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
  const result = signupSchema.safeParse(Object.fromEntries(formData));

  if (!result.success) {
    return { error: result.error.issues[0]?.message ?? "Invalid form data." };
  }

  try {
    const tokens = await signup(
      result.data.email,
      result.data.password,
      result.data.confirm_password
    );
    storeTokens(tokens);
    return redirect("/login");
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
