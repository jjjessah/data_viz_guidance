/* Accessibility check bookmark tool (bookmarklet) from the Data Visualization Guidance site.
   The bookmark loads this file on any page. This file then loads axe-core 4.14.1
   (Deque Systems, Mozilla Public License 2.0) from a pinned jsDelivr address with a
   Subresource Integrity hash, runs the WCAG 2.0 and 2.1 level A and AA rules, and shows
   the results in a small panel on the page. Nothing is sent anywhere.
   To update axe-core: change AXE_SRC and AXE_SRI together (the hash is in axe-core's sri-history.json
   or from: openssl dgst -sha384 -binary axe.min.js | openssl base64 -A). */
(function () {
  var AXE_SRC = "https://cdn.jsdelivr.net/npm/axe-core@4.14.1/axe.min.js";
  var AXE_SRI = "sha384-xt1SFg49QaDwsyt0Xfs2XAyBtYPClXl3X2q5OOLeGAUmq9jZTYIMdztpF99WdhiH";
  var AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];
  var HOST_ID = "dvg-a11y-check";
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

  var old = document.getElementById(HOST_ID);
  if (old) old.remove();
  var opener = document.activeElement;

  var host = document.createElement("div");
  host.id = HOST_ID;
  var root = host.attachShadow ? host.attachShadow({ mode: "open" }) : host;
  root.innerHTML =
    "<style>" +
    ":host{all:initial}" +
    ".box{position:fixed;top:8px;right:8px;z-index:2147483647;box-sizing:border-box;width:min(26rem,calc(100vw - 16px));" +
    "max-height:calc(100vh - 16px);overflow:auto;background:#fff;color:#1b1b1b;border:2px solid #0c5a3c;border-radius:8px;" +
    "box-shadow:0 4px 16px rgba(0,0,0,.3);padding:12px 14px;font:15px/1.4 Arial,Helvetica,sans-serif;text-align:left}" +
    "h2{margin:0 2.5rem .5rem 0;font-size:17px;color:#0c5a3c}" +
    ".close{position:absolute;top:8px;right:8px;min-width:36px;min-height:36px;font:700 20px/1 Arial,sans-serif;color:#fff;" +
    "background:#0c5a3c;border:0;border-radius:4px;cursor:pointer}" +
    "a{color:#155799;text-decoration:underline}" +
    "button:focus-visible,a:focus-visible,h2:focus-visible{outline:3px solid #155799;outline-offset:2px}" +
    "ul,ol{margin:.25rem 0 .5rem;padding-left:1.25rem}li{margin-bottom:.5rem}p{margin:.2rem 0}" +
    "code{font:13px/1.3 monospace;overflow-wrap:anywhere;background:#f4f7f6;padding:0 2px}" +
    ".note{font-size:13px}.status{font-weight:700}" +
    "</style>" +
    '<div class="box" role="dialog" aria-modal="false" aria-labelledby="t">' +
    '<button type="button" class="close" aria-label="Close accessibility results">\u00d7</button>' +
    '<h2 id="t" tabindex="-1">Accessibility check results</h2>' +
    '<p class="note">Automated checks find some problems only. They are not a full Section 508 review.</p>' +
    '<div class="status" role="status" aria-live="polite">Running checks...</div>' +
    '<div class="out"></div>' +
    '<p class="note">Press Esc or the \u00d7 button to close.</p></div>';
  document.body.appendChild(host);

  var box = root.querySelector(".box");
  var status = root.querySelector(".status");
  var out = root.querySelector(".out");
  function close() {
    document.removeEventListener("keydown", onKey, true);
    host.remove();
    if (opener && opener.focus) { try { opener.focus(); } catch (e) {} }
  }
  function onKey(e) { if (e.key === "Escape") { e.preventDefault(); close(); } }
  document.addEventListener("keydown", onKey, true);
  root.querySelector(".close").addEventListener("click", close);
  root.querySelector("h2").focus();

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }

  function run() {
    return window.axe.run({ exclude: [["#" + HOST_ID]] }, { runOnly: { type: "tag", values: AXE_TAGS } });
  }
  function render(r) {
    var elements = 0;
    r.violations.forEach(function (v) { elements += v.nodes.length; });
    var counts = el("ul");
    counts.appendChild(el("li", null, "Violations: " + plural(r.violations.length, "rule", "rules") + ", " + plural(elements, "element", "elements")));
    counts.appendChild(el("li", null, "Needs review: " + plural(r.incomplete.length, "rule", "rules")));
    counts.appendChild(el("li", null, "Passed: " + plural(r.passes.length, "rule", "rules")));
    out.appendChild(counts);
    if (r.violations.length) {
      var list = el("ol");
      r.violations.forEach(function (v) {
        var li = el("li");
        var head = el("p");
        head.appendChild(el("strong", null, (v.impact || "unknown") + ": "));
        head.appendChild(document.createTextNode(v.help + " (" + plural(v.nodes.length, "element", "elements") + ")"));
        li.appendChild(head);
        var t = v.nodes[0] && v.nodes[0].target;
        if (t) { var p = el("p", null, "First: "); p.appendChild(el("code", null, String(t[t.length - 1]))); li.appendChild(p); }
        li.appendChild(el("p", null, "W3C guidance (opens in a new tab):"));
        var refs = el("ul");
        wcagLinks(v.tags).forEach(function (w) {
          var a = el("a", null, w.text);
          a.href = w.href; a.target = "_blank"; a.rel = "noopener";
          var rli = el("li"); rli.appendChild(a); refs.appendChild(rli);
        });
        li.appendChild(refs);
        list.appendChild(li);
      });
      out.appendChild(list);
    }
    status.textContent = "Checks finished: " + plural(r.violations.length, "rule", "rules") +
      " with violations on " + plural(elements, "element", "elements") + ".";
  }
  function fail(msg) {
    status.textContent = "The checks could not run. " + msg;
    out.appendChild(el("p", null, "This page may block outside scripts (a Content Security Policy). " +
      "Use Lighthouse in Chrome's developer tools, the axe DevTools browser extension, or WAVE instead."));
  }

  if (window.axe && window.axe.run) {
    run().then(render, function (e) { fail(e.message); });
    return;
  }
  var s = document.createElement("script");
  s.src = AXE_SRC;
  s.integrity = AXE_SRI;
  s.crossOrigin = "anonymous";
  s.onload = function () { run().then(render, function (e) { fail(e.message); }); };
  s.onerror = function () { fail("axe-core could not be loaded."); };
  (document.head || document.documentElement).appendChild(s);
})();
