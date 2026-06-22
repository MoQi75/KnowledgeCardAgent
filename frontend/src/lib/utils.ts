import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getInitials(name: string | null | undefined) {
  if (!name) return "";

  const parts = name
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (parts.length === 0) return "";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();

  return `${parts[0][0] ?? ""}${parts[parts.length - 1][0] ?? ""}`.toUpperCase();
}

type FormatCurrencyOptions = Intl.NumberFormatOptions & {
  currency?: string;
  locale?: string;
  noDecimals?: boolean;
};

export function formatCurrency(value: number, options: FormatCurrencyOptions | string = {}, locale = "en-US") {
  const formatOptions: FormatCurrencyOptions = typeof options === "string" ? { currency: options, locale } : options;
  const { currency = "USD", locale: optionLocale = locale, noDecimals, ...intlOptions } = formatOptions;
  const fractionOptions = noDecimals
    ? {
        maximumFractionDigits: 0,
        minimumFractionDigits: 0,
      }
    : {};

  return new Intl.NumberFormat(optionLocale, {
    style: "currency",
    currency,
    ...fractionOptions,
    ...intlOptions,
  }).format(value);
}
