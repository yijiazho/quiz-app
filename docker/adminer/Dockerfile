FROM adminer:latest

# Create plugins directory
RUN mkdir -p /var/www/html/plugins-enabled

# Create a simple plugin that disables authentication
RUN printf '<?php\nclass AdminerNoAuth {\n    function login($login, $password) {\n        return true;\n    }\n}\nreturn new AdminerNoAuth;\n' > /var/www/html/plugins-enabled/no-auth.php 