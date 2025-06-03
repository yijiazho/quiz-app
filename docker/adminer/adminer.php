<?php
function adminer_custom_object() {
    class AdminerCustomization extends Adminer {
        function login($login, $password) {
            return true;
        }
    }
    return new AdminerCustomization;
}

// Override the original adminer_object function
if (!function_exists('adminer_object')) {
    function adminer_object() {
        return adminer_custom_object();
    }
} 