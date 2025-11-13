// Tiempo de sesión en milisegundos (60 segundos)
const SESSION_TIMEOUT = 60 * 1000;

function showError(id, msg) {
  document.getElementById(id).textContent = msg;
}

function clearErrors() {
  showError('userError', '');
  showError('passError', '');
  document.getElementById('msgGlobal').textContent = '';
}

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('loginForm');

  // Si ya hay sesión activa y no ha caducado, mandar al index
  const userStr = sessionStorage.getItem('user');
  const lastActivity = parseInt(sessionStorage.getItem('lastActivity') || '0', 10);

  if (userStr && lastActivity) {
    const diff = Date.now() - lastActivity;
    if (diff < SESSION_TIMEOUT) {
      window.location.href = 'index.html';
      return;
    } else {
      sessionStorage.clear();
    }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    clearErrors();

    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    let valid = true;

    // Validación de usuario
    if (username.length < 4) {
      showError('userError', 'El usuario debe tener al menos 4 caracteres.');
      valid = false;
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      showError('userError', 'Solo se permiten letras, números y guión bajo.');
      valid = false;
    }

    // Validación de contraseña
    if (password.length < 6) {
      showError('passError', 'La contraseña debe tener al menos 6 caracteres.');
      valid = false;
    }

    if (!valid) {
      document.getElementById('msgGlobal').textContent =
        'Revisa los datos marcados en rojo.';
      return;
    }

    // =========================================
    // Aquí iría la validación real contra BD.
    // Por ahora suponemos que es correcta.
    // =========================================

    const now = Date.now();
    const userData = {
      username: username,
      loginTime: now
    };

    sessionStorage.setItem('user', JSON.stringify(userData));
    sessionStorage.setItem('lastActivity', String(now));

    // Redirigir a tu página principal
    window.location.href = 'index.html';
  });
});
