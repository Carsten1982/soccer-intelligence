/* Soccer Intelligence – Website (seit 0.17). Wenig JavaScript, alles funktioniert auch ohne:
   1. Tabs der englischen Woche (Entwurf 3d): ohne JavaScript stehen alle Spieltage untereinander.
   2. „Zuklappen“ im Matchdetail schliesst den aufgeklappten Bereich „Zahlen im Detail“ (Entwurf 2i). */
document.querySelectorAll('[data-tabs]').forEach(function (box) {
  var leiste = box.querySelector('.tabs');
  var knoepfe = box.querySelectorAll('[data-tab]');
  var panels = box.querySelectorAll('[data-panel]');
  var subs = box.querySelectorAll('[data-sub]');
  if (!leiste) return;
  function zeige(i) {
    knoepfe.forEach(function (k, j) { k.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
    panels.forEach(function (p, j) { p.hidden = j !== i; });
    subs.forEach(function (s, j) { s.hidden = j !== i; });
  }
  knoepfe.forEach(function (k, i) { k.addEventListener('click', function () { zeige(i); }); });
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
