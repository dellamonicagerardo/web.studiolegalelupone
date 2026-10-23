(function () {
  var toggle = document.querySelector(".menu-toggle");
  var links = document.querySelector(".nav-links");

  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Chiudi il menu" : "Apri il menu");
    });

    links.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  document.querySelectorAll(".faq-item button").forEach(function (button) {
    button.addEventListener("click", function () {
      var item = button.parentElement;
      var willOpen = !item.classList.contains("open");
      document.querySelectorAll(".faq-item").forEach(function (other) {
        other.classList.remove("open");
        other.querySelector("button").setAttribute("aria-expanded", "false");
      });
      if (willOpen) {
        item.classList.add("open");
        button.setAttribute("aria-expanded", "true");
      }
    });
  });

  var motion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".faq-item .answer").forEach(function (answer) {
    var inner = document.createElement("div");
    inner.innerHTML = answer.innerHTML;
    answer.textContent = "";
    answer.appendChild(inner);
  });

  if (!motion) {
    var groups = [
      ".hero-inner > *",
      ".portrait, .about-copy > *, .stats > *",
      ".sheet-head > *, .area",
      ".section-head > *, .person",
      ".banner > div > *",
      ".office, .panel",
      ".note",
      ".feature-intro > *, .feature",
      ".faq-item",
      ".news a",
      ".close > *"
    ];
    var seen = new Set();
    groups.forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (el, index) {
        if (seen.has(el)) return;
        seen.add(el);
        el.classList.add("rise");
        var delay = el.closest(".hero") ? [0.05, 0.2, 0.4, 0.55][index] || 0.55 : Math.min(index, 6) * 0.12;
        el.style.animationDelay = delay + "s";
        el.addEventListener("animationend", function (event) {
          if (event.animationName !== "rise") return;
          el.classList.remove("rise", "in");
          el.style.animationDelay = "";
        });
      });
    });

    function show(el) { el.classList.add("in"); }

    var reveal = document.querySelectorAll(".rise");
    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          show(entry.target);
          observer.unobserve(entry.target);
        });
      }, { threshold: 0.16, rootMargin: "0px 0px -6% 0px" });
      reveal.forEach(function (el) {
        var box = el.getBoundingClientRect();
        if (box.top < window.innerHeight * 0.92 && box.bottom > 0) show(el);
        else observer.observe(el);
      });
    } else {
      reveal.forEach(show);
    }
  }

  document.documentElement.classList.remove("preload");

  function scrollLinear(track, delta) {
    var max = Math.max(0, track.scrollWidth - track.clientWidth);
    var target = Math.max(0, Math.min(max, track.scrollLeft + delta));
    if (track._raf) cancelAnimationFrame(track._raf);
    if (motion || target === track.scrollLeft) {
      track.scrollLeft = target;
      return;
    }
    var start = track.scrollLeft;
    var change = target - start;
    var t0 = performance.now();
    function frame(now) {
      var p = Math.min(1, (now - t0) / 420);
      track.scrollLeft = start + change * p;
      if (p < 1) track._raf = requestAnimationFrame(frame);
    }
    track._raf = requestAnimationFrame(frame);
  }

  document.querySelectorAll("[data-scroll]").forEach(function (button) {
    button.addEventListener("click", function () {
      var section = button.closest("section");
      var track = section ? section.querySelector(".track") : null;
      if (!track) return;
      var amount = track.clientWidth * 0.8;
      scrollLinear(track, button.getAttribute("data-scroll") === "next" ? amount : -amount);
    });
  });

  document.querySelectorAll(".track, .people").forEach(function (track) {
    var drag = null;

    function canScroll() {
      return track.scrollWidth > track.clientWidth + 2;
    }

    track.addEventListener("pointerdown", function (event) {
      if (event.pointerType !== "mouse" || event.button !== 0 || !canScroll()) return;
      if (track._raf) cancelAnimationFrame(track._raf);
      drag = {
        id: event.pointerId,
        x: event.clientX,
        scroll: track.scrollLeft,
        moved: false
      };
      track.classList.add("is-dragging");
      if (track.setPointerCapture) {
        try { track.setPointerCapture(event.pointerId); } catch (err) {}
      }
      event.preventDefault();
    });

    track.addEventListener("pointermove", function (event) {
      if (!drag || event.pointerId !== drag.id) return;
      var dx = event.clientX - drag.x;
      if (Math.abs(dx) > 4) drag.moved = true;
      track.scrollLeft = drag.scroll - dx;
    });

    function endDrag(event) {
      if (!drag || event.pointerId !== drag.id) return;
      var moved = drag.moved;
      drag = null;
      track.classList.remove("is-dragging");
      if (!moved) return;
      track.addEventListener("click", function block(clickEvent) {
        clickEvent.preventDefault();
        clickEvent.stopPropagation();
        track.removeEventListener("click", block, true);
      }, true);
    }

    track.addEventListener("pointerup", endDrag);
    track.addEventListener("pointercancel", endDrag);
    track.addEventListener("dragstart", function (event) {
      event.preventDefault();
    });

    track.addEventListener("wheel", function (event) {
      if (!canScroll()) return;
      var scale = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? track.clientWidth : 1;
      var absX = Math.abs(event.deltaX);
      var absY = Math.abs(event.deltaY);
      var delta = (absX > absY ? event.deltaX : event.deltaY) * scale;
      if (!delta) return;
      var max = track.scrollWidth - track.clientWidth;
      var next = track.scrollLeft + delta;
      var horizontal = absX > absY;
      if (!horizontal && (next < 0 || next > max)) return;
      event.preventDefault();
      track.scrollLeft = Math.max(0, Math.min(max, next));
    }, { passive: false });
  });

  var topbar = document.querySelector(".topbar");
  var nav = document.querySelector(".nav");
  if (nav) {
    nav.addEventListener("animationend", function (event) {
      if (event.target === nav && event.animationName === "nav-in") nav.classList.add("settled");
    });
    document.querySelectorAll(".nav-links a, .nav > .btn").forEach(function (el) {
      el.addEventListener("animationend", function (event) {
        if (event.animationName === "rise") el.classList.add("settled");
      });
    });
  }
  var dock = document.querySelector(".dock");
  var contact = document.querySelector("#contatti, #richiesta");
  var footer = document.querySelector(".footer");
  var lastY = window.scrollY;
  var dockOn = false;
  var dockImmediate = dock && !document.querySelector(".hero");

  function lowerBusy(el) {
    if (!el) return false;
    var rect = el.getBoundingClientRect();
    var view = window.innerHeight;
    return rect.top < view - 72 && rect.bottom > view * 0.62;
  }

  function onScroll() {
    var y = window.scrollY;
    var delta = y - lastY;
    var menuOpen = document.querySelector(".nav-links.open");
    if (topbar && !motion) {
      topbar.classList.toggle("is-scrolled", y > 20);
      topbar.classList.toggle("is-away", !menuOpen && delta > 0 && y > 140);
    }
    if (dock) {
      var blocked = menuOpen || lowerBusy(contact);
      if (dockImmediate) dockOn = !blocked;
      else if (blocked || y < 320 || lowerBusy(footer)) dockOn = false;
      else if (delta > 8) dockOn = true;
      else if (delta < -8) dockOn = false;
      dock.classList.toggle("is-on", dockOn);
      dock.setAttribute("aria-hidden", dockOn ? "false" : "true");
      if (dockOn) dock.removeAttribute("inert");
      else dock.setAttribute("inert", "");
    }
    lastY = y;
  }

  if (topbar || dock) {
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  var mesi = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"];

  function esc(value) {
    return String(value || "").replace(/[&<>"']/g, function (char) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char];
    });
  }

  function dataIt(iso) {
    var parts = String(iso || "").split("-");
    if (parts.length !== 3) return esc(iso);
    var giorno = Number(parts[2]);
    var mese = mesi[Number(parts[1]) - 1];
    if (!giorno || !mese) return esc(iso);
    return giorno + " " + mese + " " + parts[0];
  }

  function destinazione(item) {
    if (String(item.testo || "").trim() && item.slug) {
      return "notizie/" + encodeURIComponent(item.slug) + ".html";
    }
    var link = String(item.link || "");
    if (!link || /^https?:/i.test(link) || link.indexOf("//") === 0) return "";
    return link;
  }

  function scheda(item) {
    var href = destinazione(item);
    var immagine = item.immagine
      ? '<img src="' + esc(item.immagine) + '" alt="" onerror="this.remove()">'
      : "";
    var corpo = '<div class="news-body"><p class="news-meta">' + esc(item.categoria) + " · " + dataIt(item.data) + "</p><h3>" + esc(item.titolo) + "</h3><p>" + esc(item.descrizione) + "</p>" + (href ? '<span class="news-more">Leggi l\'articolo</span>' : "") + "</div>";
    if (!href) return "<li>" + immagine + corpo + "</li>";
    return '<li><a href="' + esc(href) + '">' + immagine + corpo + "</a></li>";
  }

  function paragrafi(testo) {
    return String(testo || "").split(/\n\s*\n/).filter(function (blocco) {
      return blocco.trim();
    }).map(function (blocco) {
      return "<p>" + esc(blocco).replace(/\n/g, "<br>") + "</p>";
    }).join("");
  }

  var elenco = document.querySelector("[data-articoli]");
  var pagina = document.querySelector("#articolo");

  if (elenco || pagina) {
    fetch("articoli.json")
      .then(function (response) { if (!response.ok) throw new Error("json"); return response.json(); })
      .then(function (dati) {
        var articoli = (dati && dati.articoli) || [];
        if (elenco) {
          if (!articoli.length) {
            elenco.innerHTML = "<li><div class=\"news-body\"><p>Nessuna nota pubblicata.</p></div></li>";
            return;
          }
          elenco.innerHTML = articoli.map(scheda).join("");
        }
        if (!pagina) return;
        var slug = new URLSearchParams(window.location.search).get("slug");
        var item = articoli.filter(function (articolo) { return articolo.slug === slug; })[0];
        if (!item || !String(item.testo || "").trim()) {
          pagina.innerHTML = "<h1>Articolo non trovato.</h1><p>La nota non è disponibile oppure non ha ancora un testo sul sito.</p>";
          return;
        }
        document.title = item.titolo + " | Studio Legale Lupone";
        var cover = item.immagine ? '<img class="article-cover" src="' + esc(item.immagine) + '" alt="" onerror="this.remove()">' : "";
        pagina.innerHTML = cover + '<p class="news-meta">' + esc(item.categoria) + " · " + dataIt(item.data) + "</p><h1>" + esc(item.titolo) + "</h1><p class=\"lead\">" + esc(item.descrizione) + "</p>" + paragrafi(item.testo);
      })
      .catch(function () {
        if (elenco && !elenco.querySelector("a")) {
          elenco.innerHTML = "<li><div class=\"news-body\"><p>Le notizie non sono disponibili in questo momento.</p></div></li>";
        }
        if (pagina) pagina.innerHTML = "<h1>Articolo non disponibile.</h1>";
      });
  }

  var parametri = new URLSearchParams(window.location.search);
  var materiaIniziale = document.querySelector("#materia");
  var avvocatoIniziale = document.querySelector("#destinatario");
  if (avvocatoIniziale && parametri.get("destinatario")) avvocatoIniziale.value = parametri.get("destinatario");
  if (materiaIniziale && parametri.get("materia")) materiaIniziale.value = parametri.get("materia");

  document.querySelectorAll("[data-area], [data-lawyer]").forEach(function (link) {
    link.addEventListener("click", function () {
      var materia = document.querySelector("#materia");
      var lawyer = document.querySelector("#destinatario");
      var area = link.getAttribute("data-area");
      var who = link.getAttribute("data-lawyer");
      if (materia && area) materia.value = area;
      if (lawyer && who) lawyer.value = who;
    });
  });

  var form = document.querySelector("#richiesta");
  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var data = new FormData(form);
      var to = data.get("destinatario");
      var subject = "Richiesta di appuntamento — " + data.get("materia");
      var body = [
        "Nome: " + data.get("nome"),
        "Email: " + data.get("email"),
        "Telefono: " + data.get("telefono"),
        "Materia: " + data.get("materia"),
        "Sede preferita: " + data.get("sede"),
        "",
        data.get("messaggio")
      ].join("\n");
      window.location.href =
        "mailto:" + encodeURIComponent(to) +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);
    });
  }
})();
