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
