"use strict";

(() => {
  const assessment = globalThis.ARGOS_DEMO;
  const $ = (selector) => document.querySelector(selector);
  const svgNamespace = "http://www.w3.org/2000/svg";
  const normalize = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  const localTime = new Intl.DateTimeFormat("fr-FR", {
    timeZone: "Europe/Paris", hour: "2-digit", minute: "2-digit", second: "2-digit",
  });

  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  }

  function icon(name) {
    const svg = document.createElementNS(svgNamespace, "svg");
    svg.classList.add("icon");
    svg.setAttribute("aria-hidden", "true");
    const use = document.createElementNS(svgNamespace, "use");
    use.setAttribute("href", `#i-${name}`);
    svg.append(use);
    return svg;
  }

  const findingLabels = {
    "F-001": {
      title: "Configuration de diagnostic",
      description: "La configuration synthétique déclare un mode diagnostic. Son contexte et ses paramètres doivent être examinés ; ce constat n’est pas une vulnérabilité confirmée.",
      recommendation: "Vérifier le contexte et documenter la configuration retenue.",
    },
    "F-002": {
      title: "Bannière de formation",
      description: "La bannière fictive pourrait préciser davantage l’usage de formation de l’application.",
      recommendation: "Rendre explicite l’usage réservé à la formation.",
    },
  };
  const pendingCount = assessment.findings.filter((finding) => finding.review === null).length;
  const evidenceCount = assessment.evidence.length;
  const scopeCount = assessment.mission.scope.length;

  function renderFindings() {
    const container = $("#mission-findings");
    for (const finding of assessment.findings) {
      const copy = findingLabels[finding.id];
      const card = element("article", "finding-card");
      const heading = element("div", "finding-heading");
      heading.append(
        element("span", "finding-id", finding.id),
        element("h3", "", copy.title),
        element("span", "badge neutral-badge", finding.severity === "low" ? "Faible" : "Info"),
        element("span", "badge amber-badge", "À revoir"),
      );
      card.append(heading, element("p", "", copy.description));
      card.append(element("p", "", `Recommandation : ${copy.recommendation}`));
      const proof = assessment.evidence.find((entry) => finding.evidence_ids.includes(entry.id));
      const evidence = element("div", "finding-evidence");
      evidence.append(
        icon("file"),
        element("span", "", `${proof.id} · ${proof.path.split("/").pop()}`),
        element("code", "", `SHA-256 déclaré : ${proof.sha256.slice(0, 8)}…${proof.sha256.slice(-8)}`),
      );
      card.append(evidence);
      container.append(card);
    }
  }

  const activities = [
    { step: "01", type: "mission", tag: "MISSION", text: "Document de démonstration chargé.", reference: assessment.mission.id },
    { step: "02", type: "mission", tag: "PÉRIMÈTRE", text: `${scopeCount} actif déclaré dans le périmètre de la mission.`, reference: assessment.mission.scope.join(", ") },
    { step: "03", type: "evidence", tag: "PREUVES", text: `${evidenceCount} fichiers de preuve référencés avec leur empreinte SHA-256.`, reference: assessment.evidence.map((proof) => proof.id).join(" · ") },
    { step: "04", type: "review", tag: "REVUE", text: `${pendingCount} constats synthétiques en attente de revue humaine.`, reference: assessment.findings.map((finding) => finding.id).join(" · ") },
    { step: "05", type: "report", tag: "RAPPORT", text: "Rapport Markdown de référence disponible au téléchargement.", reference: "Rapport de démonstration" },
  ];

  function renderActivities() {
    const filter = $("#activity-filter").value;
    const query = normalize($("#global-search").value);
    const events = activities.filter((event) => (
      (filter === "all" || event.type === filter)
      && normalize(`${event.tag} ${event.text} ${event.reference}`).includes(query)
    ));
    const log = $("#activity-log");
    log.replaceChildren();
    for (const event of events) {
      const row = element("div", "activity-row");
      row.append(
        element("span", "activity-step", event.step),
        element("span", `activity-tag ${event.type}`, `[${event.tag}]`),
        element("span", "activity-text", event.text),
        element("span", "activity-reference", event.reference),
      );
      log.append(row);
    }
    if (events.length === 0) log.append(element("p", "activity-empty", "Aucun événement ne correspond à ce filtre."));
    $("#activity-count").textContent = `${events.length} événement${events.length === 1 ? "" : "s"}`;
  }

  function filterDashboard() {
    const query = normalize($("#global-search").value);
    let matches = 0;
    for (const row of document.querySelectorAll(".searchable")) {
      row.hidden = !normalize(`${row.dataset.search} ${row.textContent}`).includes(query);
      if (!row.hidden) matches += 1;
    }
    const feedback = $("#search-feedback");
    feedback.hidden = query.length === 0;
    feedback.textContent = matches === 0
      ? "Aucun document ou mission ne correspond à cette recherche."
      : `${matches} résultat${matches === 1 ? "" : "s"} dans les documents et les missions.`;
    renderActivities();
  }

  const missionDialog = $("#mission-dialog");
  const aboutDialog = $("#about-dialog");
  document.querySelectorAll("[data-open-mission]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#notifications").hidden = true;
      $("#notifications-toggle").setAttribute("aria-expanded", "false");
      missionDialog.showModal();
    });
  });
  $("#about-demo").addEventListener("click", () => aboutDialog.showModal());
  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => button.closest("dialog").close());
  });
  [missionDialog, aboutDialog].forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      const bounds = dialog.getBoundingClientRect();
      if (event.target === dialog && (
        event.clientX < bounds.left || event.clientX > bounds.right
        || event.clientY < bounds.top || event.clientY > bounds.bottom
      )) dialog.close();
    });
  });

  function toggleNotifications() {
    const popover = $("#notifications");
    popover.hidden = !popover.hidden;
    $("#notifications-toggle").setAttribute("aria-expanded", String(!popover.hidden));
  }
  $("#notifications-toggle").addEventListener("click", toggleNotifications);
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".notification-wrapper")) {
      $("#notifications").hidden = true;
      $("#notifications-toggle").setAttribute("aria-expanded", "false");
    }
  });

  const chatInput = $("#chat-input");
  const chatSend = $("#chat-send");
  const chatMessages = $("#chat-messages");
  const chatPanel = $("#chat-panel");

  function focusChat() {
    chatPanel.scrollIntoView({ behavior: "auto", block: "nearest" });
    chatInput.focus({ preventScroll: true });
  }

  function addMessage(author, value) {
    // All text, including user input, is rendered as text nodes.
    const message = element("div", `message ${author === "Vous" ? "user" : "assistant"}-message`);
    if (author !== "Vous") {
      const avatar = element("span", "message-avatar");
      avatar.append(icon("eye-shield"));
      message.append(avatar);
    }
    const bubble = element("div", "message-bubble");
    bubble.append(
      element("span", "message-author", author.toUpperCase()),
      element("p", "", value),
      element("span", "message-time", "Démo locale"),
    );
    message.append(bubble);
    chatMessages.append(message);
    // Limit the conversation to a bounded, in-memory demonstration.
    while (chatMessages.childElementCount > 42) chatMessages.firstElementChild.remove();
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function demoReply(question) {
    const normalized = normalize(question);
    if (/preuve|evidence|fichier|hash|sha/.test(normalized)) {
      return `${evidenceCount} preuves sont référencées :\n\n${assessment.evidence.map((proof) => `${proof.id} — ${proof.path.split("/").pop()}`).join("\n")}\n\nLeurs empreintes SHA-256 sont déclarées dans le dossier. La vérification des fichiers se fait dans Argos Core ; ce dashboard ne lit pas vos preuves locales.`;
    }
    if (/constat|revue|vulnerab|critique|diagnostic/.test(normalized)) {
      return `${pendingCount} constats attendent une revue :\n\nF-001 — Configuration de diagnostic (faible).\nF-002 — Bannière de formation (info).\n\nCe sont des observations synthétiques. Aucun constat critique ne figure dans cette démonstration.`;
    }
    if (/agent|statut|connexion/.test(normalized)) {
      return "Aucun agent n’est connecté. Les profils affichés illustrent une organisation future. Aucune analyse ni tâche n’est lancée depuis cet accueil.";
    }
    if (/rapport|export|telecharg/.test(normalized)) {
      return "Le rapport Markdown de référence est disponible dans « Rapports & documents ». Il présente la mission synthétique, ses deux constats et les métadonnées de ses deux preuves.";
    }
    if (/mission|resum|perimetre|actif|bonjour|aide/.test(normalized)) {
      return `Votre mission : demo-offline.\n\nPérimètre : ${assessment.mission.scope.join(", ")}.\n${assessment.findings.length} constats et ${evidenceCount} preuves associées.\n${pendingCount} décisions de revue à enregistrer.\n\nUtilisez « Voir la mission » pour consulter son aperçu.`;
    }
    return "Je suis le chat de démonstration de cet accueil, avec des réponses prédéfinies. Je peux présenter la mission, les constats, les preuves, le rapport et le statut des agents. Essayez l’un des raccourcis ci-dessous.";
  }

  function askDemo(question) {
    const value = question.trim().slice(0, 500);
    if (!value) return;
    addMessage("Vous", value);
    addMessage("Argos", demoReply(value));
    chatInput.value = "";
    chatSend.disabled = true;
    focusChat();
  }

  $("#chat-form").addEventListener("submit", (event) => {
    event.preventDefault();
    askDemo(chatInput.value);
  });
  chatInput.addEventListener("input", () => { chatSend.disabled = chatInput.value.trim().length === 0; });
  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      askDemo(chatInput.value);
    }
  });
  document.querySelectorAll("[data-chat-question]").forEach((button) => {
    button.addEventListener("click", () => askDemo(button.dataset.chatQuestion));
  });
  $("#chat-focus").addEventListener("click", focusChat);
  let focusBeforeExpansion = null;
  const backgroundSections = ".skip-link, .topbar, .sidebar, .page-heading, .overview-column, .activity-panel, .workspace-footer";
  function setChatExpanded(expanded) {
    chatPanel.classList.toggle("expanded", expanded);
    const button = $("#chat-expand");
    button.setAttribute("aria-expanded", String(expanded));
    button.setAttribute("aria-label", expanded ? "Réduire le panneau de chat" : "Agrandir le panneau de chat");
    if (expanded) {
      focusBeforeExpansion = document.activeElement;
      chatPanel.setAttribute("role", "dialog");
      chatPanel.setAttribute("aria-modal", "true");
      document.querySelectorAll(backgroundSections).forEach((node) => { node.inert = true; });
      chatInput.focus({ preventScroll: true });
    } else {
      chatPanel.removeAttribute("role");
      chatPanel.removeAttribute("aria-modal");
      document.querySelectorAll(backgroundSections).forEach((node) => { node.inert = false; });
      focusBeforeExpansion?.focus({ preventScroll: true });
    }
  }
  $("#chat-expand").addEventListener("click", () => setChatExpanded(!chatPanel.classList.contains("expanded")));

  function setSidebarOpen(open) {
    $("#sidebar").classList.toggle("open", open);
    $("#sidebar-backdrop").hidden = !open;
    $("#menu-toggle").setAttribute("aria-expanded", String(open));
    $("#menu-toggle").setAttribute("aria-label", open ? "Fermer la navigation" : "Ouvrir la navigation");
    if (!open && $("#sidebar").contains(document.activeElement)) $("#menu-toggle").focus();
  }
  $("#menu-toggle").addEventListener("click", () => setSidebarOpen(!$("#sidebar").classList.contains("open")));
  $("#sidebar-backdrop").addEventListener("click", () => setSidebarOpen(false));
  $(".navigation .active").addEventListener("click", () => setSidebarOpen(false));
  window.matchMedia("(max-width: 650px)").addEventListener("change", (event) => {
    if (!event.matches) setSidebarOpen(false);
  });

  $("#global-search").addEventListener("input", filterDashboard);
  $("#activity-filter").addEventListener("change", renderActivities);
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k" && window.innerWidth > 650 && !document.querySelector("dialog[open]") && !chatPanel.classList.contains("expanded")) {
      event.preventDefault();
      $("#global-search").focus();
    }
    if (event.key === "Escape") {
      $("#notifications").hidden = true;
      $("#notifications-toggle").setAttribute("aria-expanded", "false");
      if (chatPanel.classList.contains("expanded")) setChatExpanded(false);
      setSidebarOpen(false);
    }
  });

  function updateClock() { $("#local-clock").textContent = localTime.format(new Date()); }
  updateClock();
  window.setInterval(updateClock, 1000);
  renderFindings();
  renderActivities();
})();
