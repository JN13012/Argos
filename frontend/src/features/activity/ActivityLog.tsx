import { useState } from "react";
import { Button } from "../../components/Button";
import { Icon } from "../../components/Icon";
import { matchesSearch } from "../workspace/search";
import {
  activityLabels,
  COLLAPSED_ACTIVITY_EVENTS,
  formatTime,
} from "./activity";
import type { ActivityEvent, ActivityFilter } from "./activity";
import "./ActivityLog.css";

export function ActivityLog({
  events,
  query,
}: {
  events: readonly ActivityEvent[];
  query: string;
}) {
  const [filter, setFilter] = useState<ActivityFilter>("all");
  const [expanded, setExpanded] = useState(false);
  const filtered = events.filter(
    (event) =>
      (filter === "all" || event.type === filter) &&
      matchesSearch(
        query,
        activityLabels[event.type],
        event.text,
        event.reference,
      ),
  );
  const visible = (
    expanded ? [...filtered] : filtered.slice(-COLLAPSED_ACTIVITY_EVENTS)
  ).reverse();

  return (
    <section
      className={`panel activity-panel ${expanded ? "expanded" : ""}`}
      aria-labelledby="activity-title"
    >
      <div className="panel-heading">
        <div className="panel-heading-label">
          <Icon name="terminal" />
          <h2 id="activity-title">Journal de logs</h2>
        </div>
        <label className="activity-filter">
          <Icon name="filter" />
          <span className="sr-only">Filtrer le journal de logs</span>
          <select
            id="activity-filter"
            value={filter}
            onChange={(event) =>
              setFilter(event.target.value as ActivityFilter)
            }
          >
            <option value="all">Tous les événements</option>
            <option value="mission">Mission</option>
            <option value="review">Consultation de constats</option>
            <option value="report">Rapport</option>
          </select>
        </label>
      </div>
      <div className="activity-log" id="activity-log">
        {visible.map((event) => (
          <div className="activity-row" key={event.id}>
            <time
              className="activity-time"
              dateTime={event.timestamp.toISOString()}
              title={event.timestamp.toLocaleDateString("fr-FR", {
                timeZone: "Europe/Paris",
              })}
            >
              {formatTime.format(event.timestamp)}
            </time>
            <span className={`activity-tag ${event.type}`}>
              [{activityLabels[event.type]}]
            </span>
            <span className="activity-text">{event.text}</span>
            <span className="activity-reference">{event.reference}</span>
          </div>
        ))}
        {!visible.length && (
          <p className="empty-message">
            Aucun événement ne correspond à ce filtre.
          </p>
        )}
      </div>
      <div className="activity-footer">
        <span>
          <span className="status-dot" />
          Session locale · Europe/Paris
        </span>
        <div className="activity-controls">
          <span id="activity-count">
            {visible.length === filtered.length
              ? `${visible.length} événement${visible.length === 1 ? "" : "s"}`
              : `${visible.length} sur ${filtered.length} événements`}
          </span>
          {(expanded || filtered.length > COLLAPSED_ACTIVITY_EVENTS) && (
            <Button
              variant="quiet"
              id="activity-toggle"
              aria-expanded={expanded}
              aria-controls="activity-log"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? "Réduire le journal" : "Développer le journal"}
              <Icon name="chevron" />
            </Button>
          )}
        </div>
      </div>
    </section>
  );
}
