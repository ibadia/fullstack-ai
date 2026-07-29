import { Form } from "react-router";
import { FileField } from "~/components/ui/FileField";
import { Button } from "~/components/ui/Button";

interface ReceiptUploadFormProps {
  isSubmitting: boolean;
  isProcessing: boolean;
  uploadError?: string;
  processingError?: string | null;
}

export function ReceiptUploadForm({
  isSubmitting,
  isProcessing,
  uploadError,
  processingError,
}: ReceiptUploadFormProps) {
  return (
    <Form method="post" encType="multipart/form-data" className="space-y-4">
      <div className="rounded-lg border-2 border-dashed border-gray-300 p-6 text-center dark:border-gray-700">
        <p className="mb-2 text-sm text-gray-600 dark:text-gray-400">
          Upload a receipt image
        </p>
        <FileField
          label="Receipt image"
          name="image"
          accept="image/jpeg,image/png"
          required
        />
      </div>

      {uploadError && (
        <p className="text-sm text-red-600 dark:text-red-400">{uploadError}</p>
      )}
      {processingError && (
        <p className="text-sm text-red-600 dark:text-red-400">{processingError}</p>
      )}
      {isProcessing && (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Analyzing your receipt, please wait...
        </p>
      )}

      <Button type="submit" disabled={isSubmitting || isProcessing}>
        {isSubmitting ? "Uploading..." : "Analyze Receipt"}
      </Button>
    </Form>
  );
}