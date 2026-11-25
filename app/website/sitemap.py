"""Sitemap und robots.txt (seit 0.21; SEO-Briefing 3.3 und 4).

- /sitemap.xml ist ein Sitemap-Index mit Teilen: /sitemaps/seiten.xml (Startseite, Spieltag je Liga, Methodik,
  Glossar, Kontakt, Impressum, Datenschutz) und je Liga und Saison /sitemaps/<liga>-<saison>.xml (Spiel- und
  Archivseiten). Neue Saisons kommen als weitere Teile hinzu.
- Jeder Eintrag nennt mit xhtml:link beide Sprachfassungen und x-default (Deutsch). Absolute Adressen auf der Domain.
- Aufgenommen wird nur, was indexierbar ist: dieselben Funktionen wie für das robots-Tag der Seite (seo.py), damit
  Seite und Sitemap nie auseinanderlaufen. Nicht enthalten: Cookie-Einstellungen, 404, alle noindex-Seiten.
- Vor dem Livegang (index_ab leer) enthalten die Teile je Liga und Saison darum keine Einträge. Seit 0.27 (Livegang)
  stehen im Teil der laufenden Saison alle begonnenen Spieltage (Archiv), in früheren Saisons keine Archivseiten.
"""

from __future__ import annotations

from datetime import date
from html import escape

from . import adressen as A
from . import einstellungen as W
from . import seo

XMLNS = ('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
         'xmlns:xhtml="http://www.w3.org/1999/xhtml"')
SEITEN = ("start", "methodik", "glossar", "kontakt", "impressum", "datenschutz")


def robots() -> str:
    """robots.txt der Domain: alles erlaubt (noindex-Seiten werden nicht gesperrt, sonst sähe Google das noindex nicht)."""
    return f"User-agent: *\nAllow: /\n\nSitemap: {W.DOMAIN}/sitemap.xml\n"


def _url(ziel: A.Ziel) -> str:
    """Ein Eintrag je Sprachfassung mit Verweisen auf alle Fassungen und x-default."""
    zeilen = []
    for lang in W.SPRACHEN:
        loc = W.DOMAIN + A.pfad(ziel.in_sprache(lang))
        links = "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{escape(W.DOMAIN + A.pfad(ziel.in_sprache(x)))}"/>'
                        for x in W.SPRACHEN)
        links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{escape(W.DOMAIN + A.pfad(ziel.in_sprache(W.SPRACHE)))}"/>'
        zeilen.append(f"<url><loc>{escape(loc)}</loc>{links}</url>")
    return "".join(zeilen)


def _teile(daten) -> list[str]:
    """Namen der Teile je Liga und Saison (nur Saisons mit Seiten)."""
    b = daten.bestand()
    out = []
    for web in W.LIGEN:
        plan = b.fx.leagues.get(web.name)
        if plan is None or plan.empty:
            continue
        for saison in sorted(set(plan["saison"])):
            if seo.saison_hat_seiten(saison):
                out.append(f"{web.slug}-{A.saison_slug(saison)}")
    return out


def sitemap(rest: str, daten) -> str | None:
    """XML zu /sitemap.xml oder /sitemaps/<teil>.xml; None, wenn es den Teil nicht gibt."""
    if rest == "/sitemap.xml":
        teile = ["seiten", *_teile(daten)]
        eintraege = "".join(f"<sitemap><loc>{W.DOMAIN}/sitemaps/{t}.xml</loc></sitemap>" for t in teile)
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{eintraege}</sitemapindex>\n')
    name = rest.removeprefix("/sitemaps/").removesuffix(".xml")
    if name == "seiten":
        ziele = [A.Ziel(art) for art in SEITEN] + [A.Ziel("spieltag", liga=lg.slug) for lg in W.LIGEN]
        return _urlset(ziele)
    if name not in _teile(daten):
        return None
    return _urlset(_liga_saison(name, daten))


def _urlset(ziele: list[A.Ziel]) -> str:
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset {XMLNS}>' + "".join(_url(z) for z in ziele) + "</urlset>\n"


def _liga_saison(name: str, daten) -> list[A.Ziel]:
    """Indexierbare Spiel- und Archivseiten einer Liga und Saison (vor dem Livegang keine)."""
    k = seo.konfig()
    if k.index_ab is None:
        return []
    from .spiel import spiel_daten           # hier, weil spiel.py die Daten braucht (kein Kreisbezug beim Laden)
    from .spieltag import archiv_daten
    web = next(lg for lg in W.LIGEN if name.startswith(lg.slug + "-"))
    saison = A.saison_aus_slug(name[len(web.slug) + 1:])
    zp = daten.zeitpunkt()
    plan = daten.spielplan(web.name)
    spiele = plan[(plan["saison"] == saison) & (plan["anstoss_zeit"] >= k.index_ab)]
    ziele = []
    # Archiv: seit 0.27 alle begonnenen Spieltage der laufenden Saison (auch vor dem Livegang), ältere Saisons nicht
    # (dort wird das Archiv gar nicht erst berechnet)
    nummern = plan.loc[plan["saison"] == saison, "spieltag"] if saison == seo.laufende_saison(plan) else []
    for nr in sorted({int(x) for x in nummern}):
        seite = archiv_daten(daten, web, saison, nr, zp)
        if seite is not None and seo.archiv_indexierbar(date.fromisoformat(seite["beginn"]), k, saison,
                                                        seite.get("aktuelle_saison")):
            ziele.append(A.Ziel("archiv", liga=web.slug, saison=saison, nr=nr))
    for row in spiele.itertuples():
        if row.api_id is None or row.api_id != row.api_id:
            continue
        seite = spiel_daten(daten, int(row.api_id), zp)
        if seite is not None and seo.spiel_indexierbar(seite, k):
            ziele.append(A.Ziel("spiel", liga=web.slug, slug=seite["slug"], spiel_id=seite["id"]))
    return ziele
