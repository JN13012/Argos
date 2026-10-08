import logoUrl from "../../assets/argos-wolf-kraken.png";

export function BrandLogo({ variant }: { variant: "header" | "welcome" }) {
  return (
    <img
      className={`brand-logo brand-logo--${variant}`}
      src={logoUrl}
      width={1254}
      height={1254}
      alt={
        variant === "welcome"
          ? "Emblème Argos, loup et kraken cybernétiques"
          : ""
      }
    />
  );
}
