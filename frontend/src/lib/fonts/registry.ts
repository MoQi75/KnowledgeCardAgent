export const fontRegistry = {
  geist: { label: "Geist" },
  inter: { label: "Inter" },
  notoSans: { label: "Noto Sans" },
  nunitoSans: { label: "Nunito Sans" },
  figtree: { label: "Figtree" },
  roboto: { label: "Roboto" },
  raleway: { label: "Raleway" },
  dmSans: { label: "DM Sans" },
  publicSans: { label: "Public Sans" },
  outfit: { label: "Outfit" },
  geistMono: { label: "Geist Mono" },
  geistPixelSquare: { label: "Geist Pixel Square" },
  jetBrainsMono: { label: "JetBrains Mono" },
  notoSerif: { label: "Noto Serif" },
  robotoSlab: { label: "Roboto Slab" },
  merriweather: { label: "Merriweather" },
  lora: { label: "Lora" },
  playfairDisplay: { label: "Playfair Display" },
} as const;

export type FontKey = keyof typeof fontRegistry;

export const fontOptions = Object.entries(fontRegistry).map(([key, value]) => ({
  key: key as FontKey,
  label: value.label,
}));

export const fontVars = "";
