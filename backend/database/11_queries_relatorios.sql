-- Consultas analíticas SQL. Período [@inicio,@fim), configurável antes da execução.
SET @inicio = COALESCE(@inicio, '2000-01-01');
SET @fim = COALESCE(@fim, '2100-01-01');
-- Vendas e ticket médio dos pedidos efetivamente entregues.
SELECT COUNT(*) AS pedidos_entregues, COALESCE(SUM(valor_total),0) AS receita,
       COALESCE(AVG(valor_total),0) AS ticket_medio,
       AVG(TIMESTAMPDIFF(SECOND,preparo_em,pronto_em))/60 AS tempo_medio_preparo_min
FROM pedido WHERE status='entregue' AND criado_em>=@inicio AND criado_em<@fim;
-- Consumo e estornos por ingrediente no período.
SELECT i.id_ingrediente,i.nome,i.unidade_medida,i.quantidade_estoque,
       COALESCE(SUM(CASE WHEN m.tipo='consumo' THEN -m.quantidade ELSE 0 END),0) AS consumo,
       COALESCE(SUM(CASE WHEN m.tipo='estorno' THEN m.quantidade ELSE 0 END),0) AS estorno
FROM ingrediente i LEFT JOIN movimentacao_estoque m ON m.id_ingrediente=i.id_ingrediente AND m.criado_em>=@inicio AND m.criado_em<@fim
GROUP BY i.id_ingrediente,i.nome,i.unidade_medida,i.quantidade_estoque;
-- Ocupação contratada e receita de reservas concluídas por bancada.
SELECT b.id_bancada,b.nome,COUNT(r.id_reserva) AS reservas,
       COALESCE(SUM(TIMESTAMPDIFF(SECOND,r.inicio,r.fim))/3600,0) AS horas_reservadas,
       COALESCE(SUM(CASE WHEN r.status='concluida' THEN r.valor_total ELSE 0 END),0) AS receita_reservas
FROM bancada b LEFT JOIN reserva r ON r.id_bancada=b.id_bancada AND r.status<>'cancelada' AND r.inicio>=@inicio AND r.inicio<@fim
GROUP BY b.id_bancada,b.nome;
-- Auditoria operacional por resultado e dia, sem segredos ou payloads pessoais.
SELECT DATE(criado_em) AS dia,resultado,COUNT(*) AS eventos FROM evento_auditoria
WHERE criado_em>=@inicio AND criado_em<@fim GROUP BY DATE(criado_em),resultado ORDER BY dia;
