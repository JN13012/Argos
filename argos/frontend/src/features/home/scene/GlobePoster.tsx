export function GlobePoster() {
  return (
    <svg className="globe-poster" viewBox="0 0 480 300" aria-hidden="true">
      <defs>
        <radialGradient id="poster-globe" cx="35%" cy="30%">
          <stop offset="0" stopColor="#303342" />
          <stop offset="0.6" stopColor="#151b29" />
          <stop offset="1" stopColor="#0c1019" />
        </radialGradient>
      </defs>
      <g fill="none" stroke="#7568ad" strokeWidth="0.7">
        <ellipse
          cx="250"
          cy="152"
          rx="164"
          ry="49"
          transform="rotate(-24 250 152)"
          opacity="0.45"
        />
        <circle
          cx="250"
          cy="150"
          r="104"
          fill="url(#poster-globe)"
          stroke="#8d7dbc"
        />
        <ellipse cx="250" cy="150" rx="47" ry="104" opacity="0.5" />
        <ellipse cx="250" cy="150" rx="85" ry="104" opacity="0.4" />
        <ellipse cx="250" cy="150" rx="104" ry="36" opacity="0.5" />
        <path
          d="M160 102L240 77L307 135L207 183L286 225"
          stroke="#bc9aff"
          opacity="0.7"
        />
      </g>
      <g fill="#bc9aff">
        <circle cx="160" cy="102" r="3" />
        <circle cx="240" cy="77" r="3" />
        <circle cx="307" cy="135" r="3" />
        <circle cx="207" cy="183" r="3" />
      </g>
      <circle cx="286" cy="225" r="3" fill="#e9c177" />
    </svg>
  );
}
