/* Soccer Intelligence – Website (seit 0.17). Tabs der englischen Woche (Übergabe 6.4).
   Ohne JavaScript stehen alle Spieltage untereinander; mit JavaScript ist der frühere Spieltag ausgewählt. */
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
  leiste.hidden = false;
  zeige(0);
});
