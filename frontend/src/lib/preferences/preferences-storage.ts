import { PREFERENCE_PERSISTENCE, type PreferenceKey } from "@/lib/preferences/preferences-config";

const maxAge = 60 * 60 * 24 * 365;

function setCookie(key: string, value: string) {
  /* biome-ignore lint/suspicious/noDocumentCookie: preference cookies are read by the Next.js layout on the next request. */
  document.cookie = `${encodeURIComponent(key)}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; samesite=lax`;
}

export async function persistPreference(key: PreferenceKey, value: string) {
  const persistence = PREFERENCE_PERSISTENCE[key];

  if (persistence === "localStorage") {
    window.localStorage.setItem(key, value);
    return;
  }

  setCookie(key, value);
}
