-- Dados mínimos de demonstração. Sem senhas reais e sem sobrescrever cadastros.
-- O comando seed-demo fornece @demo_password_hash por parâmetro protegido.
INSERT INTO usuario (nome,email,senha_hash,ativo)
SELECT 'Admin Demonstração','admin@demo.local',@demo_password_hash,1
WHERE @demo_password_hash IS NOT NULL AND NOT EXISTS (SELECT 1 FROM usuario WHERE email='admin@demo.local');
INSERT INTO administrador (id_usuario)
SELECT id_usuario FROM usuario WHERE email='admin@demo.local' AND NOT EXISTS (SELECT 1 FROM administrador a WHERE a.id_usuario=usuario.id_usuario);
INSERT INTO usuario (nome,email,senha_hash,ativo)
SELECT 'Cliente Demonstração','cliente@demo.local',@demo_password_hash,1
WHERE @demo_password_hash IS NOT NULL AND NOT EXISTS (SELECT 1 FROM usuario WHERE email='cliente@demo.local');
INSERT INTO cliente (id_usuario,endereco_entrega)
SELECT id_usuario,'Retirada na bancada' FROM usuario WHERE email='cliente@demo.local' AND NOT EXISTS (SELECT 1 FROM cliente c WHERE c.id_usuario=usuario.id_usuario);
INSERT INTO usuario (nome,email,senha_hash,ativo)
SELECT 'Chef Demonstração','chef@demo.local',@demo_password_hash,1
WHERE @demo_password_hash IS NOT NULL AND NOT EXISTS (SELECT 1 FROM usuario WHERE email='chef@demo.local');
INSERT INTO cozinheiro (id_usuario,turno,especialidade)
SELECT id_usuario,'noite','cozinha geral' FROM usuario WHERE email='chef@demo.local' AND NOT EXISTS (SELECT 1 FROM cozinheiro c WHERE c.id_usuario=usuario.id_usuario);
INSERT INTO bancada (nome,descricao,valor_hora,ativa)
SELECT 'Bancada demonstração','Espaço para o roteiro de apresentação',20,1 WHERE NOT EXISTS (SELECT 1 FROM bancada WHERE nome='Bancada demonstração');
INSERT INTO prato (nome,descricao,preco,ativo)
SELECT 'Risoto demonstração','Prato com ficha técnica e estoque controlado',25,1 WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome='Risoto demonstração');
INSERT INTO ingrediente (nome,unidade_medida,quantidade_estoque)
SELECT 'Arroz demonstração','kg',0 WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome='Arroz demonstração');
INSERT INTO ingrediente (nome,unidade_medida,quantidade_estoque)
SELECT 'Quinoa demonstração','kg',0 WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome='Quinoa demonstração');
UPDATE ingrediente i SET quantidade_estoque=quantidade_estoque+10
WHERE nome IN ('Arroz demonstração','Quinoa demonstração') AND NOT EXISTS (SELECT 1 FROM movimentacao_estoque m WHERE m.chave_evento=CONCAT('seed:',i.id_ingrediente));
INSERT INTO movimentacao_estoque (id_ingrediente,tipo,quantidade,chave_evento)
SELECT id_ingrediente,'entrada',10,CONCAT('seed:',id_ingrediente) FROM ingrediente
WHERE nome IN ('Arroz demonstração','Quinoa demonstração') AND NOT EXISTS (SELECT 1 FROM movimentacao_estoque m WHERE m.chave_evento=CONCAT('seed:',ingrediente.id_ingrediente));
INSERT INTO ficha_tecnica (id_prato,id_ingrediente,quantidade_necessaria)
SELECT p.id_prato,i.id_ingrediente,0.2 FROM prato p JOIN ingrediente i ON i.nome='Arroz demonstração'
WHERE p.nome='Risoto demonstração' AND NOT EXISTS (SELECT 1 FROM ficha_tecnica f WHERE f.id_prato=p.id_prato AND f.id_ingrediente=i.id_ingrediente);
INSERT INTO ingrediente_substituicao (id_ingrediente_original,id_ingrediente_substituto,prioridade,fator_conversao)
SELECT a.id_ingrediente,b.id_ingrediente,1,1.25 FROM ingrediente a JOIN ingrediente b ON b.nome='Quinoa demonstração'
WHERE a.nome='Arroz demonstração' AND NOT EXISTS (SELECT 1 FROM ingrediente_substituicao s WHERE s.id_ingrediente_original=a.id_ingrediente AND s.id_ingrediente_substituto=b.id_ingrediente);
