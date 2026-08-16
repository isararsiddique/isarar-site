/* isarar.com — progressive enhancement. Page works fine without this. */
(function () {
  "use strict";

  var calm = window.matchMedia &&
             window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- split headline into animated letters ---------- */
  function split(el) {
    var words = el.textContent.split(" ");
    el.textContent = "";
    words.forEach(function (w, wi) {
      var holder = document.createElement("span");
      holder.className = "rl";
      var inner = document.createElement("span");
      inner.textContent = w;
      inner.style.transition = "transform .95s cubic-bezier(.19,1,.22,1)";
      inner.style.transitionDelay = (wi * 0.055) + "s";
      holder.appendChild(inner);
      el.appendChild(holder);
      if (wi < words.length - 1) el.appendChild(document.createTextNode(" "));
    });
    requestAnimationFrame(function () {
      el.querySelectorAll(".rl > span").forEach(function (s) {
        s.style.transform = "translateY(0)";
      });
    });
  }

  var head = document.querySelector("[data-split]");
  if (head && !calm) split(head);

  /* ---------- scroll reveal ---------- */
  var ups = document.querySelectorAll(".up");
  if (calm || !("IntersectionObserver" in window)) {
    ups.forEach(function (n) { n.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (rows) {
      rows.forEach(function (r) {
        if (r.isIntersecting) { r.target.classList.add("in"); io.unobserve(r.target); }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.1 });
    ups.forEach(function (n) { io.observe(n); });
  }

  /* ---------- scroll progress ---------- */
  var bar = document.getElementById("bar");
  if (bar) {
    var tick = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
    };
    tick();
    window.addEventListener("scroll", tick, { passive: true });
  }

  /* ---------- cursor ---------- */
  var dot = document.getElementById("dot");
  if (dot && !calm && window.matchMedia("(hover:hover)").matches) {
    var tx = 0, ty = 0, cx = 0, cy = 0;
    window.addEventListener("mousemove", function (e) { tx = e.clientX; ty = e.clientY; });
    (function glide() {
      cx += (tx - cx) * 0.18;
      cy += (ty - cy) * 0.18;
      dot.style.transform = "translate(" + cx + "px," + cy + "px) translate(-50%,-50%)";
      requestAnimationFrame(glide);
    })();
    document.querySelectorAll("a,button").forEach(function (el) {
      el.addEventListener("mouseenter", function () { dot.classList.add("big"); });
      el.addEventListener("mouseleave", function () { dot.classList.remove("big"); });
    });
  }

  /* ---------- count up ---------- */
  var ks = document.querySelectorAll("[data-to]");
  if (ks.length) {
    if (calm || !("IntersectionObserver" in window)) {
      ks.forEach(function (k) { k.textContent = k.dataset.to; });
    } else {
      var io2 = new IntersectionObserver(function (rows) {
        rows.forEach(function (r) {
          if (!r.isIntersecting) return;
          io2.unobserve(r.target);
          var end = parseInt(r.target.dataset.to, 10),
              suf = r.target.dataset.suffix || "",
              t0 = null;
          var run = function (ts) {
            if (!t0) t0 = ts;
            var p = Math.min((ts - t0) / 1100, 1);
            var eased = 1 - Math.pow(1 - p, 3);
            r.target.textContent = Math.round(end * eased) + suf;
            if (p < 1) requestAnimationFrame(run);
          };
          requestAnimationFrame(run);
        });
      }, { threshold: 0.5 });
      ks.forEach(function (k) { io2.observe(k); });
    }
  }

  /* ---------- avatar fallback ---------- */
  var f = document.querySelector(".face img");
  if (f) {
    f.addEventListener("error", function () { f.hidden = true; });
    if (f.complete && f.naturalWidth === 0) f.hidden = true;
  }
})();
