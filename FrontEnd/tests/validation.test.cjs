const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const context={};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/validation.js'),'utf8'),context);
// Aceita um horário futuro com início anterior ao fim.
test('período futuro válido',()=>assert.equal(context.reservationPeriodError('2030-01-01T18:00','2030-01-01T20:00',new Date('2029-01-01')),''));
// Rejeita um fim anterior ao início.
test('rejeita período invertido',()=>assert.match(context.reservationPeriodError('2030-01-01T20:00','2030-01-01T18:00',new Date('2029-01-01')),/posterior/));
// Rejeita horários passados e datas que não podem ser interpretadas.
test('rejeita passado e data inválida',()=>{
  assert.match(context.reservationPeriodError('2000-01-01','2000-01-02'),/futuro/);
  assert.match(context.reservationPeriodError('inválido','2030-01-01'),/válidos/);
});
