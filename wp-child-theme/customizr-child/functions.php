<?php
/**
 * Customizr Child — EasyTic
 * Carga el stylesheet del tema padre.
 */
add_action( 'wp_enqueue_scripts', 'customizr_child_enqueue_styles' );
function customizr_child_enqueue_styles() {
    wp_enqueue_style(
        'customizr-parent-style',
        get_template_directory_uri() . '/style.css'
    );
}
