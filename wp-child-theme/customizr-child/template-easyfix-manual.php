<?php
/**
 * Template Name: EasyFix Manual
 *
 * Página de manual/funciones de EasyFix. Autocontenida, sin header/footer del tema.
 */

add_action( 'wp_print_styles', function () {
    global $wp_styles;
    $wp_styles->queue = [];
}, 999 );
add_action( 'wp_print_scripts', function () {
    global $wp_scripts;
    $wp_scripts->queue = [];
}, 999 );

$logo_full   = get_stylesheet_directory_uri() . '/assets/easyfix-logo.png';
$logo_symbol = get_stylesheet_directory_uri() . '/assets/easyfix-symbol.png';
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Manual de funciones — EasyFix · Gestión de taller mecánico</title>
  <meta name="description" content="Descubre todo lo que puedes hacer con EasyFix: vehículos, órdenes de trabajo, piezas, presupuestos, facturas, agenda y mucho más.">
  <?php wp_head(); ?>
  <style>
    html { margin-top: 0 !important; overflow-y: auto !important; height: auto !important; }
    body { overflow-y: visible !important; height: auto !important; }
    #wpadminbar { display: none !important; }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --amber:  #f57c00;
      --amber2: #ff9800;
      --dark:   #0d1620;
      --navy:   #1a2744;
      --slate:  #37474f;
      --blue:   #1565c0;
      --muted:  #546e7a;
      --light:  #f5f7fa;
      --green:  #388e3c;
    }
    html { scroll-behavior: smooth; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: var(--navy); background: #fff; line-height: 1.6;
    }
    a { text-decoration: none; }

    /* ── NAV ── */
    .ef-nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 200;
      background: rgba(13,22,32,.96); backdrop-filter: blur(14px);
      border-bottom: 1px solid rgba(255,255,255,.07);
      height: 64px; display: flex; align-items: center; justify-content: space-between;
      padding: 0 5vw;
    }
    .ef-nav__brand { display: flex; align-items: center; gap: 10px; }
    .ef-nav__sym   { width: 34px; height: 34px; }
    .ef-nav__name  { font-size: 1.15rem; font-weight: 900; letter-spacing: -.02em; color: white; }
    .ef-nav__name em { font-style: normal; color: var(--amber); }
    .ef-nav__links { display: flex; gap: 24px; align-items: center; }
    .ef-nav__links a { color: rgba(255,255,255,.68); font-size: .88rem; font-weight: 500; transition: color .15s; }
    .ef-nav__links a:hover { color: white; }
    .ef-nav__back { color: rgba(255,255,255,.55) !important; font-size: .82rem !important; }
    .ef-nav__dl {
      background: var(--amber); color: white !important; font-weight: 700 !important;
      padding: 9px 22px; border-radius: 8px; transition: background .15s !important;
    }
    .ef-nav__dl:hover { background: #e65100 !important; }

    /* ── HERO ── */
    .ef-hero {
      background: var(--dark); padding: 120px 5vw 72px;
      position: relative;
    }
    .ef-hero::before {
      content: ''; position: absolute; inset: 0; pointer-events: none;
      background:
        radial-gradient(ellipse 55% 70% at 90% 50%, rgba(245,124,0,.13) 0%, transparent 60%),
        radial-gradient(ellipse 40% 50% at 5% 80%, rgba(21,101,192,.09) 0%, transparent 55%);
    }
    .ef-hero__inner {
      max-width: 760px; margin: 0 auto; text-align: center;
      position: relative; z-index: 1;
    }
    .ef-hero__logo { width: 160px; margin: 0 auto 24px; display: block; filter: drop-shadow(0 0 12px rgba(245,124,0,.35)); }
    .ef-hero h1 {
      font-size: clamp(1.9rem, 4vw, 2.8rem); font-weight: 900; color: white;
      letter-spacing: -.03em; margin-bottom: 16px;
    }
    .ef-hero h1 em { font-style: normal; color: var(--amber2); }
    .ef-hero p {
      font-size: 1.1rem; color: rgba(255,255,255,.68); max-width: 560px; margin: 0 auto 32px;
    }
    .ef-hero__nav {
      display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;
    }
    .ef-hero__nav a {
      background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.15);
      color: rgba(255,255,255,.75); font-size: .83rem; font-weight: 600;
      padding: 8px 18px; border-radius: 20px; transition: all .15s;
    }
    .ef-hero__nav a:hover { background: rgba(255,255,255,.15); color: white; }

    /* ── MÓDULOS ── */
    .ef-modules { padding: 80px 5vw; }
    .ef-modules__inner { max-width: 1100px; margin: 0 auto; }
    .ef-section-title {
      text-align: center; margin-bottom: 48px;
    }
    .ef-section-title h2 {
      font-size: clamp(1.5rem, 2.8vw, 2rem); font-weight: 800; color: var(--navy); margin-bottom: 8px;
    }
    .ef-section-title p { color: var(--muted); font-size: .95rem; }

    .ef-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 24px; margin-bottom: 72px;
    }
    .ef-card {
      border: 1px solid #e4eaf0; border-radius: 16px; overflow: hidden;
      transition: box-shadow .2s, transform .2s;
    }
    .ef-card:hover { box-shadow: 0 8px 32px rgba(13,22,32,.1); transform: translateY(-2px); }
    .ef-card__head {
      padding: 20px 22px 14px; display: flex; align-items: flex-start; gap: 14px;
      border-bottom: 1px solid #f0f4f8;
    }
    .ef-card__icon {
      width: 44px; height: 44px; border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem; flex-shrink: 0;
    }
    .ef-card__icon--amber  { background: rgba(245,124,0,.1); }
    .ef-card__icon--blue   { background: rgba(21,101,192,.1); }
    .ef-card__icon--green  { background: rgba(56,142,60,.1); }
    .ef-card__icon--slate  { background: rgba(55,71,79,.08); }
    .ef-card__icon--purple { background: rgba(103,58,183,.1); }
    .ef-card__title { font-size: 1rem; font-weight: 800; color: var(--navy); margin-bottom: 3px; }
    .ef-card__sub   { font-size: .78rem; color: var(--muted); }
    .ef-card__body  { padding: 16px 22px 20px; }
    .ef-card__list  { list-style: none; }
    .ef-card__list li {
      font-size: .875rem; color: var(--slate); padding: 5px 0;
      border-bottom: 1px solid #f4f6f8; display: flex; gap: 8px; align-items: flex-start;
    }
    .ef-card__list li:last-child { border-bottom: none; }
    .ef-card__list li::before { content: '·'; color: var(--amber); font-weight: 900; flex-shrink: 0; margin-top: 1px; }
    .ef-badge-pro {
      display: inline-block; background: var(--amber); color: white;
      font-size: .65rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase;
      padding: 2px 8px; border-radius: 10px; margin-left: 6px; vertical-align: middle;
    }

    /* ── COMPARATIVA ── */
    .ef-compare { background: var(--light); padding: 80px 5vw; }
    .ef-compare__inner { max-width: 860px; margin: 0 auto; }
    .ef-compare h2 {
      text-align: center; font-size: clamp(1.5rem, 2.8vw, 2rem); font-weight: 800;
      color: var(--navy); margin-bottom: 40px;
    }
    .ef-compare-table {
      width: 100%; border-collapse: collapse; border-radius: 16px; overflow: hidden;
      box-shadow: 0 4px 24px rgba(13,22,32,.08);
    }
    .ef-compare-table thead th {
      padding: 18px 20px; font-size: .9rem; font-weight: 800; text-align: center;
    }
    .ef-compare-table thead th:first-child { text-align: left; background: white; }
    .ef-compare-table thead .col-free { background: #e8f0fe; color: var(--blue); }
    .ef-compare-table thead .col-pro  { background: var(--amber); color: white; }
    .ef-compare-table tbody tr { border-top: 1px solid #e8edf2; }
    .ef-compare-table tbody tr:nth-child(even) td { background: #fafbfc; }
    .ef-compare-table tbody td {
      padding: 13px 20px; font-size: .875rem; color: var(--slate);
      text-align: center; background: white;
    }
    .ef-compare-table tbody td:first-child { text-align: left; color: var(--navy); font-weight: 500; }
    .ef-compare-table .ok  { color: #388e3c; font-size: 1.1rem; }
    .ef-compare-table .no  { color: #bdbdbd; font-size: 1.1rem; }
    .ef-compare-table .val { font-weight: 700; color: var(--navy); }

    /* ── CTA ── */
    .ef-cta {
      background: var(--dark); padding: 80px 5vw; text-align: center; position: relative;
    }
    .ef-cta::before {
      content: ''; position: absolute; inset: 0; pointer-events: none;
      background: radial-gradient(ellipse 60% 80% at 50% 50%, rgba(245,124,0,.12) 0%, transparent 65%);
    }
    .ef-cta__inner { max-width: 600px; margin: 0 auto; position: relative; z-index: 1; }
    .ef-cta h2 { font-size: clamp(1.6rem, 3vw, 2.2rem); font-weight: 900; color: white; margin-bottom: 14px; }
    .ef-cta p  { color: rgba(255,255,255,.65); margin-bottom: 32px; font-size: 1rem; }
    .ef-cta__btns { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
    .ef-btn {
      display: inline-flex; align-items: center; gap: 10px;
      padding: 13px 28px; border-radius: 12px; font-weight: 700; font-size: .95rem;
      transition: transform .18s, box-shadow .18s;
    }
    .ef-btn:hover { transform: translateY(-2px); }
    .ef-btn--amber { background: var(--amber); color: white; box-shadow: 0 4px 18px rgba(245,124,0,.38); }
    .ef-btn--amber:hover { background: #e65100; color: white; box-shadow: 0 8px 28px rgba(245,124,0,.5); }
    .ef-btn--ghost { background: rgba(255,255,255,.08); border: 1.5px solid rgba(255,255,255,.22); color: rgba(255,255,255,.85); }
    .ef-btn--ghost:hover { background: rgba(255,255,255,.15); color: white; }

    /* ── FOOTER ── */
    .ef-footer {
      background: #060d14; padding: 28px 5vw;
      display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
    }
    .ef-footer a { color: rgba(255,255,255,.4); font-size: .8rem; }
    .ef-footer a:hover { color: rgba(255,255,255,.75); }
    .ef-footer__copy { font-size: .8rem; color: rgba(255,255,255,.3); }

    /* ── RESPONSIVE ── */
    @media (max-width: 700px) {
      .ef-nav__links { display: none; }
      .ef-grid { grid-template-columns: 1fr; }
      .ef-compare-table thead th, .ef-compare-table tbody td { padding: 10px 12px; font-size: .8rem; }
    }
  </style>
</head>
<body>

<!-- NAV -->
<nav class="ef-nav">
  <a class="ef-nav__brand" href="<?php echo esc_url( home_url('/productos/easyfix/') ); ?>">
    <img class="ef-nav__sym" src="<?php echo esc_url($logo_symbol); ?>" alt="EasyFix">
    <span class="ef-nav__name">Easy<em>Fix</em></span>
  </a>
  <div class="ef-nav__links">
    <a class="ef-nav__back" href="<?php echo esc_url( home_url('/productos/easyfix/') ); ?>">← Volver a EasyFix</a>
    <a href="https://play.google.com/store/apps/details?id=es.easytic.easyfix" target="_blank" rel="noopener" class="ef-nav__dl">Descargar gratis</a>
  </div>
</nav>

<!-- HERO -->
<section class="ef-hero">
  <div class="ef-hero__inner">
    <img class="ef-hero__logo" src="<?php echo esc_url($logo_full); ?>" alt="EasyFix">
    <h1>Todo lo que puedes hacer con <em>EasyFix</em></h1>
    <p>Una app completa para gestionar tu taller mecánico desde el móvil. Aquí tienes un resumen de cada módulo.</p>
    <nav class="ef-hero__nav">
      <a href="#vehiculos">Vehículos</a>
      <a href="#ordenes">Órdenes</a>
      <a href="#piezas">Piezas</a>
      <a href="#pro">Funciones Pro</a>
      <a href="#comparativa">Free vs Pro</a>
    </nav>
  </div>
</section>

<!-- MÓDULOS BASE -->
<section class="ef-modules" id="vehiculos">
  <div class="ef-modules__inner">

    <div class="ef-section-title">
      <h2>Funciones disponibles en la versión gratuita</h2>
      <p>Todo lo esencial para gestionar el día a día del taller.</p>
    </div>

    <div class="ef-grid">

      <!-- Vehículos -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--amber">🚗</div>
          <div>
            <div class="ef-card__title">Vehículos</div>
            <div class="ef-card__sub">Registro completo del parque móvil</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Ficha con matrícula, marca, modelo, año y kilómetros</li>
            <li>Datos del propietario: nombre, teléfono, email y NIF/CIF</li>
            <li>Búsqueda en tiempo real por matrícula</li>
            <li>Historial de órdenes de trabajo por vehículo</li>
            <li>Sin duplicados — la app detecta matrículas repetidas</li>
          </ul>
        </div>
      </div>

      <!-- Clientes -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--blue">👥</div>
          <div>
            <div class="ef-card__title">Clientes</div>
            <div class="ef-card__sub">Vista automática por propietario</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Se generan solos al registrar vehículos — sin trabajo extra</li>
            <li>Agrupación por propietario con todos sus vehículos</li>
            <li>Búsqueda por nombre, teléfono o email</li>
            <li>Ficha con historial completo de intervenciones</li>
          </ul>
        </div>
      </div>

      <!-- Órdenes de trabajo -->
      <div class="ef-card" id="ordenes">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--amber">📋</div>
          <div>
            <div class="ef-card__title">Órdenes de trabajo</div>
            <div class="ef-card__sub">El núcleo de la gestión del taller</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Estados: Abierta · En progreso · Completada · Cancelada</li>
            <li>Prioridades: Baja · Media · Alta · Urgente</li>
            <li>Filtrado por estado con un toque</li>
            <li>Observaciones del cliente en cada orden</li>
            <li>Vínculo directo al vehículo y propietario</li>
          </ul>
        </div>
      </div>

      <!-- Tareas y tiempo -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--green">⏱️</div>
          <div>
            <div class="ef-card__title">Tareas y control de tiempo</div>
            <div class="ef-card__sub">Detalle de cada trabajo realizado</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Varias tareas por orden, cada una con su técnico</li>
            <li>Cronómetro integrado: inicia, pausa y para cuando quieras</li>
            <li>El tiempo se acumula entre sesiones automáticamente</li>
            <li>Piezas utilizadas por tarea con cantidad y descuento</li>
            <li>Estados: Pendiente · En progreso · Completada · Cancelada</li>
          </ul>
        </div>
      </div>

      <!-- Piezas -->
      <div class="ef-card" id="piezas">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--slate">🔧</div>
          <div>
            <div class="ef-card__title">Catálogo de piezas</div>
            <div class="ef-card__sub">Stock y repuestos siempre a mano</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Ficha con nombre, código, precio y stock disponible</li>
            <li>Filtro por categoría: Filtros, Aceites, Frenos, etc.</li>
            <li>Búsqueda por nombre o código de referencia</li>
            <li>El stock se descuenta al usar piezas en una tarea</li>
            <li>Historial de uso de cada pieza en órdenes</li>
          </ul>
        </div>
      </div>

      <!-- Notificaciones -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--blue">🔔</div>
          <div>
            <div class="ef-card__title">Notificaciones</div>
            <div class="ef-card__sub">Sin olvidarte de nada importante</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Avisos de cambios de estado en órdenes de trabajo</li>
            <li>Alertas de vencimiento de facturas</li>
            <li>Recordatorios programables</li>
            <li>Filtrado por tipo: Órdenes, Facturas, Recordatorios</li>
            <li>Contador de no leídas visible en el menú</li>
          </ul>
        </div>
      </div>

    </div><!-- /grid base -->

    <!-- PRO -->
    <div class="ef-section-title" id="pro">
      <h2>Funciones exclusivas de <span style="color:var(--amber)">EasyFix Pro</span></h2>
      <p>Sin límites, sin anuncios y con todas las herramientas de gestión avanzada.</p>
    </div>

    <div class="ef-grid">

      <!-- Presupuestos -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--amber">📄</div>
          <div>
            <div class="ef-card__title">Presupuestos <span class="ef-badge-pro">Pro</span></div>
            <div class="ef-card__sub">Ofrece precio antes de empezar</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Líneas de mano de obra y piezas con descuento por línea</li>
            <li>IVA configurable y cálculo automático de totales</li>
            <li>PDF del presupuesto para compartir con el cliente</li>
            <li>Estados: Borrador · Enviado · Aceptado · Rechazado</li>
            <li>Conversión en orden de trabajo con un solo botón</li>
          </ul>
        </div>
      </div>

      <!-- Facturas -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--green">🧾</div>
          <div>
            <div class="ef-card__title">Facturas PDF <span class="ef-badge-pro">Pro</span></div>
            <div class="ef-card__sub">Facturación desde el propio taller</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Generación de factura desde cualquier orden completada</li>
            <li>PDF con datos del taller, cliente, desglose y totales</li>
            <li>QR y bloque legal para cumplimiento Verifactu (AEAT 2027)</li>
            <li>Numeración automática correlativa</li>
            <li>Compartir por WhatsApp, email o imprimir directamente</li>
          </ul>
        </div>
      </div>

      <!-- Agenda -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--blue">📅</div>
          <div>
            <div class="ef-card__title">Agenda y citas <span class="ef-badge-pro">Pro</span></div>
            <div class="ef-card__sub">Planifica la semana del taller</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Citas con hora, vehículo, técnico y tipo de trabajo</li>
            <li>Aviso si la cita cae fuera del horario comercial</li>
            <li>PDF del planning semanal para imprimir o compartir</li>
            <li>Horario comercial personalizable en Ajustes</li>
          </ul>
        </div>
      </div>

      <!-- Reportes -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--purple">📊</div>
          <div>
            <div class="ef-card__title">Reportes <span class="ef-badge-pro">Pro</span></div>
            <div class="ef-card__sub">Conoce el rendimiento de tu negocio</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Ingresos por período con comparativa mensual</li>
            <li>Piezas más utilizadas y rotación de stock</li>
            <li>Rendimiento por técnico: horas y órdenes completadas</li>
            <li>Exportación a PDF para compartir o archivar</li>
          </ul>
        </div>
      </div>

      <!-- Backup -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--slate">☁️</div>
          <div>
            <div class="ef-card__title">Copia de seguridad y sincronización <span class="ef-badge-pro">Pro</span></div>
            <div class="ef-card__sub">Tus datos siempre a salvo</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Copia de seguridad automática y manual en ZIP</li>
            <li>Sincronización en la nube entre dispositivos</li>
            <li>Restauración desde copia de seguridad anterior</li>
          </ul>
        </div>
      </div>

      <!-- Usuarios -->
      <div class="ef-card">
        <div class="ef-card__head">
          <div class="ef-card__icon ef-card__icon--green">👤</div>
          <div>
            <div class="ef-card__title">Gestión de usuarios <span class="ef-badge-pro">Pro</span></div>
            <div class="ef-card__sub">Control de acceso por rol</div>
          </div>
        </div>
        <div class="ef-card__body">
          <ul class="ef-card__list">
            <li>Roles: Administrador · Técnico · Mecánico</li>
            <li>Cada rol ve solo lo que necesita</li>
            <li>Asignación de órdenes a técnicos específicos</li>
            <li>El primer registro es siempre Administrador</li>
          </ul>
        </div>
      </div>

    </div><!-- /grid pro -->
  </div>
</section>

<!-- COMPARATIVA FREE vs PRO -->
<section class="ef-compare" id="comparativa">
  <div class="ef-compare__inner">
    <h2>Free vs Pro — de un vistazo</h2>
    <table class="ef-compare-table">
      <thead>
        <tr>
          <th></th>
          <th class="col-free">EasyFix Free</th>
          <th class="col-pro">EasyFix Pro</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Vehículos</td>                       <td class="val">Hasta 3</td>           <td class="val">Ilimitados</td></tr>
        <tr><td>Órdenes de trabajo activas</td>      <td class="val">Hasta 5</td>           <td class="val">Ilimitadas</td></tr>
        <tr><td>Piezas en catálogo</td>              <td class="val">Hasta 10</td>          <td class="val">Ilimitadas</td></tr>
        <tr><td>Tareas y control de tiempo</td>      <td class="ok">✓</td>                  <td class="ok">✓</td></tr>
        <tr><td>Clientes y vehículos</td>            <td class="ok">✓</td>                  <td class="ok">✓</td></tr>
        <tr><td>Notificaciones</td>                  <td class="ok">✓</td>                  <td class="ok">✓</td></tr>
        <tr><td>Presupuestos de reparación</td>      <td class="no">—</td>                  <td class="ok">✓</td></tr>
        <tr><td>Facturas PDF + Verifactu</td>        <td class="no">—</td>                  <td class="ok">✓</td></tr>
        <tr><td>Agenda y citas</td>                  <td class="no">—</td>                  <td class="ok">✓</td></tr>
        <tr><td>Reportes y estadísticas</td>         <td class="no">—</td>                  <td class="ok">✓</td></tr>
        <tr><td>Copia de seguridad</td>              <td class="no">—</td>                  <td class="ok">✓</td></tr>
        <tr><td>Sincronización en la nube</td>       <td class="no">—</td>                  <td class="ok">✓</td></tr>
        <tr><td>Asignación de órdenes a usuarios</td><td class="no">—</td>                  <td class="ok">✓</td></tr>
        <tr><td>Publicidad</td>                      <td>Sí</td>                            <td class="ok">Sin anuncios</td></tr>
      </tbody>
    </table>
  </div>
</section>

<!-- CTA -->
<section class="ef-cta">
  <div class="ef-cta__inner">
    <h2>Empieza gratis hoy mismo</h2>
    <p>Descarga EasyFix sin coste, sin registro previo y sin tarjeta bancaria.</p>
    <div class="ef-cta__btns">
      <a class="ef-btn ef-btn--amber"
         href="https://play.google.com/store/apps/details?id=es.easytic.easyfix"
         target="_blank" rel="noopener">
        ▶ Descargar en Google Play
      </a>
      <a class="ef-btn ef-btn--ghost"
         href="<?php echo esc_url( home_url('/productos/easyfix/') ); ?>">
        ← Volver a EasyFix
      </a>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer class="ef-footer">
  <a href="<?php echo esc_url( home_url('/') ); ?>">easytic.es</a>
  <span class="ef-footer__copy">© <?php echo date('Y'); ?> EasyTic · EasyFix</span>
</footer>

<?php wp_footer(); ?>
</body>
</html>
