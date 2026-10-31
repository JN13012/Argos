import type { ComponentProps } from "react";

type ButtonVariant = "primary" | "secondary" | "quiet" | "icon";
type ButtonProps = ComponentProps<"button"> & { variant?: ButtonVariant };

const baseStyles =
  "inline-flex items-center justify-center gap-[9px] rounded-[7px] border border-solid text-[12px] font-medium transition-[background,border-color,color] duration-[160ms] ease-[ease] disabled:opacity-70";

// Each variant supplies its own dimensions and colors, without competing utilities.
const variants: Record<ButtonVariant, string> = {
  primary:
    "min-h-[38px] px-[14px] py-[9px] border-action bg-action text-action-foreground enabled:hover:bg-action-hover disabled:border-action-disabled-border disabled:bg-action-disabled disabled:text-action-disabled-foreground [&_.icon]:size-4",
  secondary:
    "min-h-[38px] px-[14px] py-[9px] border-secondary-action-border bg-secondary-action text-secondary-action-foreground enabled:hover:border-secondary-action-hover-border enabled:hover:bg-secondary-action-hover [&_.icon]:size-4",
  quiet:
    "min-h-8 px-0 py-1 border-transparent text-accent hover:text-link-hover [&_.icon]:size-4",
  icon: "size-[38px] min-h-[38px] p-0 border-transparent text-muted enabled:hover:bg-surface-raised enabled:hover:text-foreground [&_.icon]:size-[19px]",
};

export function buttonClassName(variant: ButtonVariant, className = "") {
  return (
    "button button--" +
    variant +
    " " +
    baseStyles +
    " " +
    variants[variant] +
    " " +
    className
  );
}

export function Button({
  variant = "secondary",
  type = "button",
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={buttonClassName(variant, className)}
      {...props}
    />
  );
}
