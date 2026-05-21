# Despliegue por FTP — Child theme y páginas Productos

## Paso 1 — Subir el child theme por FTP

Conecta tu cliente FTP (FileZilla, Transmit, etc.) al servidor de easytic.es y sube la carpeta entera:

```
Local:  wp-child-theme/customizr-child/
Remote: /wp-content/themes/customizr-child/
```

La estructura remota debe quedar así:

```
/wp-content/themes/customizr-child/
├── style.css
├── functions.php
├── template-easyfix-landing.php
└── assets/
    ├── easyfix-logo.png
    ├── easyfix-symbol.png
    └── easyfix-pro-symbol.png
```

---

## Paso 2 — Activar el child theme en WordPress Admin

1. WordPress Admin → **Apariencia → Temas**
2. Localiza **"Customizr Child — EasyTic"** y haz clic en **Activar**

> El tema padre `customizr-4-2-2` debe seguir instalado — el child theme lo hereda automáticamente.

---

## Paso 3 — Crear la página hub "Productos"

1. **Páginas → Añadir nueva**
2. Título: `Productos digitales`
3. Slug: `productos` (verifica en el panel derecho → Enlace permanente)
4. Página padre: *(ninguna)*
5. Plantilla: **Página completa** o **Sin barra lateral** (panel derecho → Atributos de página)
6. Abre el editor en modo HTML: menú de tres puntos (⋮) → **Editor de código**
7. Pega el contenido íntegro de `productos/productos-hub.html`
8. **Publicar**

---

## Paso 4 — Crear la página EasyFix

1. **Páginas → Añadir nueva**
2. Título: `EasyFix — Gestión de taller mecánico`
3. Slug: `easyfix`
4. Página padre: **Productos digitales**
5. Plantilla: **EasyFix Landing** ← aparece en el selector porque subiste `template-easyfix-landing.php`
6. El editor puede quedar vacío — la plantilla es autocontenida
7. **Publicar**

La landing quedará en `easytic.es/productos/easyfix/`

> Si no aparece "EasyFix Landing" en el selector de plantillas, verifica que el archivo
> `template-easyfix-landing.php` está en `/wp-content/themes/customizr-child/` y que el
> child theme está activo.

---

## Paso 5 — Añadir "Productos" al menú principal

1. **Apariencia → Menús**
2. Selecciona el menú principal (cabecera)
3. Panel izquierdo → **Páginas** → busca **Productos digitales** → **Añadir al menú**
4. Arrástrala entre "Qué hacemos" y "Clientes"
5. Despliega el ítem y cambia el texto de navegación a: **Productos**
6. **Guardar menú**

---

## Paso 6 — Verificar URLs de clientes en el hub

En la página hub ya publicada, los botones "Visitar web" usan estas URLs — comprueba que son correctas:

| Cliente | URL usada | Estado |
|---------|-----------|--------|
| ChirinaCars | `https://chirinacars.es` | Verificar dominio real |
| PGA Industria | `https://pgaindustria.com` | Parece correcto |
| ¿Qué cocinas? | `#` | Añadir URL cuando esté publicada |

---

## Resultado final

| URL | Contenido |
|-----|-----------|
| `easytic.es/productos/` | Hub con grid de apps y webs de clientes |
| `easytic.es/productos/easyfix/` | Landing de ventas EasyFix (sin header/footer del tema) |
