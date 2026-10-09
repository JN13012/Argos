import logoUrl from "../../assets/argos-mascot.png";

export function BrandLogo({ variant }: { variant: "header" | "welcome" }) {
  const image = (
    <img
      className={`brand-logo brand-logo--${variant} ${variant === "welcome" ? "mascot" : ""}`}
      src={logoUrl}
      width={1024}
      height={1536}
      alt={
        variant === "welcome"
          ? "Mascotte Argos, chien robotique aux yeux bleus"
          : ""
      }
    />
  );
  return variant === "header" ? (
    <span className="brand-mark">{image}</span>
  ) : (
    image
  );
}
