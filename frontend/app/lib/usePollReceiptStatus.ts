import { useEffect, useRef, useState } from "react";
import { useRevalidator } from "react-router";
import { getReceiptStatus } from "./receipts";
import type { ReceiptData } from "./types";

export function usePollReceiptStatus(newReceipt: ReceiptData | null | undefined) {
  const [receipt, setReceipt] = useState<ReceiptData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const revalidator = useRevalidator();

  useEffect(() => {
    if (!newReceipt) return;

    setReceipt(newReceipt);
    setError(null);

    const poll = async () => {
      try {
        const result = await getReceiptStatus(newReceipt.id);
        setReceipt(result);

        if (result.status === "done" || result.status === "failed") {
          if (intervalRef.current) clearInterval(intervalRef.current);
          revalidator.revalidate();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch status");
        if (intervalRef.current) clearInterval(intervalRef.current);
      }
    };

    intervalRef.current = setInterval(poll, 3000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [newReceipt?.id]);

  const isProcessing = receipt !== null && receipt.status !== "done" && receipt.status !== "failed";

  return { receipt, error, isProcessing };
}