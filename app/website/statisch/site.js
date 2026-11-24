/* Soccer Intelligence – Website (seit 0.17). Wenig JavaScript, alles funktioniert auch ohne:
   1. Tabs der englischen Woche (Entwurf Spieltag_P1): ohne JavaScript stehen alle Spieltage untereinander, mit
      Überschrift und Sprungliste. Erst wenn das Skript läuft, verschwinden Sprungliste und Überschriften und die
      Tab-Leiste erscheint (Beschluss 19.11.2026).
   2. „Zuklappen“ auf der Spielseite schliesst den aufgeklappten Bereich „Zahlen im Detail“ (Entwurf Spiel_P1).
   3. Sprachmenü (seit 0.21): öffnet und schliesst ohne Skript über <details>; das Skript schliesst es zusätzlich mit
      Escape und bei einem Klick ausserhalb. */
document.querySelectorAll('[data-tabs]').forEach(function (box) {
  var leiste = box.querySelector('.tabs');
  var knoepfe = box.querySelectorAll('[data-tab]');
  var panels = box.querySelectorAll('[data-panel]');
  if (!leiste) return;
  function zeige(i) {
    knoepfe.forEach(function (k, j) { k.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
    panels.forEach(function (p, j) { p.hidden = j !== i; });
  }
  knoepfe.forEach(function (k, i) { k.addEventListener('click', function () { zeige(i); }); });
  box.querySelectorAll('[data-sprungliste], [data-tabtitel]').forEach(function (el) { el.hidden = true; });
  leiste.hidden = false;
  zeige(0);
});
document.querySelectorAll('[data-zuklappen]').forEach(function (knopf) {
  knopf.hidden = false;
  knopf.addEventListener('click', function () {
    var d = knopf.closest('details');
    if (d) { d.open = false; d.querySelector('summary').focus(); }
  });
});
document.querySelectorAll('[data-sprachmenue]').forEach(function (menue) {
  var knopf = menue.querySelector('summary');
  function zu(fokus) {
    if (!menue.open) return;
    menue.open = false;
    if (fokus) knopf.focus();
  }
  menue.addEventListener('toggle', function () { knopf.setAttribute('aria-expanded', menue.open ? 'true' : 'false'); });
  knopf.setAttribute('aria-expanded', 'false');
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') zu(true); });
  document.addEventListener('click', function (e) { if (!menue.contains(e.target)) zu(false); });
});
/* 4. Methodik (seit 0.21.1, Entwurfsrunde 20.11.2026): Einstieg „Wie tief möchtest du einsteigen?“. Die gewählte Karte ist
      dunkel, tiefere Ebenen (und der Download bei Ebene 3) werden ausgeblendet. Ohne Skript ist alles sichtbar.
      Start: Ebene aus der Adresse (#ebene2), sonst 1. Die Weiter-Schaltflächen springen zur nächsten Ebene. */
document.querySelectorAll('[data-tiefe]').forEach(function (nav) {
  var karten = nav.querySelectorAll('.tiefe-karte');
  var teile = document.querySelectorAll('[data-ebene]');
  function zeige(n) {
    karten.forEach(function (k) { k.setAttribute('aria-current', k.getAttribute('data-tiefe-wahl') === String(n) ? 'true' : 'false'); });
    teile.forEach(function (t) { t.hidden = Number(t.getAttribute('data-ebene')) > n; });
  }
  var start = /^#ebene([123])$/.exec(location.hash);
  zeige(start ? Number(start[1]) : 1);
  document.querySelectorAll('[data-tiefe-wahl]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      var n = Number(el.getAttribute('data-tiefe-wahl'));
      var bisher = Math.max.apply(null, Array.prototype.map.call(teile, function (t) { return t.hidden ? 0 : Number(t.getAttribute('data-ebene')); }));
      if (el.hasAttribute('data-springen')) {
        zeige(Math.max(n, bisher));
        if (el.hasAttribute('data-aufklappen')) document.querySelectorAll('#ebene' + n + ' details').forEach(function (d) { d.open = true; });
        return;                                     /* der Link springt selbst zur Ebene */
      }
      e.preventDefault();
      zeige(n);
      if (history.replaceState) history.replaceState(null, '', '#ebene' + n);
    });
  });
});

// Seit 0.23 (Entwurf 2k final, Beschluss 29): „Nicht eingestuft ⓘ“ und „keine ⓘ“ klappen den Erklärsatz auf. Ohne
// Skript steht der Satz offen da; mit Skript ist er zu, bis man den Knopf antippt (aria-expanded).
document.querySelectorAll('[data-aufklapp]').forEach(function (knopf) {
  var ziel = document.getElementById(knopf.getAttribute('data-aufklapp'));
  if (!ziel) { return; }
  ziel.hidden = true;
  knopf.setAttribute('aria-expanded', 'false');
  knopf.addEventListener('click', function () {
    var offen = knopf.getAttribute('aria-expanded') === 'true';
    knopf.setAttribute('aria-expanded', offen ? 'false' : 'true');
    ziel.hidden = offen;
  });
});

// Seit 0.23 (Template-Briefing T5): Das Kontaktformular funktioniert ohne Skript; mit Skript wird der Knopf nach dem
// Absenden gesperrt, damit eine Nachricht nicht doppelt geht.
document.querySelectorAll('form[data-ein-klick]').forEach(function (form) {
  form.addEventListener('submit', function () {
    var knopf = form.querySelector('button[type="submit"]');
    if (knopf) { window.setTimeout(function () { knopf.disabled = true; }, 0); }
  });
});
