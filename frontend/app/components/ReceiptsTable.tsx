import { useSearchParams } from "react-router";
import { Button } from "~/components/ui/Button";
import type { ReceiptData } from "~/lib/types";

export function ReceiptsTable({ receipts }: { receipts: ReceiptData[] }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedId = searchParams.get("selected");
  const selected = receipts.find((r) => String(r.id) === selectedId) ?? null;

  const handleSelect = (id: number) => {
    setSearchParams({ selected: String(id) });
  };

  const handleClose = () => {
    setSearchParams({});
  };

  return (
    <div>
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="text-left text-sm font-medium text-gray-600 dark:text-gray-400">
              Date
            </th>
            <th className="text-left text-sm font-medium text-gray-600 dark:text-gray-400">
              Store Name
            </th>
            <th className="text-left text-sm font-medium text-gray-600 dark:text-gray-400">
              Total Amount
            </th>
            <th className="text-left text-sm font-medium text-gray-600 dark:text-gray-400">
              Details
            </th>
          </tr>
        </thead>
        <tbody>
          {receipts.map((r) => (
            <tr key={r.id} className="border-t border-gray-200 dark:border-gray-800">
              <td className="py-2 text-sm text-gray-900 dark:text-gray-100">
                {new Date(r.created_at).toLocaleDateString()}
              </td>
              <td className="py-2 text-sm text-gray-900 dark:text-gray-100">
                {(r.extracted_data?.merchant_name as string) ?? "-"}
              </td>
              <td className="py-2 text-sm text-gray-900 dark:text-gray-100">
                {r.total_amount ?? "-"}
              </td>
              <td className="py-2 text-sm">
                <Button variant="secondary" onClick={() => handleSelect(r.id)}>
                  View Details
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selected && (
        <div className="mt-4 rounded-lg border border-gray-200 p-4 dark:border-gray-800">
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
          <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-gray-100">
            Receipt #{selected.id}
          </h3>
          <pre className="mt-2 overflow-x-auto rounded-lg bg-gray-50 p-3 text-xs text-gray-600 dark:bg-gray-950 dark:text-gray-400">
            {JSON.stringify(selected.extracted_data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}