# Instrucciones de implementación — WordPress easytic.es

## Estructura de páginas a crear

```
easytic.es/
└── productos/                    ← página raíz nueva
    ├── (hub)                     ← productos-hub.html
    └── easyfix/                  ← easyfix.html
```

---

## Paso 1 — Crear la página hub "Productos"

1. En WordPress Admin → **Páginas → Añadir nueva**
2. Título: `Productos digitales`
3. Slug: `productos`
4. Página padre: (ninguna — raíz)
5. Plantilla: **Página completa** o **Sin barra lateral** (según tema Customizr)
6. Abre el editor en modo **HTML** (tres puntos → Editor de código)
7. Pega el contenido íntegro de `productos-hub.html`
8. Publica

---

## Paso 2 — Crear la página EasyFix

1. En WordPress Admin → **Páginas → Añadir nueva**
2. Título: `EasyFix — Gestión de taller mecánico`
3. Slug: `easyfix`
4. **Página padre: Productos digitales** (el que acabas de crear)
5. Plantilla: **Página completa** o **Sin barra lateral**
6. Abre el editor en modo **HTML**
7. Pega el contenido íntegro de `easyfix.html`
8. Publica

---

## Paso 3 — Añadir "Productos" al menú principal

1. WordPress Admin → **Apariencia → Menús**
2. Selecciona el menú principal (cabecera)
3. En el panel izquierdo busca la página **Productos digitales** y añádela
4. Arrástrala a la posición deseada en el menú (entre "Qué hacemos" y "Clientes" queda bien)
5. Cambia el texto de navegación a: **Productos**
6. Guarda el menú

---

## Paso 4 — Ajustar URLs de clientes

En `productos-hub.html`, edita los href de los botones "Visitar web" con las URLs reales:

| Proyecto       | URL actual (placeholder)       | URL real             |
|----------------|-------------------------------|----------------------|
| ChirinaCars    | `https://chirinacars.es`      | Verificar dominio real |
| IONSA Huelva   | `https://ionsahuelva.es`      | Verificar dominio real |
| PGA Industria  | `https://pgaindustria.com`    | Verificar (parece correcto) |
| ¿Qué cocinas?  | `#`                           | Añadir URL si está publicada |

---

## Paso 5 — Ajustar colores al tema (opcional)

Los estilos usan CSS variables definidas en los bloques `wp:html` de cada fichero.
Para cambiar el esquema cromático, edita las variables al principio de cada página:

**En productos-hub.html:**
```css
--et-navy:   #0d1f3c;   /* Fondo oscuro hero */
--et-blue:   #1565c0;   /* Azul principal */
--et-accent: #f57c00;   /* Naranja/ámbar CTAs */
```

**En easyfix.html:**
```css
--ef-amber:  #f57c00;   /* Color principal EasyFix */
--ef-navy:   #1a2744;   /* Fondo oscuro */
--ef-blue:   #1565c0;   /* Azul secundario */
```

---

## Notas adicionales

- Los bloques `<details>/<summary>` del FAQ de EasyFix funcionan con HTML nativo — no requieren JavaScript.
- Los enlaces de Google Play apuntan a los app IDs reales (`es.easytic.easyfix` y `es.easytic.easyfix.pro`).
- Para añadir capturas de pantalla reales de la app, reemplaza los bloques de icono emoji 📱 por bloques `<!-- wp:image -->` con las imágenes subidas a la biblioteca de medios.
- La página EasyBoat en `/productos/easyboat/` puede crearse en el futuro con la misma estructura.
