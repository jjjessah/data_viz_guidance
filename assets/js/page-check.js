/* "Run accessibility checks on this page" button in the Page tools panel.
   Loads the site's own copy of axe-core (assets/js/axe.min.js, version 4.14.1,
   Mozilla Public License 2.0) only when the button is pressed, runs the WCAG 2.0
   and 2.1 level A and AA rules on this page (the Page tools panel is left out),
   and lists the results in the panel, with links to the W3C pages for each
   WCAG success criterion. Nothing is sent anywhere. */
(function () {
  var button = document.getElementById("page-check-run");
  var status = document.getElementById("page-check-status");
  var results = document.getElementById("page-check-results");
  if (!button || !status || !results) return;
  button.hidden = false;
  var AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];
  var highlighted = null;
  /* WCAG 2.0 and 2.1 success criteria that axe-core can report: number -> [W3C Understanding page, name].
     Every address below was checked and opened on the W3C site. */
  var WCAG_BASE = "https://www.w3.org/WAI/WCAG21/Understanding/";
  var WCAG_QUICKREF = "https://www.w3.org/WAI/WCAG22/quickref/?versions=2.1";
  var WCAG_SC = {
    "1.1.1": ["non-text-content", "Non-text Content"],
    "1.2.1": ["audio-only-and-video-only-prerecorded", "Audio-only and Video-only (Prerecorded)"],
    "1.2.2": ["captions-prerecorded", "Captions (Prerecorded)"],
    "1.2.3": ["audio-description-or-media-alternative-prerecorded", "Audio Description or Media Alternative (Prerecorded)"],
    "1.2.4": ["captions-live", "Captions (Live)"],
    "1.2.5": ["audio-description-prerecorded", "Audio Description (Prerecorded)"],
    "1.3.1": ["info-and-relationships", "Info and Relationships"],
    "1.3.2": ["meaningful-sequence", "Meaningful Sequence"],
    "1.3.3": ["sensory-characteristics", "Sensory Characteristics"],
    "1.3.4": ["orientation", "Orientation"],
    "1.3.5": ["identify-input-purpose", "Identify Input Purpose"],
    "1.4.1": ["use-of-color", "Use of Color"],
    "1.4.2": ["audio-control", "Audio Control"],
    "1.4.3": ["contrast-minimum", "Contrast (Minimum)"],
    "1.4.4": ["resize-text", "Resize Text"],
    "1.4.5": ["images-of-text", "Images of Text"],
    "1.4.10": ["reflow", "Reflow"],
    "1.4.11": ["non-text-contrast", "Non-text Contrast"],
    "1.4.12": ["text-spacing", "Text Spacing"],
    "1.4.13": ["content-on-hover-or-focus", "Content on Hover or Focus"],
    "2.1.1": ["keyboard", "Keyboard"],
    "2.1.2": ["no-keyboard-trap", "No Keyboard Trap"],
    "2.1.3": ["keyboard-no-exception", "Keyboard (No Exception)"],
    "2.1.4": ["character-key-shortcuts", "Character Key Shortcuts"],
    "2.2.1": ["timing-adjustable", "Timing Adjustable"],
    "2.2.2": ["pause-stop-hide", "Pause, Stop, Hide"],
    "2.3.1": ["three-flashes-or-below-threshold", "Three Flashes or Below Threshold"],
    "2.4.1": ["bypass-blocks", "Bypass Blocks"],
    "2.4.2": ["page-titled", "Page Titled"],
    "2.4.3": ["focus-order", "Focus Order"],
    "2.4.4": ["link-purpose-in-context", "Link Purpose (In Context)"],
    "2.4.5": ["multiple-ways", "Multiple Ways"],
    "2.4.6": ["headings-and-labels", "Headings and Labels"],
    "2.4.7": ["focus-visible", "Focus Visible"],
    "2.5.1": ["pointer-gestures", "Pointer Gestures"],
    "2.5.2": ["pointer-cancellation", "Pointer Cancellation"],
    "2.5.3": ["label-in-name", "Label in Name"],
    "2.5.4": ["motion-actuation", "Motion Actuation"],
    "3.1.1": ["language-of-page", "Language of Page"],
    "3.1.2": ["language-of-parts", "Language of Parts"],
    "3.2.1": ["on-focus", "On Focus"],
    "3.2.2": ["on-input", "On Input"],
    "3.2.3": ["consistent-navigation", "Consistent Navigation"],
    "3.2.4": ["consistent-identification", "Consistent Identification"],
    "3.3.1": ["error-identification", "Error Identification"],
    "3.3.2": ["labels-or-instructions", "Labels or Instructions"],
    "3.3.3": ["error-suggestion", "Error Suggestion"],
    "3.3.4": ["error-prevention-legal-financial-data", "Error Prevention (Legal, Financial, Data)"],
    "4.1.1": ["parsing", "Parsing"],
    "4.1.2": ["name-role-value", "Name, Role, Value"],
    "4.1.3": ["status-messages", "Status Messages"]
  };
  /* axe-core tags such as "wcag143" or "wcag1410" -> links to the matching W3C pages. */
  function wcagLinks(tags) {
    var links = [];
    (tags || []).forEach(function (t) {
      var m = /^wcag(\d)(\d)(\d+)$/.exec(t);
      if (!m) return;
      var num = m[1] + "." + m[2] + "." + m[3];
      var sc = WCAG_SC[num];
      if (sc) links.push({ text: "WCAG " + num + ": " + sc[1], href: WCAG_BASE + sc[0] + ".html" });
    });
    if (!links.length) links.push({ text: "WCAG quick reference", href: WCAG_QUICKREF });
    return links;
  }

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
        li.appendChild(el("p", null, "W3C guidance (opens in a new tab):"));
        var refs = el("ul", "page-check-wcag");
        wcagLinks(v.tags).forEach(function (w) {
          var a = el("a", null, w.text);
          a.href = w.href;
          a.target = "_blank";
          a.rel = "noopener";
          var rli = el("li");
          rli.appendChild(a);
          refs.appendChild(rli);
        });
        li.appendChild(refs);
        var actions = el("p", "page-check-actions");
        if (sel && v.nodes[0].target.length === 1) {
          var hb = el("button", "page-check-highlight-btn", "Highlight");
          hb.type = "button";
          hb.setAttribute("aria-pressed", "false");
          hb.setAttribute("aria-label", "Highlight the first element for: " + v.help);
          hb.addEventListener("click", function () { highlight(hb, sel); });
          actions.appendChild(hb);
        }
        if (actions.childNodes.length) li.appendChild(actions);
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
