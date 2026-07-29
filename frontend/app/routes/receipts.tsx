import { useLoaderData, useActionData, useNavigation } from "react-router";
import { listReceipts, getReceiptSummary, uploadReceiptFromFormData } from "~/lib/receipts";
import { usePollReceiptStatus } from "~/lib/usePollReceiptStatus";
import { PageLayout } from "~/components/layout/PageLayout";
import { ReceiptUploadForm } from "~/components/ReceiptUploadForm";
import { ReceiptSummaryCards } from "~/components/ReceiptSummaryCards";
import { ReceiptsTable } from "~/components/ReceiptsTable";
import type { Route } from "./+types/receipts";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Receipts" },
    { name: "description", content: "Upload and review your receipts" },
  ];
}

export async function clientLoader({}: Route.ClientLoaderArgs) {
  const [receipts, summary] = await Promise.all([listReceipts(), getReceiptSummary()]);
  return { receipts, summary };
}

export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData();
  const image = formData.get("image");

  if (!image || !(image instanceof File) || image.size === 0) {
    return { error: "Please select an image to upload" };
  }

  try {
    const receipt = await uploadReceiptFromFormData(formData);
    return { receipt, error: undefined };
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Upload failed" };
  }
}

export default function ReceiptsRoute() {
  const { receipts, summary } = useLoaderData<typeof clientLoader>();
  const actionData = useActionData<typeof clientAction>();
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";

  const { isProcessing, error: processingError } = usePollReceiptStatus(actionData?.receipt);

  return (
    <PageLayout>
      <div className="space-y-6">
        <ReceiptSummaryCards summary={summary} />

        <ReceiptUploadForm
          isSubmitting={isSubmitting}
          isProcessing={isProcessing}
          uploadError={actionData?.error}
          processingError={processingError}
        />

        <ReceiptsTable receipts={receipts} />
      </div>
    </PageLayout>
  );
}

export function shouldRevalidate({ currentUrl, nextUrl, defaultShouldRevalidate }: Route.ShouldRevalidateArgs) {
  // Skip revalidation if only the "selected" search param changed
  const currentParams = new URLSearchParams(currentUrl.search);
  const nextParams = new URLSearchParams(nextUrl.search);
  currentParams.delete("selected");
  nextParams.delete("selected");

  if (currentParams.toString() === nextParams.toString() && currentUrl.pathname === nextUrl.pathname) {
    return false;
  }

  return defaultShouldRevalidate;
}