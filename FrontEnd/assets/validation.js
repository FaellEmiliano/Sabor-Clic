function reservationPeriodError(start,end,now=new Date()) {
  const parse=value=>new Date(value&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value)?value+'-03:00':value);
  const first=parse(start), last=parse(end);
  if(!start||!end||!Number.isFinite(first.getTime())||!Number.isFinite(last.getTime())) return 'Informe início e fim válidos.';
  if(first<now) return 'Escolha um início futuro.';
  if(last<=first) return 'O término deve ser posterior ao início.';
  return '';
}
