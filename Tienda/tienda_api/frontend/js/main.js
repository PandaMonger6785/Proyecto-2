function showError(id, msg) {
  const el = document.getElementById(id);
  if (el) el.textContent = msg;
}

function clearErrors() {
  showError('userError', '');  // Limpiar el error del usuario
  showError('passError', '');  // Limpiar el error de la contraseña
  const msg = document.getElementById('msgGlobal');
  if (msg) msg.textContent = '';  // Limpiar mensaje global
}

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('loginForm');
  if (!form || form.dataset.mode !== 'demo') return;  // Si no hay formulario o no está en modo demo, salir

  // Verificación del usuario en sessionStorage
  const userStr = sessionStorage.getItem('user');

  if (userStr) {
    window.location.href = 'index.html';  // Redirigir si la sesión está activa
    return;
  }

  // Manejador de envío del formulario de login
  form.addEventListener('submit', function (e) {
    e.preventDefault();  // Prevenir el comportamiento por defecto

    clearErrors();  // Limpiar errores previos

    const usernameInput = form.querySelector('input[name="username"]');
    const passwordInput = form.querySelector('input[name="password"]');

    const username = usernameInput?.value.trim() || '';
    const password = passwordInput?.value.trim() || '';

    let valid = true;

    // Validación del nombre de usuario
    if (username.length < 4) {
      showError('userError', 'El usuario debe tener al menos 4 caracteres.');
      valid = false;
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      showError('userError', 'Solo se permiten letras, números y guión bajo.');
      valid = false;
    }

    // Validación de la contraseña
    if (password.length < 6) {
      showError('passError', 'La contraseña debe tener al menos 6 caracteres.');
      valid = false;
    }

    if (!valid) {
      const globalMsg = document.getElementById('msgGlobal');
      if (globalMsg) {
        globalMsg.textContent = 'Revisa los datos marcados en rojo.';
      }
      return;  // Detener si hay errores
    }

    // Si todo es válido, almacenar la información en sessionStorage
    const now = Date.now();
    const userData = {
      username: username,
      loginTime: now
    };

    sessionStorage.setItem('user', JSON.stringify(userData));  // Guardar usuario

    window.location.href = 'index.html';  // Redirigir a la página principal
  });
});