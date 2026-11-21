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
        var a = el("a", null, "How to fix (Deque)");
        a.href = v.helpUrl; a.target = "_blank"; a.rel = "noopener";
        var pa = el("p"); pa.appendChild(a); li.appendChild(pa);
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
