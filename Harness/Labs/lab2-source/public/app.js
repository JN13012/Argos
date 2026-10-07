/*
 * The online banking client.
 *
 * Pages are rendered by the server; the actions on them post to the JSON API
 * so there is one implementation of every instruction rather than two. A form
 * marked data-api is serialised to JSON, sent, and its result shown in the
 * panel named by data-result.
 */

(function () {
  "use strict";

  function serialise(form) {
    const out = {};
    new FormData(form).forEach(function (value, key) {
      if (value === "") return;
      out[key] = value;
    });
    return out;
  }

  function show(panel, ok, body) {
    if (!panel) return;
    panel.hidden = false;
    panel.className = "result " + (ok ? "ok" : "bad");
    if (typeof body === "string") {
      panel.textContent = body;
      return;
    }
    const message = body.error
      || (body.ok ? "Done." : "")
      || "";
    const detail = Object.keys(body)
      .filter(function (k) { return k !== "ok" && k !== "error"; })
      .map(function (k) {
        const v = body[k];
        return k + ": " + (typeof v === "object" ? JSON.stringify(v) : v);
      });
    panel.textContent = [message].concat(detail).filter(Boolean).join("\n");
  }

  document.addEventListener("submit", function (event) {
    const form = event.target.closest("form[data-api]");
    if (!form) return;
    event.preventDefault();

    const panel = document.querySelector(form.dataset.result || "");
    const buttons = form.querySelectorAll("button");
    buttons.forEach(function (b) { b.disabled = true; });

    fetch(form.dataset.api, {
      method: form.dataset.method || "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(serialise(form)),
    })
      .then(function (res) {
        return res.json().then(function (body) { return { ok: res.ok, body: body }; });
      })
      .then(function (r) {
        show(panel, r.ok, r.body);
        if (r.ok && form.dataset.reloadOnSuccess !== undefined) {
          setTimeout(function () { window.location.reload(); }, 900);
        }
      })
      .catch(function () {
        show(panel, false, "That did not go through. Try again.");
      })
      .finally(function () {
        buttons.forEach(function (b) { b.disabled = false; });
      });
  });
})();
