import { useEffect, useRef, useState } from "react";
import type { ReactNode, RefObject } from "react";
import { BrandLogo } from "../components/BrandLogo";
import { Button } from "../components/Button";
import { Icon } from "../components/Icon";
import { Sidebar } from "./Sidebar";
import "./AppShell.css";

interface AppShellProps {
  children: ReactNode;
  query: string;
  onQueryChange(query: string): void;
  ready: boolean;
  onOpenChat(): void;
  onAbout(): void;
  modalOpen: boolean;
  searchRef: RefObject<HTMLInputElement | null>;
}

export function AppShell({
  children,
  query,
  onQueryChange,
  ready,
  onOpenChat,
  onAbout,
  modalOpen,
  searchRef,
}: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(
    () => window.matchMedia("(max-width: 700px)").matches,
  );
  const menuRef = useRef<HTMLButtonElement>(null);
  const shellRef = useRef<HTMLDivElement>(null);

  function closeSidebar() {
    if (
      shellRef.current
        ?.querySelector("#sidebar")
        ?.contains(document.activeElement)
    )
      menuRef.current?.focus();
    setSidebarOpen(false);
  }

  useEffect(() => {
    const breakpoint = window.matchMedia("(max-width: 700px)");
    const closeOnDesktop = () => {
      setIsMobile(breakpoint.matches);
      if (!breakpoint.matches) setSidebarOpen(false);
    };
    breakpoint.addEventListener("change", closeOnDesktop);
    return () => breakpoint.removeEventListener("change", closeOnDesktop);
  }, []);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") closeSidebar();
      if (
        (event.ctrlKey || event.metaKey) &&
        event.key.toLowerCase() === "k" &&
        ready &&
        !modalOpen &&
        window.innerWidth > 700
      ) {
        event.preventDefault();
        searchRef.current?.focus();
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [ready, modalOpen, searchRef]);

  return (
    <div className="app-shell" ref={shellRef}>
      <a className="skip-link" href="#main-content">
        Aller au contenu
      </a>
      <header className="topbar">
        <button
          type="button"
          className="button button--icon mobile-menu"
          ref={menuRef}
          aria-label={
            sidebarOpen ? "Fermer la navigation" : "Ouvrir la navigation"
          }
          aria-controls="sidebar"
          aria-expanded={sidebarOpen}
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          <Icon name="menu" />
        </button>
        <a className="brand" href="#main-content" aria-label="Argos, accueil">
          <BrandLogo variant="header" />
          <span>ARGOS</span>
        </a>
        <div className="environment">
          <span className="status-dot" />
          <span>Espace local</span>
        </div>
        <label className="global-search">
          <Icon name="search" />
          <input
            ref={searchRef}
            id="global-search"
            type="search"
            placeholder="Rechercher dans le dossier…"
            aria-label="Rechercher dans le dashboard"
            autoComplete="off"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            disabled={!ready}
          />
          <kbd>Ctrl K</kbd>
        </label>
        <div className="header-actions">
          <Button
            variant="icon"
            id="chat-focus"
            aria-label="Ouvrir Argos Chat"
            onClick={onOpenChat}
            disabled={!ready}
          >
            <Icon name="chat" />
          </Button>
          <div className="profile">
            <span className="profile-avatar">A</span>
            <span>
              <strong>Analyste</strong>
              <small>Espace local</small>
            </span>
          </div>
          <Button
            variant="primary"
            className="new-mission"
            disabled
            title="La création de mission sera intégrée dans une prochaine page"
          >
            <Icon name="plus" />
            Nouvelle mission
          </Button>
        </div>
      </header>
      <Sidebar
        open={sidebarOpen}
        hiddenOnMobile={isMobile && !sidebarOpen}
        onNavigate={closeSidebar}
        onAbout={() => {
          closeSidebar();
          onAbout();
        }}
      />
      {sidebarOpen && (
        <button
          type="button"
          className="sidebar-backdrop"
          aria-label="Fermer la navigation"
          onClick={closeSidebar}
        />
      )}
      {children}
    </div>
  );
}
