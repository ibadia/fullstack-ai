/**
 * LoginForm — presentational component for the login page.
 *
 * All mutation logic lives in the route's clientAction.
 * This component just renders the form UI and displays errors.
 */

import { Form, Link } from "react-router";
import { CenteredPageLayout } from "~/components/layout/CenteredPageLayout";
import { TextField } from "~/components/ui/TextField";

interface LoginFormProps {
  error?: string;
  isSubmitting: boolean;
}

export function LoginForm({ error, isSubmitting }: LoginFormProps) {
  return (
    <CenteredPageLayout>
      <h1 className="mb-6 text-xl font-semibold text-gray-900 dark:text-gray-100">
        Log in
      </h1>

      <Form method="post" className="space-y-4">
        <TextField
          label="Email"
          name="email"
          type="email"
          required
          autoComplete="email"
        />
        <TextField
          label="Password"
          name="password"
          type="password"
          required
          autoComplete="current-password"
        />

        {error && (
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-lg bg-gray-900 py-2.5 text-sm font-semibold text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-gray-100 dark:text-gray-900 dark:hover:bg-gray-300"
        >
          {isSubmitting ? "Logging in…" : "Log in"}
        </button>
      </Form>

      <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
        Don&apos;t have an account?{" "}
        <Link
          to="/signup"
          className="font-semibold text-gray-900 hover:underline dark:text-gray-100"
        >
          Sign up
        </Link>
      </p>
    </CenteredPageLayout>
  );
}