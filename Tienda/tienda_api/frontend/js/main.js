function showError(id, msg) {
  const el = document.getElementById(id);
  if (el) el.textContent = msg;
}

function clearErrors() {
  showError('userError', '');  
  showError('passError', '');  
  const msg = document.getElementById('msgGlobal');
  if (msg) msg.textContent = '';  
}

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('loginForm');
  if (!form || form.dataset.mode !== 'demo') return;  

  // Verificación del usuario en sessionStorage
  const userStr = sessionStorage.getItem('user');

  if (userStr) {
    window.location.href = 'index.html';  
    return;
  }

  
  form.addEventListener('submit', function (e) {
    e.preventDefault();  

    clearErrors();  

    const usernameInput = form.querySelector('input[name="username"]');
    const passwordInput = form.querySelector('input[name="password"]');

    const username = usernameInput?.value.trim() || '';
    const password = passwordInput?.value.trim() || '';

    let valid = true;

    
    if (username.length < 4) {
      showError('userError', 'El usuario debe tener al menos 4 caracteres.');
      valid = false;
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      showError('userError', 'Solo se permiten letras, números y guión bajo.');
      valid = false;
    }

    
    if (password.length < 6) {
      showError('passError', 'La contraseña debe tener al menos 6 caracteres.');
      valid = false;
    }

    if (!valid) {
      const globalMsg = document.getElementById('msgGlobal');
      if (globalMsg) {
        globalMsg.textContent = 'Revisa los datos marcados en rojo.';
      }
      return;  
    }

    
    const now = Date.now();
    const userData = {
      username: username,
      loginTime: now
    };

    sessionStorage.setItem('user', JSON.stringify(userData));  

    window.location.href = 'index.html'; 
  });
});