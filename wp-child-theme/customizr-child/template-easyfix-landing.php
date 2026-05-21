<?php
/**
 * Template Name: EasyFix Landing
 *
 * Plantilla de página completa para la landing de EasyFix.
 * No carga el header ni footer del tema — la página es autocontenida.
 * Sube este archivo al child theme y asígnalo a la página /productos/easyfix/
 */

// Landing autocontenida: elimina TODOS los estilos y scripts de WordPress/tema
// justo antes de imprimirlos para evitar interferencias de scroll del tema Customizr.
add_action( 'wp_print_styles', function () {
    global $wp_styles;
    $wp_styles->queue = [];
}, 999 );
add_action( 'wp_print_scripts', function () {
    global $wp_scripts;
    $wp_scripts->queue = [];
}, 999 );

// Rutas de logos (en /assets/ del child theme)
$logo_full   = get_stylesheet_directory_uri() . '/assets/easyfix-logo.png';
$logo_symbol = get_stylesheet_directory_uri() . '/assets/easyfix-symbol.png';
$logo_pro    = get_stylesheet_directory_uri() . '/assets/easyfix-pro-symbol.png';
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EasyFix — App de gestión para talleres mecánicos · Android</title>
  <meta name="description" content="EasyFix: la app Android que organiza tu taller mecánico. Órdenes de trabajo, stock, facturación y Verifactu. Versión gratuita disponible en Google Play.">
  <?php wp_head(); /* Mantiene SEO (Yoast/RankMath), Google Analytics, etc. */ ?>
  <style>
    /* Eliminar margen superior de la barra de administración de WordPress */
    html { margin-top: 0 !important; overflow-y: auto !important; height: auto !important; }
    body { overflow-y: visible !important; height: auto !important; }
    #wpadminbar { display: none !important; }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --amber:  #f57c00; --amber2: #ff9800;
      --dark:   #0d1620; --navy:   #1a2744; --slate:  #37474f;
      --blue:   #1565c0; --muted:  #546e7a; --light:  #f5f7fa;
      --r: 14px;
      --sh:  0 4px 28px rgba(13,22,32,.11);
      --sh2: 0 14px 52px rgba(13,22,32,.22);
    }
    html { scroll-behavior: smooth; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: var(--navy); background: #fff; line-height: 1.6;
    }
    a { text-decoration: none; }
    h1,h2,h3,h4 { line-height: 1.2; }

    /* ── NAV ── */
    .ef-nav {
      position: fixed; top:0; left:0; right:0; z-index:200;
      background: rgba(13,22,32,.96); backdrop-filter: blur(14px);
      border-bottom: 1px solid rgba(255,255,255,.07);
      height: 64px; display:flex; align-items:center; justify-content:space-between;
      padding: 0 5vw;
    }
    .ef-nav__brand { display:flex; align-items:center; gap:10px; }
    .ef-nav__sym   { width:34px; height:34px; }
    .ef-nav__name  { font-size:1.15rem; font-weight:900; letter-spacing:-.02em; color:white; }
    .ef-nav__name em { font-style:normal; color:var(--amber); }
    .ef-nav__links { display:flex; gap:24px; align-items:center; }
    .ef-nav__links a { color:rgba(255,255,255,.68); font-size:.88rem; font-weight:500; transition:color .15s; }
    .ef-nav__links a:hover { color:white; }
    .ef-nav__dl { background:var(--amber); color:white !important; font-weight:700 !important; padding:9px 22px; border-radius:8px; transition:background .15s !important; }
    .ef-nav__dl:hover { background:#e65100 !important; }

    /* ── HERO ── */
    .ef-hero {
      min-height: 100vh; background: var(--dark);
      display:flex; align-items:center; position:relative;
      padding: 100px 5vw 80px;
    }
    .ef-hero::before {
      content:''; position:absolute; inset:0; pointer-events:none;
      background:
        radial-gradient(ellipse 65% 60% at 80% 50%, rgba(245,124,0,.17) 0%, transparent 60%),
        radial-gradient(ellipse 35% 45% at 8% 80%, rgba(21,101,192,.11) 0%, transparent 55%);
    }
    .ef-hero::after {
      content:''; position:absolute; inset:0; pointer-events:none;
      background-image: linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
      background-size: 48px 48px;
    }
    .ef-hero__inner {
      max-width:1160px; margin:0 auto; width:100%;
      display:grid; grid-template-columns:1fr 1fr; gap:64px; align-items:center;
      position:relative; z-index:1;
    }
    .ef-hero__logo { width:200px; margin-bottom:24px; display:block; filter:drop-shadow(0 0 12px rgba(245,124,0,.35)); }
    .ef-hero__badge {
      display:inline-flex; align-items:center; gap:8px;
      background:rgba(245,124,0,.14); border:1px solid rgba(245,124,0,.32);
      color:var(--amber2); font-size:.76rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
      padding:5px 15px; border-radius:20px; margin-bottom:18px;
    }
    .ef-hero__badge-dot { width:7px; height:7px; border-radius:50%; background:var(--amber2); animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.35;transform:scale(.65)} }
    .ef-hero__title { font-size:clamp(2.2rem,4.5vw,3.3rem); font-weight:900; color:white; letter-spacing:-.03em; margin-bottom:18px; }
    .ef-hero__title em { font-style:normal; background:linear-gradient(90deg,var(--amber),var(--amber2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
    .ef-hero__sub { font-size:1.15rem; color:rgba(255,255,255,.7); line-height:1.75; margin-bottom:34px; max-width:480px; }
    .ef-hero__btns { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:28px; }
    .ef-btn-gp {
      display:inline-flex; align-items:center; gap:12px;
      background:var(--amber); color:white; padding:13px 24px; border-radius:12px;
      font-weight:700; font-size:1rem; box-shadow:0 4px 20px rgba(245,124,0,.38);
      transition:transform .18s,box-shadow .18s;
    }
    .ef-btn-gp:hover { transform:translateY(-2px); box-shadow:0 8px 28px rgba(245,124,0,.5); color:white; }
    .ef-btn-gp__icon { font-size:1.4rem; }
    .ef-btn-gp small { font-size:.7rem; opacity:.82; display:block; line-height:1.2; }
    .ef-btn-gp strong { font-size:.98rem; display:block; }
    .ef-btn-gp--ghost { background:rgba(255,255,255,.08); border:1.5px solid rgba(255,255,255,.22); box-shadow:none; }
    .ef-btn-gp--ghost:hover { background:rgba(255,255,255,.15); box-shadow:none; }
    .ef-hero__trust { font-size:.83rem; color:rgba(255,255,255,.48); display:flex; gap:6px; flex-wrap:wrap; }
    .ef-hero__trust span { color:#66bb6a; }

    /* Phone mockup */
    .ef-hero__visual { display:flex; justify-content:center; align-items:center; position:relative; }
    .ef-glow { position:absolute; width:360px; height:360px; border-radius:50%; background:radial-gradient(circle,rgba(245,124,0,.2) 0%,transparent 70%); top:50%; left:50%; transform:translate(-50%,-50%); pointer-events:none; }
    .ef-phone { width:272px; background:#111928; border-radius:44px; border:2px solid rgba(255,255,255,.10); padding:18px 14px 22px; box-shadow:0 36px 88px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.05); position:relative; z-index:1; }
    .ef-phone-notch { width:72px; height:18px; background:#0d1620; border-radius:0 0 12px 12px; margin:0 auto 12px; }
    .ef-phone-screen { background:linear-gradient(160deg,#1c2b40,#101820); border-radius:22px; overflow:hidden; }
    .ef-ph-hdr { background:var(--amber); padding:13px 14px 9px; display:flex; align-items:center; gap:9px; }
    .ef-ph-hdr-logo { width:26px; height:26px; }
    .ef-ph-hdr-title { color:white; font-weight:900; font-size:.9rem; }
    .ef-ph-body { padding:12px 11px; }
    .ef-ph-stats { display:flex; gap:7px; margin-bottom:9px; }
    .ef-ph-stat { flex:1; background:rgba(255,255,255,.06); border-radius:9px; padding:9px 6px; text-align:center; }
    .ef-ph-stat b { font-size:1.25rem; font-weight:800; color:var(--amber2); display:block; line-height:1; }
    .ef-ph-stat small { font-size:.6rem; color:rgba(255,255,255,.45); display:block; margin-top:2px; }
    .ef-ph-row { background:rgba(255,255,255,.05); border-radius:9px; padding:9px 11px; margin-bottom:7px; display:flex; align-items:center; justify-content:space-between; }
    .ef-ph-row-name { font-size:.74rem; font-weight:700; color:white; }
    .ef-ph-row-plate { font-size:.62rem; color:rgba(255,255,255,.42); }
    .ef-ph-badge { font-size:.6rem; font-weight:700; padding:3px 8px; border-radius:20px; white-space:nowrap; }
    .ef-ph-badge--a { background:rgba(245,124,0,.2); color:var(--amber2); }
    .ef-ph-badge--p { background:rgba(21,101,192,.25); color:#90caf9; }
    .ef-ph-badge--d { background:rgba(76,175,80,.2); color:#a5d6a7; }
    .ef-phone__float { position:absolute; bottom:-14px; left:-28px; z-index:2; background:white; border-radius:14px; padding:11px 15px; box-shadow:0 8px 32px rgba(0,0,0,.28); display:flex; align-items:center; gap:9px; font-size:.8rem; font-weight:600; color:var(--navy); white-space:nowrap; }
    .ef-phone__float small { font-size:.7rem; font-weight:400; color:var(--muted); display:block; }

    /* ── PROOF BAR ── */
    .ef-proof { background:white; border-bottom:1px solid #e8edf2; padding:22px 5vw; }
    .ef-proof__inner { max-width:1100px; margin:0 auto; display:flex; align-items:center; justify-content:center; gap:44px; flex-wrap:wrap; }
    .ef-proof-item { display:flex; align-items:center; gap:9px; font-size:.88rem; color:var(--muted); font-weight:500; }
    .ef-proof-item strong { color:var(--navy); }

    /* ── HOOK ── */
    .ef-hook { padding:80px 5vw; background:var(--light); }
    .ef-hook__inner { max-width:860px; margin:0 auto; text-align:center; }
    .ef-chip { display:inline-block; background:rgba(21,101,192,.1); color:var(--blue); font-size:.74rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; padding:5px 15px; border-radius:20px; margin-bottom:14px; }
    .ef-chip--a { background:rgba(245,124,0,.12); color:var(--amber); }
    .ef-hook h2 { font-size:clamp(1.7rem,3vw,2.35rem); font-weight:800; color:var(--navy); margin-bottom:18px; }
    .ef-hook__lead { font-size:1.1rem; color:var(--muted); line-height:1.8; margin-bottom:40px; }
    .ef-hook__grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
    .ef-hook-card { background:white; border-radius:12px; padding:24px 20px; box-shadow:var(--sh); border-top:3px solid #e0e0e0; transition:transform .2s,box-shadow .2s; }
    .ef-hook-card:hover { transform:translateY(-4px); box-shadow:var(--sh2); }
    .ef-hook-card--bad  { border-top-color:#ef5350; }
    .ef-hook-card--free { border-top-color:var(--amber); }
    .ef-hook-card--pro  { border-top-color:var(--blue); }
    .ef-hook-card__icon { font-size:1.8rem; margin-bottom:10px; }
    .ef-hook-card h4 { font-size:1rem; font-weight:700; color:var(--navy); margin-bottom:6px; }
    .ef-hook-card p  { font-size:.9rem; color:var(--muted); line-height:1.62; }

    /* ── FEATURES ── */
    .ef-features { padding:88px 5vw; background:white; }
    .ef-features__inner { max-width:1160px; margin:0 auto; }
    .ef-sec-head { text-align:center; margin-bottom:52px; }
    .ef-sec-head h2 { font-size:clamp(1.7rem,3vw,2.35rem); font-weight:800; color:var(--navy); margin-bottom:10px; }
    .ef-sec-head p  { font-size:1.03rem; color:var(--muted); max-width:540px; margin:0 auto; }
    .ef-feat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:26px; }
    .ef-feat { border-radius:var(--r); box-shadow:var(--sh); background:white; overflow:hidden; transition:transform .2s,box-shadow .2s; }
    .ef-feat:hover { transform:translateY(-5px); box-shadow:var(--sh2); }
    .ef-feat__head { padding:26px 22px 14px; display:flex; align-items:center; gap:14px; }
    .ef-feat__icon { width:50px; height:50px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:1.4rem; flex-shrink:0; }
    .fi-o{background:#fff3e0} .fi-b{background:#e3f2fd} .fi-t{background:#e0f2f1} .fi-g{background:#e8f5e9} .fi-p{background:#f3e5f5}
    .ef-feat__ttl { font-size:1.02rem; font-weight:700; color:var(--navy); }
    .ef-feat__sub { font-size:.74rem; color:var(--muted); margin-top:1px; }
    .ef-feat__body { padding:0 22px 22px; font-size:.92rem; color:#445566; line-height:1.65; }
    .ef-feat__ul { list-style:none; margin-top:10px; }
    .ef-feat__ul li { padding:5px 0; font-size:.88rem; color:var(--muted); display:flex; align-items:flex-start; gap:8px; }
    .ef-feat__ul li::before { content:'✓'; color:var(--amber); font-weight:700; flex-shrink:0; }

    /* ── VERSIONS ── */
    .ef-versions { padding:88px 5vw; background:var(--light); }
    .ef-versions__inner { max-width:960px; margin:0 auto; }
    .ef-ver-grid { display:grid; grid-template-columns:1fr 1fr; gap:26px; margin-top:44px; }
    .ef-ver-card { background:white; border-radius:20px; box-shadow:var(--sh); overflow:hidden; }
    .ef-ver-card--pro { box-shadow:0 14px 56px rgba(245,124,0,.22); position:relative; }
    .ef-ver-ribbon { position:absolute; top:0; right:30px; background:var(--amber); color:white; font-size:.68rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; padding:5px 15px; border-radius:0 0 10px 10px; }
    .ef-ver-head { padding:30px 26px 22px; display:flex; align-items:center; gap:18px; }
    .ef-ver-head--free { background:linear-gradient(135deg,#e3f2fd,#bbdefb); }
    .ef-ver-head--pro  { background:linear-gradient(135deg,#f57c00,#ff9800); }
    .ef-ver-logo-full  { height:44px; width:auto; display:block; }
    .ef-ver-logo-sym   { width:52px; height:52px; }
    .ef-ver-name  { font-size:1.35rem; font-weight:800; color:var(--navy); margin-bottom:2px; }
    .ef-ver-head--pro .ef-ver-name { color:white; }
    .ef-ver-price { font-size:1rem; font-weight:600; color:var(--blue); }
    .ef-ver-head--pro .ef-ver-price { color:rgba(255,255,255,.88); }
    .ef-ver-body { padding:22px 26px 26px; }
    .ef-chk-list { list-style:none; }
    .ef-chk-list li { padding:8px 0; border-bottom:1px solid #f0f4f8; font-size:.93rem; color:var(--navy); display:flex; align-items:flex-start; gap:9px; }
    .ef-chk-list li:last-child { border-bottom:none; }
    .ef-ck { color:#43a047; font-weight:700; flex-shrink:0; }
    .ef-cx { color:#bdbdbd; flex-shrink:0; }
    .ef-dim { color:var(--muted); }
    .ef-ver-cta { margin-top:18px; }
    .ef-btn-dl { display:flex; align-items:center; justify-content:center; gap:11px; width:100%; padding:14px 18px; border-radius:12px; font-size:.98rem; font-weight:700; color:white; transition:transform .18s,box-shadow .18s; }
    .ef-btn-dl--blue  { background:var(--blue); }
    .ef-btn-dl--blue:hover { background:var(--navy); color:white; }
    .ef-btn-dl--amber { background:var(--amber); box-shadow:0 4px 20px rgba(245,124,0,.32); }
    .ef-btn-dl--amber:hover { background:#e65100; box-shadow:0 8px 28px rgba(245,124,0,.45); color:white; }

    /* ── VERIFACTU ── */
    .ef-verif { background:linear-gradient(135deg,var(--dark),var(--slate)); padding:72px 5vw; position:relative; overflow:hidden; }
    .ef-verif::before { content:''; position:absolute; top:-100px; right:-100px; width:420px; height:420px; border-radius:50%; background:rgba(245,124,0,.07); pointer-events:none; }
    .ef-verif__inner { max-width:1000px; margin:0 auto; display:grid; grid-template-columns:1fr auto; gap:48px; align-items:center; position:relative; z-index:1; }
    .ef-verif__pill { display:inline-block; background:rgba(245,124,0,.18); border:1px solid rgba(245,124,0,.36); color:var(--amber2); font-size:.75rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase; padding:5px 14px; border-radius:20px; margin-bottom:12px; }
    .ef-verif h2 { font-size:1.85rem; font-weight:800; color:white; margin-bottom:12px; }
    .ef-verif p  { font-size:.98rem; color:rgba(255,255,255,.7); line-height:1.72; margin-bottom:8px; }
    .ef-verif__pts { margin-top:14px; display:flex; flex-direction:column; gap:8px; }
    .ef-verif__pt  { display:flex; align-items:center; gap:9px; font-size:.88rem; color:rgba(255,255,255,.78); }
    .ef-verif__dot { width:7px; height:7px; border-radius:50%; background:var(--amber); flex-shrink:0; }
    .ef-verif__ring { width:110px; height:110px; border-radius:50%; border:3px solid rgba(245,124,0,.3); display:flex; align-items:center; justify-content:center; font-size:2.8rem; background:rgba(245,124,0,.1); margin:0 auto 10px; }
    .ef-verif__badge p { color:var(--amber2); font-weight:700; font-size:.86rem; margin:0; text-align:center; }

    /* ── OFFLINE ── */
    .ef-offline { padding:54px 5vw; background:white; border-top:1px solid #e8edf2; border-bottom:1px solid #e8edf2; }
    .ef-offline__inner { max-width:960px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; gap:28px; flex-wrap:wrap; }
    .ef-offline h3 { font-size:1.35rem; font-weight:800; color:var(--navy); margin-bottom:7px; }
    .ef-offline p  { font-size:.97rem; color:var(--muted); max-width:480px; line-height:1.7; }
    .ef-offline__tags { display:flex; gap:9px; flex-wrap:wrap; margin-top:13px; }
    .ef-offline__tag { display:flex; align-items:center; gap:6px; background:var(--light); border-radius:8px; padding:6px 13px; font-size:.83rem; font-weight:600; color:var(--slate); }

    /* ── FAQ ── */
    .ef-faq { padding:80px 5vw; background:var(--light); }
    .ef-faq__inner { max-width:740px; margin:0 auto; }
    .ef-faq__list  { display:flex; flex-direction:column; gap:11px; margin-top:44px; }
    details.ef-fi  { background:white; border-radius:12px; box-shadow:0 2px 12px rgba(13,22,32,.06); overflow:hidden; }
    details.ef-fi summary { list-style:none; padding:19px 22px; font-weight:700; font-size:.96rem; color:var(--navy); cursor:pointer; display:flex; justify-content:space-between; align-items:center; }
    details.ef-fi summary:hover { color:var(--amber); }
    details.ef-fi summary::after { content:'+'; font-size:1.4rem; font-weight:300; color:var(--amber); flex-shrink:0; margin-left:14px; }
    details.ef-fi[open] summary::after { content:'−'; }
    details.ef-fi[open] { border-left:3px solid var(--amber); }
    details.ef-fi .ef-faq-ans { padding:0 22px 18px; font-size:.93rem; color:var(--muted); line-height:1.72; }

    /* ── MANUAL CTA ── */
    .ef-manual { padding:52px 5vw; background:white; border-bottom:1px solid #e8edf2; }
    .ef-manual__box { max-width:860px; margin:0 auto; background:var(--light); border-radius:18px; padding:36px 36px; display:flex; align-items:center; justify-content:space-between; gap:28px; flex-wrap:wrap; }
    .ef-manual h3 { font-size:1.25rem; font-weight:800; color:var(--navy); margin-bottom:7px; }
    .ef-manual p  { font-size:.93rem; color:var(--muted); max-width:460px; line-height:1.65; }
    .ef-btn-man { display:inline-flex; align-items:center; gap:9px; background:var(--navy); color:white; padding:13px 24px; border-radius:10px; font-weight:700; font-size:.93rem; white-space:nowrap; transition:background .18s; }
    .ef-btn-man:hover { background:var(--dark); color:white; }

    /* ── FINAL CTA ── */
    .ef-final { padding:100px 5vw; background:var(--dark); text-align:center; position:relative; overflow:hidden; }
    .ef-final::before { content:''; position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse 60% 80% at 50% 110%,rgba(245,124,0,.14) 0%,transparent 60%); }
    .ef-final__in { max-width:680px; margin:0 auto; position:relative; z-index:1; }
    .ef-final__logo-wrap { display:flex; align-items:center; gap:12px; justify-content:center; margin-bottom:20px; }
    .ef-final__sym { width:52px; height:52px; }
    .ef-final__wordmark { font-size:2.4rem; font-weight:900; color:white; letter-spacing:-.03em; }
    .ef-final__wordmark em { font-style:normal; color:var(--amber); }
    .ef-final h2 { font-size:clamp(1.9rem,4vw,2.7rem); font-weight:900; color:white; letter-spacing:-.03em; margin-bottom:14px; }
    .ef-final p  { font-size:1.08rem; color:rgba(255,255,255,.68); margin-bottom:32px; line-height:1.75; }
    .ef-final__btns { display:flex; gap:14px; justify-content:center; flex-wrap:wrap; }
    .ef-final__note { margin-top:18px; font-size:.8rem; color:rgba(255,255,255,.38); }
    .ef-final__note a { color:rgba(255,255,255,.58); border-bottom:1px solid rgba(255,255,255,.18); }

    /* ── FOOTER ── */
    .ef-footer { background:#060e18; padding:28px 5vw; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:14px; }
    .ef-footer__brand { display:flex; align-items:center; gap:8px; }
    .ef-footer__sym   { width:22px; height:22px; }
    .ef-footer__name  { color:rgba(255,255,255,.65); font-size:.86rem; font-weight:600; }
    .ef-footer__name span { color:var(--amber); }
    .ef-footer__links { display:flex; gap:18px; flex-wrap:wrap; }
    .ef-footer__links a { color:rgba(255,255,255,.38); font-size:.81rem; transition:color .15s; }
    .ef-footer__links a:hover { color:rgba(255,255,255,.78); }

    /* ── RESPONSIVE ── */
    @media(max-width:900px){
      .ef-hero__inner{grid-template-columns:1fr}
      .ef-hero__visual{display:none}
      .ef-hook__grid,.ef-feat-grid{grid-template-columns:1fr 1fr}
      .ef-ver-grid{grid-template-columns:1fr}
      .ef-verif__inner{grid-template-columns:1fr}
      .ef-verif .ef-verif__badge{display:none}
    }
    @media(max-width:600px){
      .ef-hook__grid,.ef-feat-grid{grid-template-columns:1fr}
      .ef-manual__box{flex-direction:column;align-items:flex-start}
      .ef-nav__links{display:none}
    }
  </style>
</head>
<body class="ef-landing-page">

<!-- NAV -->
<nav class="ef-nav">
  <div class="ef-nav__brand">
    <img src="<?php echo esc_url($logo_symbol); ?>" alt="" class="ef-nav__sym">
    <span class="ef-nav__name">Easy<em>Fix</em></span>
  </div>
  <div class="ef-nav__links">
    <a href="#funcionalidades">Funcionalidades</a>
    <a href="#versiones">Versiones</a>
    <a href="#faq">FAQ</a>
    <a href="<?php echo esc_url(home_url('/productos/easyfix/manual/')); ?>">Manual</a>
    <a href="https://play.google.com/store/apps/details?id=es.easytic.easyfix" target="_blank" rel="noopener" class="ef-nav__dl">Descargar gratis</a>
  </div>
</nav>

<!-- HERO -->
<section class="ef-hero">
  <div class="ef-hero__inner">
    <div>
      <img src="<?php echo esc_url($logo_full); ?>" alt="EasyFix" class="ef-hero__logo">
      <div class="ef-hero__badge"><span class="ef-hero__badge-dot"></span>App Android para talleres mecánicos</div>
      <h1 class="ef-hero__title">Tu taller,<br><em>siempre bajo control</em></h1>
      <p class="ef-hero__sub">Órdenes de trabajo, stock, citas y facturación en una sola app. Sin papel, sin hojas de cálculo, sin complicaciones — y sin necesidad de internet.</p>
      <div class="ef-hero__btns">
        <a class="ef-btn-gp" href="https://play.google.com/store/apps/details?id=es.easytic.easyfix" target="_blank" rel="noopener">
          <span class="ef-btn-gp__icon">▶</span>
          <span><small>Descargar gratis en</small><strong>Google Play</strong></span>
        </a>
        <a class="ef-btn-gp ef-btn-gp--ghost" href="https://play.google.com/store/apps/details?id=es.easytic.easyfix.pro" target="_blank" rel="noopener">
          <span class="ef-btn-gp__icon">⭐</span>
          <span><small>Versión profesional</small><strong>EasyFix Pro</strong></span>
        </a>
      </div>
      <div class="ef-hero__trust">
        <span>✓</span> Funciona sin internet &nbsp;·&nbsp;
        <span>✓</span> Android 6.0+ &nbsp;·&nbsp;
        <span>✓</span> Gratis para siempre
      </div>
    </div>
    <div class="ef-hero__visual">
      <div class="ef-glow"></div>
      <div style="position:relative">
        <div class="ef-phone">
          <div class="ef-phone-notch"></div>
          <div class="ef-phone-screen">
            <div class="ef-ph-hdr">
              <img src="<?php echo esc_url($logo_symbol); ?>" alt="EasyFix" class="ef-ph-hdr-logo">
              <span class="ef-ph-hdr-title">EasyFix</span>
            </div>
            <div class="ef-ph-body">
              <div class="ef-ph-stats">
                <div class="ef-ph-stat"><b>12</b><small>Vehículos</small></div>
                <div class="ef-ph-stat"><b>5</b><small>OT abiertas</small></div>
                <div class="ef-ph-stat"><b>2</b><small>Citas hoy</small></div>
              </div>
              <div style="font-size:.64rem;color:rgba(255,255,255,.35);margin-bottom:5px">ÓRDENES RECIENTES</div>
              <div class="ef-ph-row"><div><div class="ef-ph-row-name">Seat León 2019</div><div class="ef-ph-row-plate">1234·ABC · Cambio aceite</div></div><span class="ef-ph-badge ef-ph-badge--p">En curso</span></div>
              <div class="ef-ph-row"><div><div class="ef-ph-row-name">Volkswagen Golf</div><div class="ef-ph-row-plate">5678·XYZ · Frenos</div></div><span class="ef-ph-badge ef-ph-badge--a">Abierta</span></div>
              <div class="ef-ph-row" style="margin-bottom:0"><div><div class="ef-ph-row-name">Ford Focus</div><div class="ef-ph-row-plate">9012·DEF · Revisión</div></div><span class="ef-ph-badge ef-ph-badge--d">Lista</span></div>
            </div>
          </div>
        </div>
        <div class="ef-phone__float"><span style="font-size:1.2rem">📶</span><div>Sin internet<small>Funciona offline 100%</small></div></div>
      </div>
    </div>
  </div>
</section>

<!-- PROOF BAR -->
<div class="ef-proof">
  <div class="ef-proof__inner">
    <div class="ef-proof-item"><span style="font-size:1.15rem">🤖</span> Desarrollada con <strong>Flutter + IA</strong></div>
    <div class="ef-proof-item"><span style="font-size:1.15rem">🔒</span> Datos <strong>100% en tu dispositivo</strong></div>
    <div class="ef-proof-item"><span style="font-size:1.15rem">⚡</span> Sin cuotas en la <strong>versión gratuita</strong></div>
    <div class="ef-proof-item"><span style="font-size:1.15rem">🇪🇸</span> Hecho en <strong>Huelva, España</strong></div>
  </div>
</div>

<!-- HOOK -->
<section class="ef-hook">
  <div class="ef-hook__inner">
    <span class="ef-chip">¿Te identificas?</span>
    <h2>El taller que trabaja mucho<br>pero gestiona con papel</h2>
    <p class="ef-hook__lead">Órdenes perdidas, stock sin control, facturas tardías, citas olvidadas. EasyFix existe para resolver exactamente eso.</p>
    <div class="ef-hook__grid">
      <div class="ef-hook-card ef-hook-card--bad"><div class="ef-hook-card__icon">😤</div><h4>Sin EasyFix</h4><p>Albaranes en papel, stock de cabeza, no sabes qué tiene abierto cada mecánico y la factura la haces al final del día de memoria.</p></div>
      <div class="ef-hook-card ef-hook-card--free"><div class="ef-hook-card__icon">😌</div><h4>Con EasyFix (gratis)</h4><p>Órdenes en el móvil, stock con alertas, cada mecánico ve sus trabajos, historial de cada vehículo a un tap.</p></div>
      <div class="ef-hook-card ef-hook-card--pro"><div class="ef-hook-card__icon">🚀</div><h4>Con EasyFix Pro</h4><p>Todo lo anterior más presupuestos PDF, facturas automáticas, Verifactu AEAT, sincronización y estadísticas.</p></div>
    </div>
  </div>
</section>

<!-- FEATURES -->
<section class="ef-features" id="funcionalidades">
  <div class="ef-features__inner">
    <div class="ef-sec-head">
      <span class="ef-chip ef-chip--a">Módulos incluidos</span>
      <h2>Todo lo que necesita tu taller, integrado</h2>
      <p>Cinco módulos que cubren el ciclo completo: desde que entra el coche hasta que sale con la factura pagada.</p>
    </div>
    <div class="ef-feat-grid">
      <div class="ef-feat"><div class="ef-feat__head"><div class="ef-feat__icon fi-o">🚗</div><div><div class="ef-feat__ttl">Vehículos y clientes</div><div class="ef-feat__sub">Historial completo</div></div></div><div class="ef-feat__body">Ficha con propietario, matrícula e historial. Consulta cualquier trabajo anterior en segundos.<ul class="ef-feat__ul"><li>Propietario, teléfono, email, NIF</li><li>Historial de reparaciones</li><li>Búsqueda por matrícula</li></ul></div></div>
      <div class="ef-feat"><div class="ef-feat__head"><div class="ef-feat__icon fi-b">📋</div><div><div class="ef-feat__ttl">Órdenes de trabajo</div><div class="ef-feat__sub">Seguimiento en tiempo real</div></div></div><div class="ef-feat__body">Crea, asigna y sigue el estado de cada orden. Tareas, piezas y tiempo por orden.<ul class="ef-feat__ul"><li>Estados: abierta / en curso / lista</li><li>Asignación a mecánicos</li><li>Control de tiempo</li></ul></div></div>
      <div class="ef-feat"><div class="ef-feat__head"><div class="ef-feat__icon fi-t">🔩</div><div><div class="ef-feat__ttl">Stock de piezas</div><div class="ef-feat__sub">Sin roturas inesperadas</div></div></div><div class="ef-feat__body">Inventario con alertas de mínimos. Cada pieza usada se descuenta automáticamente.<ul class="ef-feat__ul"><li>Alertas de stock mínimo</li><li>Descuento automático</li><li>Histórico de consumo</li></ul></div></div>
      <div class="ef-feat"><div class="ef-feat__head"><div class="ef-feat__icon fi-g">📅</div><div><div class="ef-feat__ttl">Agenda de citas</div><div class="ef-feat__sub">Sin solapamientos</div></div></div><div class="ef-feat__body">Calendario semanal con avisos fuera de horario comercial.<ul class="ef-feat__ul"><li>Vista semanal clara</li><li>Horario configurable</li><li>Aviso fuera de horario</li></ul></div></div>
      <div class="ef-feat"><div class="ef-feat__head"><div class="ef-feat__icon fi-p">👥</div><div><div class="ef-feat__ttl">Usuarios y roles</div><div class="ef-feat__sub">Control de acceso</div></div></div><div class="ef-feat__body">Tres roles: administrador, técnico y mecánico. Cada uno accede solo a lo suyo.<ul class="ef-feat__ul"><li>3 roles diferenciados</li><li>Sesión individual</li><li>El primero es siempre admin</li></ul></div></div>
      <div class="ef-feat" style="background:linear-gradient(135deg,#fff8f0,#fff3e0);border:2px solid #ffe0b2"><div class="ef-feat__head"><div class="ef-feat__icon" style="background:rgba(245,124,0,.18)">⭐</div><div><div class="ef-feat__ttl" style="color:var(--amber)">Exclusivo Pro</div><div class="ef-feat__sub">Herramientas avanzadas</div></div></div><div class="ef-feat__body">Presupuestos PDF, facturación, Verifactu, reportes, nube y copias de seguridad.<ul class="ef-feat__ul"><li>Presupuestos y facturas PDF</li><li>Verifactu (AEAT 2027)</li><li>Reportes y estadísticas</li></ul></div></div>
    </div>
  </div>
</section>

<!-- VERSIONS -->
<section class="ef-versions" id="versiones">
  <div class="ef-versions__inner">
    <div class="ef-sec-head">
      <span class="ef-chip">Elige tu versión</span>
      <h2>Empieza gratis. Crece con Pro.</h2>
      <p>La versión gratuita es completa y sin límite de tiempo. Pasa a Pro cuando el taller lo necesite.</p>
    </div>
    <div class="ef-ver-grid">
      <div class="ef-ver-card">
        <div class="ef-ver-head ef-ver-head--free">
          <img src="<?php echo esc_url($logo_full); ?>" alt="EasyFix" class="ef-ver-logo-full">
          <div><div class="ef-ver-name">EasyFix</div><div class="ef-ver-price">Gratis · para siempre</div></div>
        </div>
        <div class="ef-ver-body">
          <ul class="ef-chk-list">
            <li><span class="ef-ck">✓</span> Gestión de vehículos y clientes</li>
            <li><span class="ef-ck">✓</span> Órdenes de trabajo</li>
            <li><span class="ef-ck">✓</span> Control de piezas y stock</li>
            <li><span class="ef-ck">✓</span> Agenda de citas</li>
            <li><span class="ef-ck">✓</span> Gestión de usuarios y roles</li>
            <li class="ef-dim"><span class="ef-cx">–</span> Presupuestos PDF</li>
            <li class="ef-dim"><span class="ef-cx">–</span> Facturación completa</li>
            <li class="ef-dim"><span class="ef-cx">–</span> Verifactu AEAT</li>
            <li class="ef-dim"><span class="ef-cx">–</span> Sincronización en la nube</li>
          </ul>
          <div class="ef-ver-cta"><a class="ef-btn-dl ef-btn-dl--blue" href="https://play.google.com/store/apps/details?id=es.easytic.easyfix" target="_blank" rel="noopener">▶ &nbsp;Descargar en Google Play</a></div>
        </div>
      </div>
      <div class="ef-ver-card ef-ver-card--pro">
        <div class="ef-ver-ribbon">Recomendado</div>
        <div class="ef-ver-head ef-ver-head--pro">
          <img src="<?php echo esc_url($logo_pro); ?>" alt="EasyFix Pro" class="ef-ver-logo-sym">
          <div><div class="ef-ver-name">EasyFix Pro</div><div class="ef-ver-price">Taller profesional</div></div>
        </div>
        <div class="ef-ver-body">
          <ul class="ef-chk-list">
            <li><span class="ef-ck">✓</span> Todo lo de la versión gratuita</li>
            <li><span class="ef-ck">✓</span> <strong>Presupuestos</strong> de reparación en PDF</li>
            <li><span class="ef-ck">✓</span> <strong>Facturación completa</strong> PDF profesional</li>
            <li><span class="ef-ck">✓</span> <strong>Verifactu</strong> — integración nativa AEAT 2027</li>
            <li><span class="ef-ck">✓</span> <strong>Reportes y estadísticas</strong></li>
            <li><span class="ef-ck">✓</span> <strong>Sincronización</strong> entre dispositivos</li>
            <li><span class="ef-ck">✓</span> <strong>Copias de seguridad</strong> completas</li>
            <li><span class="ef-ck">✓</span> <strong>Sin publicidad</strong></li>
          </ul>
          <div class="ef-ver-cta"><a class="ef-btn-dl ef-btn-dl--amber" href="https://play.google.com/store/apps/details?id=es.easytic.easyfix.pro" target="_blank" rel="noopener">⭐ &nbsp;Descargar EasyFix Pro</a></div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- VERIFACTU -->
<section class="ef-verif">
  <div class="ef-verif__inner">
    <div>
      <div class="ef-verif__pill">Obligatorio desde 2027</div>
      <h2>Verifactu ya está integrado</h2>
      <p>La AEAT exigirá Verifactu a todos los negocios. <strong style="color:white">EasyFix Pro ya está preparado</strong> — sin software adicional ni cambios en tu flujo de trabajo.</p>
      <div class="ef-verif__pts">
        <div class="ef-verif__pt"><span class="ef-verif__dot"></span>Hash SHA-256 encadenado por factura, calculado al emitir</div>
        <div class="ef-verif__pt"><span class="ef-verif__dot"></span>QR de verificación incluido en cada PDF de factura</div>
        <div class="ef-verif__pt"><span class="ef-verif__dot"></span>Cola automática de envío con reintentos</div>
        <div class="ef-verif__pt"><span class="ef-verif__dot"></span>Sin conexión: sincroniza en cuanto hay señal</div>
      </div>
    </div>
    <div class="ef-verif__badge"><div class="ef-verif__ring">📊</div><p>Listo para<br>AEAT 2027</p></div>
  </div>
</section>

<!-- OFFLINE -->
<section class="ef-offline">
  <div class="ef-offline__inner">
    <div>
      <h3>Sin internet. Sin excusas.</h3>
      <p>EasyFix guarda todos los datos en el dispositivo. El trabajo diario siempre funciona, aunque no haya cobertura.</p>
      <div class="ef-offline__tags">
        <div class="ef-offline__tag">📱 Android 6.0+</div>
        <div class="ef-offline__tag">💾 Solo 100 MB</div>
        <div class="ef-offline__tag">🔌 Offline 100%</div>
        <div class="ef-offline__tag">🔄 Sync opcional</div>
      </div>
    </div>
    <a class="ef-btn-gp" href="https://play.google.com/store/apps/details?id=es.easytic.easyfix" target="_blank" rel="noopener" style="white-space:nowrap">
      <span class="ef-btn-gp__icon">▶</span><span><small>Gratis en</small><strong>Google Play</strong></span>
    </a>
  </div>
</section>

<!-- FAQ -->
<section class="ef-faq" id="faq">
  <div class="ef-faq__inner">
    <div class="ef-sec-head"><span class="ef-chip">Preguntas frecuentes</span><h2>Resolvemos tus dudas</h2></div>
    <div class="ef-faq__list">
      <details class="ef-fi"><summary>¿EasyFix es realmente gratis?</summary><div class="ef-faq-ans">Sí. La versión gratuita incluye vehículos, órdenes, stock, citas y roles. Sin límite de tiempo, sin tarjeta. La versión Pro añade facturación, Verifactu y nube.</div></details>
      <details class="ef-fi"><summary>¿Funciona sin conexión a internet?</summary><div class="ef-faq-ans">Completamente. Todos los datos se guardan en el dispositivo (SQLite). Solo necesitas red para sincronizar en nube o enviar a Verifactu, y ambas son funciones Pro opcionales.</div></details>
      <details class="ef-fi"><summary>¿Puedo usarlo con varios mecánicos?</summary><div class="ef-faq-ans">Sí. Tres roles: administrador, técnico y mecánico. Cada empleado tiene su sesión y accede solo a lo que le corresponde.</div></details>
      <details class="ef-fi"><summary>¿Qué dispositivos son compatibles?</summary><div class="ef-faq-ans">Cualquier smartphone o tablet Android 6.0 o superior con 100 MB libres. Instalación desde Google Play o APK directo.</div></details>
      <details class="ef-fi"><summary>¿Cómo funciona Verifactu en EasyFix Pro?</summary><div class="ef-faq-ans">Al activarlo, cada factura genera su hash SHA-256 encadenado y queda en cola para la AEAT. El PDF incluye el QR. Sin conexión, los envíos se reintentan automáticamente.</div></details>
      <details class="ef-fi"><summary>¿Puedo migrar mis datos al cambiar de móvil?</summary><div class="ef-faq-ans">Con EasyFix Pro sí: exporta un ZIP completo y restáuralo en el nuevo dispositivo.</div></details>
    </div>
  </div>
</section>

<!-- MANUAL CTA -->
<section class="ef-manual">
  <div class="ef-manual__box">
    <div>
      <h3>📖 Manual de instalación y primeros pasos</h3>
      <p>Guía paso a paso para instalar EasyFix Pro, configurar el taller, crear usuarios y activar Verifactu. Lista en menos de 15 minutos.</p>
    </div>
    <a class="ef-btn-man" href="<?php echo esc_url(home_url('/productos/easyfix/manual/')); ?>">Leer el manual →</a>
  </div>
</section>

<!-- FINAL CTA -->
<section class="ef-final">
  <div class="ef-final__in">
    <div class="ef-final__logo-wrap">
      <img src="<?php echo esc_url($logo_symbol); ?>" alt="" class="ef-final__sym">
      <span class="ef-final__wordmark">Easy<em>Fix</em></span>
    </div>
    <h2>Empieza hoy.<br>Es gratis.</h2>
    <p>Descarga EasyFix y ten tu taller organizado antes de que llegue el próximo coche. Sin registro, sin tarjetas.</p>
    <div class="ef-final__btns">
      <a class="ef-btn-gp" href="https://play.google.com/store/apps/details?id=es.easytic.easyfix" target="_blank" rel="noopener">
        <span class="ef-btn-gp__icon">▶</span><span><small>Descargar gratis en</small><strong>Google Play</strong></span>
      </a>
      <a class="ef-btn-gp ef-btn-gp--ghost" href="https://play.google.com/store/apps/details?id=es.easytic.easyfix.pro" target="_blank" rel="noopener">
        <span class="ef-btn-gp__icon">⭐</span><span><small>Versión profesional</small><strong>EasyFix Pro</strong></span>
      </a>
    </div>
    <p class="ef-final__note">¿Tienes dudas? <a href="<?php echo esc_url(home_url('/productos/easyfix/manual/')); ?>">Lee el manual de instalación</a></p>
  </div>
</section>

<!-- FOOTER -->
<footer class="ef-footer">
  <div class="ef-footer__brand">
    <img src="<?php echo esc_url($logo_symbol); ?>" alt="EasyFix" class="ef-footer__sym">
    <span class="ef-footer__name">Easy<span>Fix</span> — by EasyTic</span>
  </div>
  <div class="ef-footer__links">
    <a href="<?php echo esc_url(home_url('/productos/easyfix/manual/')); ?>">Manual</a>
    <a href="<?php echo esc_url(home_url('/productos/')); ?>">Más productos</a>
    <a href="<?php echo esc_url(home_url('/contacto/')); ?>">Contacto</a>
    <a href="<?php echo esc_url(home_url('/politica-de-privacidad-2/')); ?>">Privacidad</a>
  </div>
</footer>

<?php wp_footer(); /* Mantiene Google Analytics, scripts de plugins, etc. */ ?>
</body>
</html>
