import wolfKrakenUrl from "../../assets/argos-wolf-kraken.png";

export function BrandLogo() {
  return (
    <span className="brand-mark">
      <img
        className="brand-logo brand-logo--header"
        src={wolfKrakenUrl}
        width={1254}
        height={1254}
        alt=""
      />
    </span>
  );
}
