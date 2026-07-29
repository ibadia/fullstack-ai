import { apiFetch } from "./api";
import type { ReceiptData, ReceiptSummary } from "./types";

export async function uploadReceiptFromFormData(formData: FormData): Promise<ReceiptData> {
  return apiFetch<ReceiptData>("/api/receipts/analyze/", {
    method: "POST",
    body: formData,
    auth: true,
  });
}

export async function getReceiptStatus(id: number): Promise<ReceiptData> {
  return apiFetch<ReceiptData>(`/api/receipts/${id}/status/`, {
    method: "GET",
    auth: true,
  });
}

export async function listReceipts(): Promise<ReceiptData[]> {
  return apiFetch<ReceiptData[]>("/api/receipts/", {
    method: "GET",
    auth: true,
  });
}

export async function getReceiptSummary(): Promise<ReceiptSummary> {
  return apiFetch<ReceiptSummary>("/api/receipts/summary/", {
    method: "GET",
    auth: true,
  });
}