import type { ReceiptSummary } from "~/lib/types";

export function ReceiptSummaryCards({ summary }: { summary: ReceiptSummary }) {
  return (
    <div className="flex gap-4">
      <div className="flex-1 rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
        <p className="text-sm text-gray-600 dark:text-gray-400">Total Receipts Scanned</p>
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          {summary.total_count}
        </h2>
      </div>
      <div className="flex-1 rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
        <p className="text-sm text-gray-600 dark:text-gray-400">Total Amount Spent</p>
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          ${summary.total_sum.toFixed(2)}
        </h2>
      </div>
    </div>
  );
}