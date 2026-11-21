/* "Run accessibility checks on this page" button in the Page tools panel.
   Loads the site's own copy of axe-core (assets/js/axe.min.js, version 4.14.1,
   Mozilla Public License 2.0) only when the button is pressed, runs the WCAG 2.0
   and 2.1 level A and AA rules on this page (the Page tools panel is left out),
   and lists the results in the panel. Nothing is sent anywhere. */
(function () {
  var button = document.getElementById("page-check-run");
  var status = document.getElementById("page-check-status");
  var results = document.getElementById("page-check-results");
  if (!button || !status || !results) return;
  button.hidden = false;
  var AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];
  var highlighted = null;

  function loadAxe(src) {
    return new Promise(function (resolve, reject) {
      if (window.axe) return resolve(window.axe);
      var s = document.createElement("script");
      s.src = src;
      s.onload = function () { window.axe ? resolve(window.axe) : reject(new Error("axe-core did not load")); };
      s.onerror = function () { reject(new Error("axe-core could not be loaded")); };
      document.head.appendChild(s);
    });
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }
  function clearHighlight() {
    if (highlighted) {
      highlighted.el.classList.remove("page-check-highlight");
      highlighted.btn.setAttribute("aria-pressed", "false");
      highlighted.btn.textContent = "Highlight";
      highlighted = null;
    }
  }
  function highlight(btn, selector) {
    var same = highlighted && highlighted.btn === btn;
    clearHighlight();
    if (same) return;
    var target = null;
    try { target = document.querySelector(selector); } catch (e) {}
    if (!target) { btn.textContent = "Not found"; return; }
    target.classList.add("page-check-highlight");
    target.scrollIntoView({ block: "center" });
    btn.setAttribute("aria-pressed", "true");
    btn.textContent = "Remove highlight";
    highlighted = { el: target, btn: btn };
  }

  function render(r) {
    var elements = 0;
    r.violations.forEach(function (v) { elements += v.nodes.length; });
    results.textContent = "";
    var counts = el("ul", "page-check-counts");
    counts.appendChild(el("li", null, "Violations: " + plural(r.violations.length, "rule", "rules") + ", " + plural(elements, "element", "elements")));
    counts.appendChild(el("li", null, "Needs review: " + plural(r.incomplete.length, "rule", "rules")));
    counts.appendChild(el("li", null, "Passed: " + plural(r.passes.length, "rule", "rules")));
    results.appendChild(counts);
    if (r.violations.length) {
      var list = el("ol", "page-check-list");
      r.violations.forEach(function (v) {
        var li = el("li");
        var head = el("p", "page-check-rule");
        head.appendChild(el("strong", null, (v.impact || "unknown") + ": "));
        head.appendChild(document.createTextNode(v.help));
        li.appendChild(head);
        li.appendChild(el("p", null, plural(v.nodes.length, "element", "elements")));
        var sel = v.nodes[0] && v.nodes[0].target ? String(v.nodes[0].target[v.nodes[0].target.length - 1]) : "";
        if (sel) {
          var p = el("p", null, "First: ");
          p.appendChild(el("code", null, sel));
          li.appendChild(p);
        }
        var actions = el("p", "page-check-actions");
        var a = el("a", null, "How to fix (Deque)");
        a.href = v.helpUrl;
        a.target = "_blank";
        a.rel = "noopener";
        actions.appendChild(a);
        if (sel && v.nodes[0].target.length === 1) {
          var hb = el("button", "page-check-highlight-btn", "Highlight");
          hb.type = "button";
          hb.setAttribute("aria-pressed", "false");
          hb.setAttribute("aria-label", "Highlight the first element for: " + v.help);
          hb.addEventListener("click", function () { highlight(hb, sel); });
          actions.appendChild(hb);
        }
        li.appendChild(actions);
        list.appendChild(li);
      });
      results.appendChild(list);
    }
    results.hidden = false;
    status.textContent = "Checks finished: " + plural(r.violations.length, "rule", "rules") +
      " with violations on " + plural(elements, "element", "elements") +
      ", " + r.incomplete.length + " to review, " + r.passes.length + " passed.";
  }

  button.addEventListener("click", function () {
    clearHighlight();
    button.disabled = true;
    status.textContent = "Running checks...";
    loadAxe(button.getAttribute("data-axe-src"))
      .then(function (axe) {
        return axe.run({ exclude: [[".page-tools"]] }, { runOnly: { type: "tag", values: AXE_TAGS } });
      })
      .then(render)
      .catch(function (e) { status.textContent = "The checks could not run: " + e.message + "."; })
      .then(function () { button.disabled = false; });
  });
})();
