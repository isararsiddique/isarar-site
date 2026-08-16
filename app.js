// Progressive enhancement only — the page is fully readable without this file.
(function () {
  "use strict";

  var reduced = window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- scroll reveal ----
  var targets = document.querySelectorAll(".reveal");

  if (reduced || !("IntersectionObserver" in window)) {
    // show everything immediately, no motion
    for (var i = 0; i < targets.length; i++) targets[i].classList.add("in");
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    for (var j = 0; j < targets.length; j++) io.observe(targets[j]);
  }

  // ---- nav hairline on scroll ----
  var nav = document.querySelector(".nav");
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle("scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // ---- avatar fallback to initials ----
  var av = document.querySelector(".avatar img");
  if (av) {
    av.addEventListener("error", function () { av.hidden = true; });
    if (av.complete && av.naturalWidth === 0) av.hidden = true;
  }
})();
