(function () {
  var toggle = document.getElementById("nav-toggle");
  var sidebar = document.getElementById("site-sidebar");
  if (!toggle || !sidebar) return;

  toggle.addEventListener("click", function () {
    var open = sidebar.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
