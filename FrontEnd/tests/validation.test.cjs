// Run at repository root: node --test FrontEnd/tests/validation.test.cjs
// No external dependencies. These tests exercise the same demonstrative JS used by the HTML page.
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function fixture() {
  const nextYear = String(new Date().getFullYear() + 1);
  const values = {
    reservaData: `${nextYear}-09-23`,
    reservaHorario: "20:00–23:00",
    reservaBancada: "Provence",
    reservaPessoas: "6",
    reservaTelefone: "(11) 99999-0000",
    reservaEmail: "cliente@exemplo.com"
  };
  const fields = Object.fromEntries(
    Object.entries(values).map(([name, value]) => [name, { value, focus() {} }])
  );
  const messages = [];
  const document = {
    getElementById: name => fields[name] || null,
    addEventListener() {}
  };
  const context = {
    document,
    window: { location: { pathname: "cliente_reservas.html" } },
    benches: [
      { nome: "Bancada Provence", status: "Disponível", cap: 6 },
      { nome: "Bancada Toscana", status: "Disponível", cap: 4 }
    ],
    showToast: message => messages.push(message)
  };
  const source = fs.readFileSync(path.join(__dirname, "..", "assets", "validation.js"), "utf8");
  vm.runInNewContext(source, context, { filename: "validation.js" });
  return {
    fields, messages,
    validate: () => context.validateReservation()
  };
}

test("reserva demonstrativa com dados válidos", () => {
  const app = fixture();
  assert.equal(app.validate(), true);
  assert.match(app.messages.at(-1), /demonstrativa confirmada/i);
});

test("e-mail inválido é rejeitado", () => {
  const app = fixture();
  app.fields.reservaEmail.value = "sem-arroba";
  assert.equal(app.validate(), false);
  assert.match(app.messages.at(-1), /e-mail válido/i);
});

test("data passada é rejeitada", () => {
  const app = fixture();
  app.fields.reservaData.value = "2000-01-01";
  assert.equal(app.validate(), false);
  assert.match(app.messages.at(-1), /data atual ou futura/i);
});

test("não permite mais pessoas que a capacidade", () => {
  const app = fixture();
  app.fields.reservaBancada.value = "Toscana";
  app.fields.reservaPessoas.value = "6";
  assert.equal(app.validate(), false);
  assert.match(app.messages.at(-1), /entre 1 e 4/i);
});

test("quantidade de pessoas deve ser inteiro positivo", () => {
  const app = fixture();
  app.fields.reservaPessoas.value = "1.5";
  assert.equal(app.validate(), false);
  assert.match(app.messages.at(-1), /pessoa/i);
});

test("telefone informado deve possuir DDD", () => {
  const app = fixture();
  app.fields.reservaTelefone.value = "123";
  assert.equal(app.validate(), false);
  assert.match(app.messages.at(-1), /telefone/i);
});

test("término deve ser depois do início", () => {
  const app = fixture();
  app.fields.reservaHorario.value = "23:00–20:00";
  assert.equal(app.validate(), false);
  assert.match(app.messages.at(-1), /posterior/i);
});

test("campo obrigatório vazio bloqueia confirmação", () => {
  const app = fixture();
  app.fields.reservaEmail.value = "";
  assert.equal(app.validate(), false);
  assert.match(app.messages.at(-1), /obrigatórios/i);
});
