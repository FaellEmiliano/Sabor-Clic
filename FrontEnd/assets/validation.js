// Validações simples de formulário — 3º bimestre
// O objetivo nesta etapa é validar entradas no cliente; o backend definitivo validará novamente no 4º bimestre.

function isValidEmail(email) {
  return email.includes("@") && email.includes(".");
}

function validateReservation() {
  const fields = document.querySelectorAll(".form-grid input, .form-grid select");

  for (const field of fields) {
    if (!String(field.value).trim()) {
      showToast("Preencha todos os campos obrigatórios da reserva.");
      field.focus();
      return false;
    }
  }

  const emailField = document.querySelector('.form-grid input[value*="@"]');
  if (emailField && !isValidEmail(emailField.value)) {
    showToast("Informe um e-mail válido.");
    emailField.focus();
    return false;
  }

  showToast("Reserva simulada criada com sucesso.");
  return true;
}

function initReservationValidation() {
  if (!window.location.pathname.endsWith("cliente_reservas.html")) return;

  const buttons = document.querySelectorAll("button");

  for (const button of buttons) {
    if (button.textContent.trim() === "Confirmar reserva") {
      button.onclick = validateReservation;
      break;
    }
  }
}

document.addEventListener("DOMContentLoaded", initReservationValidation);
