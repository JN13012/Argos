import type { IconName } from "../components/Icon";

interface NavigationItem {
  label: string;
  icon: IconName;
  available: boolean;
}

// Only implemented destinations are interactive.
export const navigationGroups: readonly (readonly NavigationItem[])[] = [
  [
    { label: "Accueil", icon: "grid", available: true },
    { label: "Red Team", icon: "target", available: false },
    { label: "OSINT", icon: "globe", available: false },
    { label: "Blue Team", icon: "shield", available: false },
  ],
  [
    { label: "Preuves", icon: "folder", available: false },
    { label: "Rapports", icon: "file", available: false },
    { label: "Agents", icon: "users", available: false },
    { label: "Paramètres", icon: "gear", available: false },
  ],
];
