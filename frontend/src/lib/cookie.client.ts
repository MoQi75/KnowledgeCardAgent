export function setClientCookie(key: string, value: string, maxAge = 60 * 60 * 24 * 7) {
  /* biome-ignore lint/suspicious/noDocumentCookie: cookie persistence keeps server-rendered layout preferences in sync. */
  document.cookie = `${encodeURIComponent(key)}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; samesite=lax`;
}
