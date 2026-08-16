const authCard = document.getElementById('auth-card');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const togglePwBtn = document.getElementById('toggle-pw');

// Email kiritilayotganda qiziqib qarashadi
emailInput.addEventListener('focus', () => {
  authCard.setAttribute('data-mood', 'nosy');
});

emailInput.addEventListener('blur', () => {
  authCard.setAttribute('data-mood', 'idle');
});

// Parol kiritilayotganda ko'zlarini olib qochishadi
passwordInput.addEventListener('focus', () => {
  if (passwordInput.type === 'password') {
    authCard.setAttribute('data-mood', 'shy');
  } else {
    authCard.setAttribute('data-mood', 'exposed');
  }
});

passwordInput.addEventListener('blur', () => {
  authCard.setAttribute('data-mood', 'idle');
});

// Parolni ko'rsatish/yashirish tugmasi
togglePwBtn.addEventListener('click', () => {
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    authCard.setAttribute('data-mood', 'exposed');
  } else {
    passwordInput.type = 'password';
    authCard.setAttribute('data-mood', 'shy');
  }
});