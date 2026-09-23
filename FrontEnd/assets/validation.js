// Validações de interface do protótipo — 3º bimestre.
// Estas verificações melhoram a experiência, mas NÃO substituem validação/autorização no Flask.

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email || "").trim());
}

function localDateISO(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function reservationError(message, field) {
  showToast(message);
  if (field) field.focus();
  return false;
}

function validateReservation() {
  const fields = {
    date: document.getElementById("reservaData"),
    time: document.getElementById("reservaHorario"),
    bench: document.getElementById("reservaBancada"),
    people: document.getElementById("reservaPessoas"),
    phone: document.getElementById("reservaTelefone"),
    email: document.getElementById("reservaEmail")
  };

  if (Object.values(fields).some(field => !field)) {
    showToast("Formulário de reserva indisponível.");
    return false;
  }

  for (const [name, field] of Object.entries(fields)) {
    if (name !== "phone" && !String(field.value).trim()) {
      return reservationError("Preencha todos os campos obrigatórios da reserva.", field);
    }
  }

  if (fields.date.value < localDateISO()) {
    return reservationError("Escolha uma data atual ou futura.", fields.date);
  }

  const interval = fields.time.value.match(/^(\d{2}):(\d{2})\s*[–-]\s*(\d{2}):(\d{2})$/);
  if (!interval) {
    return reservationError("Informe um horário válido.", fields.time);
  }
  const inicio = Number(interval[1]) * 60 + Number(interval[2]);
  const fim = Number(interval[3]) * 60 + Number(interval[4]);
  if (inicio >= fim || Number(interval[2]) >= 60 || Number(interval[4]) >= 60) {
    return reservationError("O término deve ser posterior ao início da reserva.", fields.time);
  }

  const bancada = benches.find(item => item.nome === `Bancada ${fields.bench.value}`);
  if (!bancada || bancada.status !== "Disponível") {
    return reservationError("Selecione uma bancada disponível.", fields.bench);
  }

  const pessoas = Number(fields.people.value);
  if (!Number.isInteger(pessoas) || pessoas < 1 || pessoas > bancada.cap) {
    return reservationError(`Informe entre 1 e ${bancada.cap} pessoa(s) para esta bancada.`, fields.people);
  }

  const telefoneInformado = fields.phone.value.trim();
  const telefone = telefoneInformado.replace(/\D/g, "");
  if (telefoneInformado && (!/^[0-9()\s+-]+$/.test(telefoneInformado) || !/^\d{10,11}$/.test(telefone))) {
    return reservationError("Informe um telefone com DDD (10 ou 11 dígitos).", fields.phone);
  }

  if (!isValidEmail(fields.email.value)) {
    return reservationError("Informe um e-mail válido.", fields.email);
  }

  // Somente demonstração: ainda não cria uma reserva na API ou no banco de dados.
  showToast("Dados válidos! Reserva demonstrativa confirmada.");
  return true;
}

function initReservationValidation() {
  if (!window.location.pathname.endsWith("cliente_reservas.html")) return;
  const date = document.getElementById("reservaData");
  if (!date) return;
  const today = localDateISO();
  date.min = today;
  if (!date.value || date.value < today) date.value = today;

  const button = document.getElementById("confirmarReserva");
  if (button) button.onclick = validateReservation;
}

document.addEventListener("DOMContentLoaded", initReservationValidation);
