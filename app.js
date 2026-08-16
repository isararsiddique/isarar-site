/* isarar.com — progressive enhancement. Everything works without this file. */
(function () {
  "use strict";

  /* ---------- theme (runs first to avoid a flash) ---------- */
  var root = document.documentElement;
  try {
    var saved = localStorage.getItem("theme");
    if (saved === "dark" || saved === "light") root.setAttribute("data-theme", saved);
  } catch (e) {}

  function wireTheme() {
    var btn = document.getElementById("theme");
    if (!btn) return;
    var sysDark = window.matchMedia("(prefers-color-scheme: dark)");
    var current = function () {
      var a = root.getAttribute("data-theme");
      return a || (sysDark.matches ? "dark" : "light");
    };
    var paint = function () {
      btn.setAttribute("aria-label",
        current() === "dark" ? "Switch to light mode" : "Switch to dark mode");
      btn.setAttribute("aria-pressed", current() === "dark" ? "true" : "false");
    };
    paint();
    btn.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      paint();
    });
  }

  var calm = window.matchMedia &&
             window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- split headline ---------- */
  function split(el) {
    var words = el.textContent.split(" ");
    el.textContent = "";
    words.forEach(function (w, i) {
      var hold = document.createElement("span");
      hold.className = "rl";
      var inner = document.createElement("span");
      inner.textContent = w;
      inner.style.transition = "transform .95s cubic-bezier(.19,1,.22,1)";
      inner.style.transitionDelay = (i * 0.05) + "s";
      hold.appendChild(inner);
      el.appendChild(hold);
      if (i < words.length - 1) el.appendChild(document.createTextNode(" "));
    });
    requestAnimationFrame(function () {
      el.querySelectorAll(".rl > span").forEach(function (s) {
        s.style.transform = "translateY(0)";
      });
    });
  }

  function boot() {
    wireTheme();

    var head = document.querySelector("[data-split]");
    if (head && !calm) split(head);

    /* reveal */
    var ups = document.querySelectorAll(".up, .fig");
    if (calm || !("IntersectionObserver" in window)) {
      ups.forEach(function (n) { n.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (rows) {
        rows.forEach(function (r) {
          if (r.isIntersecting) { r.target.classList.add("in"); io.unobserve(r.target); }
        });
      }, { rootMargin: "0px 0px -6% 0px", threshold: 0.08 });
      ups.forEach(function (n) { io.observe(n); });
    }

    /* progress + sticky hairline */
    var bar = document.getElementById("bar");
    var top = document.querySelector(".top");
    var onScroll = function () {
      if (bar) {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
      }
      if (top) top.classList.toggle("stuck", window.scrollY > 6);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    /* cursor */
    var dot = document.getElementById("dot");
    if (dot && !calm && window.matchMedia("(hover:hover)").matches) {
      var tx = 0, ty = 0, cx = 0, cy = 0;
      window.addEventListener("mousemove", function (e) { tx = e.clientX; ty = e.clientY; });
      (function glide() {
        cx += (tx - cx) * 0.18; cy += (ty - cy) * 0.18;
        dot.style.transform = "translate(" + cx + "px," + cy + "px) translate(-50%,-50%)";
        requestAnimationFrame(glide);
      })();
      document.querySelectorAll("a,button").forEach(function (el) {
        el.addEventListener("mouseenter", function () { dot.classList.add("big"); });
        el.addEventListener("mouseleave", function () { dot.classList.remove("big"); });
      });
    }

    /* count up */
    var ks = document.querySelectorAll("[data-to]");
    if (ks.length) {
      if (calm || !("IntersectionObserver" in window)) {
        ks.forEach(function (k) { k.textContent = k.dataset.to; });
      } else {
        var io2 = new IntersectionObserver(function (rows) {
          rows.forEach(function (r) {
            if (!r.isIntersecting) return;
            io2.unobserve(r.target);
            var end = parseInt(r.target.dataset.to, 10), t0 = null;
            var run = function (ts) {
              if (!t0) t0 = ts;
              var p = Math.min((ts - t0) / 1100, 1);
              r.target.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
              if (p < 1) requestAnimationFrame(run);
            };
            requestAnimationFrame(run);
          });
        }, { threshold: 0.5 });
        ks.forEach(function (k) { io2.observe(k); });
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else { boot(); }
})();
