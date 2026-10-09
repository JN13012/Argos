import { Button } from "../components/Button";
import { Icon } from "../components/Icon";
import { navigationGroups } from "./navigation";

interface SidebarProps {
  open: boolean;
  hiddenOnMobile: boolean;
  onNavigate(): void;
  onAbout(): void;
}

export function Sidebar({
  open,
  hiddenOnMobile,
  onNavigate,
  onAbout,
}: SidebarProps) {
  return (
    <aside
      className={`sidebar ${open ? "open" : ""}`}
      id="sidebar"
      aria-label="Navigation principale"
      inert={hiddenOnMobile}
    >
      <p className="nav-section-label">ESPACE DE TRAVAIL</p>
      <nav className="navigation" aria-label="Espaces Argos">
        {navigationGroups.map((group, index) => (
          <div className="navigation-group" key={index}>
            {group.map((item) =>
              item.available ? (
                <a
                  key={item.label}
                  className="nav-item active"
                  href="#main-content"
                  aria-current="page"
                  onClick={onNavigate}
                >
                  <Icon name={item.icon} />
                  <span>{item.label}</span>
                  <span className="active-dot" />
                </a>
              ) : (
                <button
                  key={item.label}
                  type="button"
                  className="nav-item"
                  disabled
                  title="Cet espace sera disponible dans une prochaine version"
                >
                  <Icon name={item.icon} />
                  <span>{item.label}</span>
                </button>
              ),
            )}
          </div>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="local-status">
          <span className="eyebrow">ENVIRONNEMENT LOCAL</span>
          <strong>
            <span className="status-dot" />
            MODE DÉMONSTRATION
          </strong>
          <p>Explorez l’interface avec des données synthétiques.</p>
          <Button variant="quiet" onClick={onAbout}>
            À propos d’Argos <Icon name="arrow" />
          </Button>
        </div>
        <div className="sidebar-footer">
          <Icon name="lock" />
          <span>
            Argos Core <strong>0.1.0</strong>
          </span>
        </div>
      </div>
    </aside>
  );
}
