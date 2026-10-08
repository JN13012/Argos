import type { SVGProps } from "react";

// Original local icon geometry. Decorative by default; label the surrounding control.
const drawings = {
  shield: (
    <>
      <path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z" />
      <path d="m8.5 12 2.5 2.5 4.5-5" />
    </>
  ),
  "eye-shield": (
    <>
      <path d="m12 2 9 3.5V12c0 6-9 10-9 10S3 18 3 12V5.5z" />
      <path d="M7 11.5s2-3 5-3 5 3 5 3-2 3-5 3-5-3-5-3Z" />
      <circle cx="12" cy="11.5" r="1.1" />
    </>
  ),
  grid: (
    <>
      <rect x="3" y="3" width="6" height="6" rx="1.3" />
      <rect x="15" y="3" width="6" height="6" rx="1.3" />
      <rect x="3" y="15" width="6" height="6" rx="1.3" />
      <rect x="15" y="15" width="6" height="6" rx="1.3" />
    </>
  ),
  target: (
    <>
      <circle cx="12" cy="12" r="8" />
      <circle cx="12" cy="12" r="4" />
      <path d="M12 1v4m0 14v4M1 12h4m14 0h4" />
    </>
  ),
  globe: (
    <>
      <circle cx="12" cy="12" r="9" />
      <ellipse cx="12" cy="12" rx="4" ry="9" />
      <path d="M3 12h18M5 7h14M5 17h14" />
    </>
  ),
  folder: (
    <>
      <path d="M3 6a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    </>
  ),
  file: (
    <>
      <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6M8 13h8M8 17h6" />
    </>
  ),
  users: (
    <>
      <circle cx="9" cy="8" r="3" />
      <path d="M3 20v-2a6 6 0 0 1 12 0v2M17 5a3 3 0 0 1 0 6m1 3a5 5 0 0 1 4 5" />
    </>
  ),
  gear: (
    <>
      <path d="m9 3-1 3-3 1-2 3 2 2-1 3 3 2 3-1 2 3 3-1 1-3 3-1 1-3-2-2 1-3-3-2-3 1-2-2z" />
      <circle cx="12" cy="11" r="3" />
    </>
  ),
  search: (
    <>
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="m16 16 5 5" />
    </>
  ),
  bell: (
    <>
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" />
    </>
  ),
  chat: (
    <>
      <path d="M4 4h16v13H9l-5 4z" />
      <path d="M8 9h8M8 13h5" />
    </>
  ),
  plus: (
    <>
      <path d="M12 5v14M5 12h14" />
    </>
  ),
  chevron: (
    <>
      <path d="m9 5 7 7-7 7" />
    </>
  ),
  arrow: (
    <>
      <path d="M4 12h16m-6-6 6 6-6 6" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  check: (
    <>
      <path d="m5 12 4 4L19 6" />
    </>
  ),
  alert: (
    <>
      <path d="m12 3 10 18H2zM12 9v5M12 17v.1" />
    </>
  ),
  agent: (
    <>
      <path d="m12 2 9 5v10l-9 5-9-5V7z" />
      <rect x="7" y="8" width="10" height="8" rx="2" />
      <path d="M12 5v3M9 11v1M15 11v1M10 15h4" />
    </>
  ),
  clipboard: (
    <>
      <path d="M8 5H5v16h14V5h-3" />
      <rect x="8" y="3" width="8" height="5" rx="1" />
      <path d="m8 14 2 2 5-5" />
    </>
  ),
  terminal: (
    <>
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m6 9 4 3-4 3M13 15h5" />
    </>
  ),
  filter: (
    <>
      <path d="M3 5h18l-7 8v6l-4 2v-8z" />
    </>
  ),
  send: (
    <>
      <path d="m3 3 18 9-18 9 4-9zM7 12h14" />
    </>
  ),
  expand: (
    <>
      <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
    </>
  ),
  close: (
    <>
      <path d="m6 6 12 12M6 18 18 6" />
    </>
  ),
  lock: (
    <>
      <rect x="5" y="10" width="14" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" />
    </>
  ),
  download: (
    <>
      <path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5" />
    </>
  ),
  menu: (
    <>
      <path d="M4 6h16M4 12h16M4 18h16" />
    </>
  ),
  info: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v6M12 7v.1" />
    </>
  ),
};

export type IconName = keyof typeof drawings;

interface IconProps extends SVGProps<SVGSVGElement> {
  name: IconName;
}

export function Icon({ name, className = "", ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={`icon ${className}`}
      aria-hidden="true"
      focusable="false"
      {...props}
    >
      {drawings[name]}
    </svg>
  );
}
