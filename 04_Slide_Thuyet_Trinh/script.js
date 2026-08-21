(function () {
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var total = slides.length;
  var current = 0;
  var counterEls = document.querySelectorAll(".counter");

  // Review mode: navigate all slides (main + former appendix) as one
  // continuous 1..N deck. The .appendix class stays for visual labeling
  // only -- it no longer affects numbering.
  function render() {
    slides.forEach(function (s, i) {
      s.classList.toggle("active", i === current);
    });
    var text = (current + 1) + " / " + total;
    counterEls.forEach(function (el) { el.textContent = text; });
    history.replaceState(null, "", "#" + (current + 1));
  }

  function goTo(i) {
    if (i < 0) i = 0;
    if (i >= total) i = total - 1;
    current = i;
    render();
  }

  function next() { goTo(current + 1); }
  function prev() { goTo(current - 1); }

  document.addEventListener("keydown", function (e) {
    switch (e.key) {
      case "ArrowRight":
      case " ":
      case "PageDown":
        e.preventDefault();
        next();
        break;
      case "ArrowLeft":
      case "PageUp":
        e.preventDefault();
        prev();
        break;
      case "Home":
        e.preventDefault();
        goTo(0);
        break;
      case "End":
        e.preventDefault();
        goTo(total - 1);
        break;
    }
  });

  var prevBtn = document.getElementById("prevBtn");
  var nextBtn = document.getElementById("nextBtn");
  if (prevBtn) prevBtn.addEventListener("click", prev);
  if (nextBtn) nextBtn.addEventListener("click", next);

  var hash = parseInt((location.hash || "").replace("#", ""), 10);
  if (!isNaN(hash) && hash >= 1 && hash <= total) current = hash - 1;

  render();
})();
