(function () {
  "use strict";

  var params = new URLSearchParams(window.location.search);
  var from = (params.get("from") || "").toLowerCase();
  var allowed = { cement: 1, steel: 1, pharma: 1 };
  var back = document.getElementById("backToDeck");
  if (back) {
    if (allowed[from]) {
      back.href = "../" + from + ".html#scene-tech";
      back.textContent = "← Back to " + from + " deck";
    } else {
      back.href = "../index.html";
      back.textContent = "← Back to decks";
    }
  }

  document.querySelectorAll("[data-pill-from]").forEach(function (a) {
    if (allowed[from]) {
      var href = a.getAttribute("href") || "";
      var join = href.indexOf("?") >= 0 ? "&" : "?";
      a.setAttribute("href", href + join + "from=" + encodeURIComponent(from));
    }
  });

  document.querySelectorAll("[data-flip]").forEach(function (card) {
    card.addEventListener("click", function () {
      var on = card.classList.toggle("is-flipped");
      card.setAttribute("aria-pressed", on ? "true" : "false");
    });
    card.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        card.click();
      }
    });
  });

  window.StampedDeepDive = {
    from: from,
    bindChips: function (rootSel, detailSel, data) {
      var root = document.querySelector(rootSel);
      var detail = document.querySelector(detailSel);
      if (!root || !detail) return;
      var chips = root.querySelectorAll("[data-chip]");
      function show(key) {
        var item = data[key];
        if (!item) return;
        chips.forEach(function (c) {
          c.classList.toggle("is-active", c.getAttribute("data-chip") === key);
        });
        detail.innerHTML =
          "<h3>" +
          item.title +
          "</h3><p>" +
          item.body +
          '</p><span class="rule-cite">' +
          item.cite +
          "</span>";
      }
      chips.forEach(function (chip) {
        chip.addEventListener("click", function () {
          show(chip.getAttribute("data-chip"));
        });
      });
      var first = chips[0] && chips[0].getAttribute("data-chip");
      if (first) show(first);
    },
    bindPipeline: function (rootSel, detailSel, data) {
      var root = document.querySelector(rootSel);
      var detail = document.querySelector(detailSel);
      if (!root || !detail) return;
      var nodes = root.querySelectorAll("[data-node]");
      function show(key) {
        var item = data[key];
        if (!item) return;
        nodes.forEach(function (n) {
          n.classList.toggle("is-active", n.getAttribute("data-node") === key);
        });
        detail.innerHTML =
          "<strong>" +
          item.title +
          "</strong><p style=\"margin-top:0.4rem\">" +
          item.body +
          "</p>" +
          (item.code ? "<p style=\"margin-top:0.55rem\"><code>" + item.code + "</code></p>" : "");
        detail.hidden = false;
      }
      nodes.forEach(function (node) {
        node.addEventListener("click", function () {
          show(node.getAttribute("data-node"));
        });
      });
      var first = nodes[0] && nodes[0].getAttribute("data-node");
      if (first) show(first);
    },
    bindCalculator: function (pickSel, outSel, actions) {
      var pick = document.querySelector(pickSel);
      var out = document.querySelector(outSel);
      if (!pick || !out) return;
      var buttons = pick.querySelectorAll("[data-action]");
      function render(key) {
        var a = actions[key];
        if (!a) return;
        buttons.forEach(function (b) {
          b.classList.toggle("is-active", b.getAttribute("data-action") === key);
        });
        out.innerHTML =
          '<dl class="ledger">' +
          '<div class="ledger-row"><dt>Baseline lock</dt><dd>' +
          a.baseline +
          "</dd></div>" +
          '<div class="ledger-row"><dt>Telemetry delta</dt><dd>' +
          a.delta +
          "</dd></div>" +
          '<div class="ledger-row"><dt>Tariff line</dt><dd>' +
          a.tariff +
          "</dd></div>" +
          '<div class="ledger-row"><dt>Potential (engine)</dt><dd class="money">' +
          a.potential +
          "</dd></div>" +
          '<div class="ledger-row"><dt>Realised</dt><dd class="' +
          (a.status === "VERIFIED" ? "status-ok" : "status-pending") +
          '">' +
          a.realised +
          " · " +
          a.status +
          "</dd></div>" +
          '<div class="ledger-row"><dt>Remaining opportunity</dt><dd class="money">' +
          a.remaining +
          "</dd></div>" +
          "</dl>" +
          '<div class="engine-pulse" aria-hidden="true"><div class="engine-pulse__bar"></div></div>' +
          '<p class="cite">calc://impact@' +
          a.engine +
          " · M&amp;V locked at issue · sample walkthrough</p>";
      }
      buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          render(btn.getAttribute("data-action"));
        });
      });
      var first = buttons[0] && buttons[0].getAttribute("data-action");
      if (first) render(first);
    },
  };
})();
