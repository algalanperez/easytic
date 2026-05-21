<?php
/**
 * Template Name: EasyFix Privacidad
 *
 * Política de privacidad de EasyFix. Autocontenida, sin header/footer del tema.
 */

add_action( 'wp_print_styles', function () {
    global $wp_styles;
    $wp_styles->queue = [];
}, 999 );
add_action( 'wp_print_scripts', function () {
    global $wp_scripts;
    $wp_scripts->queue = [];
}, 999 );

$logo_symbol = get_stylesheet_directory_uri() . '/assets/easyfix-symbol.png';
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Política de Privacidad — EasyFix</title>
  <meta name="description" content="Política de privacidad de la aplicación EasyFix para gestión de talleres mecánicos.">
  <meta name="robots" content="noindex">
  <?php wp_head(); ?>
  <style>
    html { margin-top: 0 !important; overflow-y: auto !important; height: auto !important; }
    body { overflow-y: visible !important; height: auto !important; }
    #wpadminbar { display: none !important; }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --amber: #f57c00;
      --dark:  #0d1620;
      --navy:  #1a2744;
      --muted: #546e7a;
      --light: #f5f7fa;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: var(--navy); background: #fff; line-height: 1.7;
    }
    a { color: var(--amber); text-decoration: none; }
    a:hover { text-decoration: underline; }

    /* NAV */
    .ef-nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 200;
      background: rgba(13,22,32,.96); backdrop-filter: blur(14px);
      border-bottom: 1px solid rgba(255,255,255,.07);
      height: 64px; display: flex; align-items: center; justify-content: space-between;
      padding: 0 5vw;
    }
    .ef-nav__brand { display: flex; align-items: center; gap: 10px; }
    .ef-nav__sym   { width: 34px; height: 34px; }
    .ef-nav__name  { font-size: 1.1rem; font-weight: 900; color: white; letter-spacing: -.02em; }
    .ef-nav__name em { font-style: normal; color: var(--amber); }
    .ef-nav__back  { color: rgba(255,255,255,.55); font-size: .85rem; }
    .ef-nav__back:hover { color: white; text-decoration: none; }

    /* CONTENIDO */
    .ef-legal {
      max-width: 780px; margin: 0 auto;
      padding: 104px 5vw 80px;
    }
    .ef-legal__header { margin-bottom: 48px; padding-bottom: 24px; border-bottom: 2px solid #f0f4f8; }
    .ef-legal__header h1 {
      font-size: clamp(1.6rem, 3vw, 2.2rem); font-weight: 900;
      color: var(--navy); margin-bottom: 8px;
    }
    .ef-legal__date { font-size: .85rem; color: var(--muted); }

    .ef-legal h2 {
      font-size: 1.1rem; font-weight: 800; color: var(--navy);
      margin: 40px 0 12px; padding-bottom: 6px;
      border-bottom: 1px solid #e8edf2;
    }
    .ef-legal h3 {
      font-size: .95rem; font-weight: 700; color: var(--navy);
      margin: 24px 0 8px;
    }
    .ef-legal p  { margin-bottom: 14px; font-size: .95rem; color: #374151; }
    .ef-legal ul { margin: 0 0 14px 20px; }
    .ef-legal ul li { font-size: .95rem; color: #374151; margin-bottom: 6px; }

    /* Tablas */
    .ef-legal table {
      width: 100%; border-collapse: collapse; margin: 16px 0 24px;
      font-size: .875rem;
    }
    .ef-legal table th, .ef-legal table td {
      padding: 10px 14px; text-align: left;
      border: 1px solid #e4eaf0;
    }
    .ef-legal table th { background: var(--light); font-weight: 700; color: var(--navy); }
    .ef-legal table td { color: #374151; }

    /* FOOTER */
    .ef-footer {
      background: #060d14; padding: 24px 5vw;
      display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
    }
    .ef-footer a { color: rgba(255,255,255,.4); font-size: .8rem; }
    .ef-footer a:hover { color: rgba(255,255,255,.75); text-decoration: none; }
    .ef-footer__copy { font-size: .8rem; color: rgba(255,255,255,.3); }

    @media (max-width: 600px) {
      .ef-nav__back span { display: none; }
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
  <a class="ef-nav__back" href="<?php echo esc_url( home_url('/productos/easyfix/') ); ?>">
    ← <span>Volver a EasyFix</span>
  </a>
</nav>

<!-- CONTENIDO -->
<main class="ef-legal">

  <div class="ef-legal__header">
    <h1>Política de Privacidad</h1>
    <p class="ef-legal__date">Última actualización: mayo de 2026</p>
  </div>

  <h2>1. Responsable del tratamiento</h2>
  <table>
    <tr><th>Empresa</th><td>EasyTic</td></tr>
    <tr><th>Correo electrónico</th><td><a href="mailto:info@easytic.es">info@easytic.es</a></td></tr>
    <tr><th>Sitio web</th><td><a href="https://easytic.es">easytic.es</a></td></tr>
  </table>

  <h2>2. Qué es EasyFix</h2>
  <p>EasyFix es una aplicación Android para la gestión de talleres mecánicos. Permite registrar vehículos, clientes, órdenes de trabajo, piezas, presupuestos y facturas. Está disponible en dos versiones:</p>
  <ul>
    <li><strong>EasyFix</strong> (versión gratuita): funciones básicas con publicidad.</li>
    <li><strong>EasyFix Pro</strong> (versión de pago): funciones completas sin publicidad.</li>
  </ul>

  <h2>3. Datos que tratamos</h2>

  <h3>3.1 Datos que introduce el usuario</h3>
  <p>La app almacena los datos que el propio usuario introduce para gestionar su taller:</p>
  <table>
    <thead><tr><th>Categoría</th><th>Ejemplos</th></tr></thead>
    <tbody>
      <tr><td>Datos de vehículos</td><td>Matrícula, marca, modelo, año, kilómetros</td></tr>
      <tr><td>Datos de clientes</td><td>Nombre, teléfono, correo electrónico, NIF/CIF</td></tr>
      <tr><td>Gestión del taller</td><td>Órdenes de trabajo, tareas, piezas, presupuestos, facturas</td></tr>
      <tr><td>Usuarios de la app</td><td>Nombre, nombre de usuario, email, contraseña cifrada</td></tr>
    </tbody>
  </table>
  <p>Estos datos son introducidos voluntariamente por el usuario y corresponden a la información de sus propios clientes y operaciones de taller. EasyTic no accede a estos datos ni los utiliza con ningún otro fin.</p>

  <h3>3.2 Almacenamiento local</h3>
  <p>Todos los datos se almacenan en la base de datos local del dispositivo (SQLite). No se transmiten a servidores externos salvo en los casos descritos a continuación.</p>

  <h3>3.3 Sincronización en la nube (solo EasyFix Pro)</h3>
  <p>La versión Pro ofrece sincronización en la nube mediante <strong>Firebase Firestore</strong> (Google LLC). Los datos del taller se sincronizan cifrados con los servidores de Google para permitir el acceso desde múltiples dispositivos y la copia de seguridad automática.</p>
  <p>Google actúa como encargado del tratamiento bajo los Términos de Servicio de Firebase y el Acuerdo de Procesamiento de Datos de Google Cloud. Más información: <a href="https://firebase.google.com/support/privacy" target="_blank" rel="noopener">firebase.google.com/support/privacy</a>.</p>

  <h3>3.4 Publicidad (solo EasyFix versión gratuita)</h3>
  <p>La versión gratuita muestra anuncios mediante <strong>Google AdMob</strong> (Google LLC). AdMob puede recopilar un identificador publicitario del dispositivo para mostrar anuncios personalizados según la configuración del usuario.</p>
  <p>Puedes desactivar los anuncios personalizados desde los ajustes de tu dispositivo Android: <em>Ajustes → Google → Anuncios → Inhabilitar personalización de anuncios</em>.</p>
  <p>Más información: <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">policies.google.com/privacy</a>.</p>

  <h3>3.5 Acceso a la galería de imágenes</h3>
  <p>La app solicita permiso para acceder a las imágenes del dispositivo únicamente cuando el usuario elige adjuntar una imagen. Este acceso es puntual y voluntario; las imágenes seleccionadas se almacenan localmente en el dispositivo.</p>

  <h2>4. Finalidad y base legal del tratamiento</h2>
  <table>
    <thead><tr><th>Finalidad</th><th>Base legal</th></tr></thead>
    <tbody>
      <tr><td>Gestión de los datos del taller</td><td>Ejecución del contrato / interés legítimo del usuario</td></tr>
      <tr><td>Sincronización en la nube (Pro)</td><td>Consentimiento del usuario al activar la función</td></tr>
      <tr><td>Publicidad personalizada (Free)</td><td>Consentimiento del usuario (configurable en el dispositivo)</td></tr>
    </tbody>
  </table>

  <h2>5. Conservación de los datos</h2>
  <p>Los datos se conservan en el dispositivo del usuario mientras la app esté instalada. El usuario puede eliminarlos en cualquier momento desinstalando la aplicación o usando las funciones de eliminación disponibles en la propia app.</p>
  <p>Los datos sincronizados con Firebase (EasyFix Pro) se eliminan de los servidores de Google al solicitar la supresión de datos a través de <a href="mailto:info@easytic.es">info@easytic.es</a>.</p>

  <h2>6. Comunicación de datos a terceros</h2>
  <p>EasyTic <strong>no vende, alquila ni cede</strong> los datos de los usuarios a terceros con fines comerciales. Los únicos terceros con acceso a datos son Google Firebase y Google AdMob, que actúan como encargados del tratamiento bajo contrato.</p>

  <h2>7. Transferencias internacionales</h2>
  <p>Google LLC, proveedor de Firebase y AdMob, tiene su sede en Estados Unidos. Las transferencias de datos se realizan bajo las garantías establecidas por las Cláusulas Contractuales Tipo aprobadas por la Comisión Europea y el Marco de Privacidad de Datos UE-EE.UU.</p>

  <h2>8. Derechos del usuario</h2>
  <p>De conformidad con el RGPD y la Ley Orgánica 3/2018 (LOPDGDD), el usuario tiene derecho a:</p>
  <ul>
    <li><strong>Acceso</strong>: conocer qué datos se tratan.</li>
    <li><strong>Rectificación</strong>: corregir datos inexactos.</li>
    <li><strong>Supresión</strong>: solicitar la eliminación de sus datos.</li>
    <li><strong>Limitación del tratamiento</strong>: solicitar que se restrinja su uso.</li>
    <li><strong>Portabilidad</strong>: recibir sus datos en formato legible.</li>
    <li><strong>Oposición</strong>: oponerse a determinados tratamientos.</li>
  </ul>
  <p>Para ejercer cualquiera de estos derechos, escríbenos a <a href="mailto:info@easytic.es">info@easytic.es</a>. Si consideras que el tratamiento no es conforme a la normativa, puedes reclamar ante la <a href="https://www.aepd.es" target="_blank" rel="noopener">Agencia Española de Protección de Datos</a>.</p>

  <h2>9. Seguridad</h2>
  <p>Las contraseñas se almacenan cifradas mediante hash SHA-256 con sal; nunca en texto plano. La sincronización con Firebase se realiza mediante conexiones cifradas (TLS).</p>

  <h2>10. Cambios en esta política</h2>
  <p>EasyTic se reserva el derecho a actualizar esta política para adaptarla a cambios legales o funcionales de la aplicación. En caso de cambios relevantes, se notificará a los usuarios mediante la propia app.</p>

  <h2>11. Contacto</h2>
  <p><strong>EasyTic</strong> · <a href="mailto:info@easytic.es">info@easytic.es</a> · <a href="https://easytic.es">easytic.es</a></p>

</main>

<!-- FOOTER -->
<footer class="ef-footer">
  <a href="<?php echo esc_url( home_url('/') ); ?>">easytic.es</a>
  <span class="ef-footer__copy">© <?php echo date('Y'); ?> EasyTic</span>
</footer>

<?php wp_footer(); ?>
</body>
</html>
