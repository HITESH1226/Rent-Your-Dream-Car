/* CarRent – site-wide behaviour. Plain JavaScript, no build step. */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  document.documentElement.classList.remove("no-js");

  /* ---------- helpers ---------- */
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function toISO(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function parseISO(s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function addDays(d, n) { var x = new Date(d.getTime()); x.setDate(x.getDate() + n); return x; }
  function fmtDate(s) {
    return parseISO(s).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  }
  function rupees(n) { return "₹" + Number(n).toLocaleString("en-IN"); }

  function toast(message) {
    var stack = $(".toast-stack");
    if (!stack) {
      stack = document.createElement("div");
      stack.className = "toast-stack";
      stack.setAttribute("role", "status");
      document.body.appendChild(stack);
    }
    var t = document.createElement("div");
    t.className = "toast-msg";
    t.textContent = message;
    stack.appendChild(t);
    setTimeout(function () { t.remove(); }, 3500);
  }

  /* ---------- footer year ---------- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- navbar shrink on scroll ---------- */
  var nav = $("#mainNav");
  if (nav) {
    var onScroll = function () { nav.classList.toggle("scrolled", window.scrollY > 30); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- reveal on scroll ---------- */
  var revealEls = $$(".reveal");
  if (revealEls.length) {
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
        });
      }, { threshold: 0.12 });
      revealEls.forEach(function (el, i) {
        el.style.transitionDelay = Math.min((i % 4) * 80, 240) + "ms";
        io.observe(el);
      });
    } else {
      revealEls.forEach(function (el) { el.classList.add("in"); });
    }
  }

  /* ---------- fleet: filter + search + sort ---------- */
  var grid = $("#carGrid");
  if (grid) {
    var cols = $$(".car-col", grid);
    cols.forEach(function (c, i) { c.dataset.order = i; });
    var state = { filter: "all", q: "", sort: "default" };
    var countEl = $("#carCount"), emptyEl = $("#carEmpty");

    var renderFleet = function () {
      var q = state.q.trim().toLowerCase();
      var visible = cols.filter(function (c) {
        var okCat = state.filter === "all" || c.dataset.category === state.filter;
        var okText = !q || (c.dataset.name + " " + c.dataset.category + " " + c.textContent).toLowerCase().indexOf(q) !== -1;
        var show = okCat && okText;
        c.hidden = !show;
        return show;
      });
      var sorted = cols.slice().sort(function (a, b) {
        if (state.sort === "low") return a.dataset.price - b.dataset.price;
        if (state.sort === "high") return b.dataset.price - a.dataset.price;
        if (state.sort === "name") return a.dataset.name.localeCompare(b.dataset.name);
        return a.dataset.order - b.dataset.order;
      });
      sorted.forEach(function (c) { grid.appendChild(c); });
      countEl.textContent = "Showing " + visible.length + " of " + cols.length + " cars";
      emptyEl.hidden = visible.length > 0;
    };

    $$(".filter-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        $$(".filter-btn").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        state.filter = btn.dataset.filter;
        renderFleet();
      });
    });
    $("#carSearch").addEventListener("input", function (e) { state.q = e.target.value; renderFleet(); });
    $("#carSort").addEventListener("change", function (e) { state.sort = e.target.value; renderFleet(); });
    $("#carReset").addEventListener("click", function () {
      state = { filter: "all", q: "", sort: "default" };
      $("#carSearch").value = ""; $("#carSort").value = "default";
      $$(".filter-btn").forEach(function (b) { b.classList.toggle("active", b.dataset.filter === "all"); });
      renderFleet();
    });
    renderFleet();
  }

  /* ---------- gallery lightbox ---------- */
  var modalImg = $("#modalImage");
  if (modalImg) {
    var items = $$(".gallery-item"), current = 0;
    var show = function (i) {
      current = (i + items.length) % items.length;
      modalImg.src = items[current].dataset.img;
      modalImg.alt = items[current].querySelector("img").alt;
      $("#lbCount").textContent = (current + 1) + " / " + items.length;
    };
    items.forEach(function (it, i) { it.addEventListener("click", function () { show(i); }); });
    $("#lbPrev").addEventListener("click", function () { show(current - 1); });
    $("#lbNext").addEventListener("click", function () { show(current + 1); });
    document.addEventListener("keydown", function (e) {
      if (!$("#imageModal").classList.contains("show")) return;
      if (e.key === "ArrowLeft") show(current - 1);
      if (e.key === "ArrowRight") show(current + 1);
    });
  }

  /* ---------- confirm dialogs: <form data-confirm="..."> ---------- */
  $$("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.dataset.confirm)) e.preventDefault();
    });
  });

  /* ---------- generic validation ---------- */
  function groupOf(input) {
    var wrap = input.closest(".input-wrap");
    return (wrap || input).parentElement;
  }
  function checkField(input) {
    var ok = input.checkValidity() && (input.type === "password" || input.type === "date" || input.value.trim() !== "" || !input.required);
    groupOf(input).classList.toggle("invalid", !ok);
    return ok;
  }
  function wireLive(form) {
    $$("input, textarea", form).forEach(function (inp) {
      inp.addEventListener("blur", function () { if (inp.value !== "") checkField(inp); });
      inp.addEventListener("input", function () { if (groupOf(inp).classList.contains("invalid")) checkField(inp); });
    });
  }
  function validateForm(form) {
    var first = null;
    $$("input, textarea", form).forEach(function (inp) {
      if (inp.type === "hidden") return;
      if (!checkField(inp) && !first) first = inp;
    });
    if (first) first.focus();
    return !first;
  }
  function setLoading(btn) {
    if (!btn) return;
    btn.disabled = true;
    btn.dataset.original = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>' + (btn.dataset.loadingText || "Please wait…");
  }

  $$("form[data-validate]").forEach(function (form) {
    wireLive(form);
    form.addEventListener("submit", function (e) {
      if (!validateForm(form)) { e.preventDefault(); return; }
      setLoading($("button[type=submit]", form));
    });
  });

  /* ---------- password: show/hide + strength ---------- */
  $$("[data-toggle-password]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = document.getElementById(btn.dataset.togglePassword);
      var showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.setAttribute("aria-label", showing ? "Show password" : "Hide password");
      btn.innerHTML = '<i class="bi bi-eye' + (showing ? "" : "-slash") + '"></i>';
    });
  });
  var strengthInput = $("[data-strength]");
  if (strengthInput) {
    var bar = $("#pwBar"), hint = $("#pwHint");
    var levels = [
      ["12%", "var(--danger)", "Too weak"], ["35%", "var(--danger)", "Weak"],
      ["60%", "var(--warning)", "Okay"], ["82%", "var(--success)", "Good"], ["100%", "var(--success)", "Strong"]
    ];
    strengthInput.addEventListener("input", function () {
      var v = strengthInput.value, score = 0;
      if (!v) { bar.style.width = "0"; hint.textContent = "Use at least 6 characters. Longer is better."; return; }
      if (v.length >= 6) score++;
      if (v.length >= 10) score++;
      if (/[A-Z]/.test(v) && /[a-z]/.test(v)) score++;
      if (/\d/.test(v) && /[^A-Za-z0-9]/.test(v)) score++;
      var l = levels[score];
      bar.style.width = l[0]; bar.style.background = l[1]; hint.textContent = "Password strength: " + l[2];
    });
  }

  /* ---------- booking form: dates + live estimate ---------- */
  var bookingForm = $("#bookingForm");
  if (bookingForm) {
    var price = +bookingForm.dataset.price;
    var pickup = $("#pickup_date"), ret = $("#return_date");
    var today = toISO(new Date());
    pickup.min = today; ret.min = toISO(addDays(new Date(), 1));

    var update = function () {
      if (pickup.value) {
        var minReturn = toISO(addDays(parseISO(pickup.value), 1));
        ret.min = minReturn;
        if (ret.value && ret.value < minReturn) ret.value = "";
      }
      $("#sumPickup").textContent = pickup.value ? fmtDate(pickup.value) : "—";
      $("#sumReturn").textContent = ret.value ? fmtDate(ret.value) : "—";
      if (pickup.value && ret.value) {
        var days = Math.round((parseISO(ret.value) - parseISO(pickup.value)) / 86400000);
        if (days > 0) {
          $("#sumDays").textContent = days + (days === 1 ? " day" : " days");
          $("#sumTotal").textContent = rupees(days * price);
          return;
        }
      }
      $("#sumDays").textContent = "—"; $("#sumTotal").textContent = "₹0";
    };
    pickup.addEventListener("change", update);
    ret.addEventListener("change", update);
    wireLive(bookingForm);

    bookingForm.addEventListener("submit", function (e) {
      var ok = true;
      if (!pickup.value || pickup.value < today) { groupOf(pickup).classList.add("invalid"); ok = false; }
      if (!ret.value || (pickup.value && ret.value <= pickup.value)) { groupOf(ret).classList.add("invalid"); ok = false; }
      if (!ok) { e.preventDefault(); (groupOf(pickup).classList.contains("invalid") ? pickup : ret).focus(); return; }
      setLoading($("#bookBtn"));
    });
    update();
  }

  /* ---------- tables: status tabs + search ---------- */
  $$("[data-status-tabs]").forEach(function (tabs) {
    var body = $(tabs.dataset.statusTabs);
    var empty = document.getElementById(body.id + "Empty");
    var searchInput = $('[data-table-search="#' + body.id + '"]');
    var status = "all", q = "";
    var apply = function () {
      var shown = 0;
      $$("tr", body).forEach(function (row) {
        var ok = (status === "all" || row.dataset.status === status) &&
                 (!q || row.textContent.toLowerCase().indexOf(q) !== -1);
        row.hidden = !ok;
        if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    };
    $$(".tab-btn", tabs).forEach(function (btn) {
      btn.addEventListener("click", function () {
        $$(".tab-btn", tabs).forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        status = btn.dataset.status;
        apply();
      });
    });
    if (searchInput) searchInput.addEventListener("input", function () { q = searchInput.value.trim().toLowerCase(); apply(); });
  });

  /* ---------- print ---------- */
  $$("[data-print]").forEach(function (b) { b.addEventListener("click", function () { window.print(); }); });

  /* ---------- contact form: opens the visitor's e-mail app ---------- */
  var contactForm = $("#contactForm");
  if (contactForm) {
    wireLive(contactForm);
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validateForm(contactForm)) return;
      var f = contactForm.elements;
      var body = f.message.value + "\n\n— " + f.name.value + " (" + f.email.value + ")";
      window.location.href = "mailto:support@carforrent.com?subject=" + encodeURIComponent(f.subject.value) +
                             "&body=" + encodeURIComponent(body);
      toast("Opening your e-mail app…");
    });
  }
})();
