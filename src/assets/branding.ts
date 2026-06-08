const brandingModules = import.meta.glob("./branding/*.png", {
  eager: true,
  import: "default",
  query: "?url",
}) as Record<string, string>;

export const companyLogoUrl = brandingModules["./branding/company-logo.png"] ?? null;
