-- Dados de demonstração. Sem senhas reais e sem sobrescrever cadastros.
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


-- Bancadas com tarifas, capacidades e situações variadas.
INSERT INTO bancada (nome, descricao, valor_hora, ativa)
SELECT demo.nome, demo.descricao, demo.valor_hora, demo.ativa
FROM (
    SELECT 'Aurora' AS nome, 'Bancada para duas pessoas, perto da entrada.' AS descricao, 24 AS valor_hora, 1 AS ativa
    UNION ALL
    SELECT 'Cedro', 'Bancada de canto para duas pessoas, com assentos altos.', 26, 1
    UNION ALL
    SELECT 'Ipê', 'Bancada central para três pessoas, com vista da cozinha.', 30, 1
    UNION ALL
    SELECT 'Manacá', 'Bancada para quatro pessoas, em área mais reservada.', 34, 1
    UNION ALL
    SELECT 'Provence', 'Bancada baixa para quatro pessoas, com espaço de aproximação.', 36, 1
    UNION ALL
    SELECT 'Toscana', 'Bancada para seis pessoas, voltada para a cozinha aberta.', 48, 1
    UNION ALL
    SELECT 'Jasmim', 'Bancada de apoio temporariamente em manutenção.', 22, 0
) AS demo
WHERE NOT EXISTS (SELECT 1 FROM bancada b WHERE b.nome = demo.nome);

-- Cada ingrediente novo recebe seu saldo inicial e a entrada correspondente.
INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Pão italiano', 'kg', 5
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Pão italiano');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 5, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Tomate italiano', 'kg', 10
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Tomate italiano');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 10, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Manjericão', 'kg', 0.5
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Manjericão');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 0.5, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Azeite de oliva', 'L', 4
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Azeite de oliva');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 4, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Arroz arbóreo', 'kg', 8
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Arroz arbóreo');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 8, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Cogumelo paris', 'kg', 6
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Cogumelo paris');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 6, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Parmesão', 'kg', 3
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Parmesão');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 3, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Caldo de legumes', 'L', 18
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Caldo de legumes');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 18, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Manteiga', 'kg', 3
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Manteiga');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 3, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Nhoque de batata', 'kg', 10
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Nhoque de batata');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 10, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Molho de tomate', 'kg', 8
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Molho de tomate');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 8, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Hambúrguer bovino', 'kg', 12
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Hambúrguer bovino');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 12, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Pão brioche', 'un', 48
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Pão brioche');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 48, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Cheddar', 'kg', 4
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Cheddar');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 4, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Alface crespa', 'kg', 5
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Alface crespa');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 5, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Maionese', 'kg', 3
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Maionese');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 3, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Petit gâteau de chocolate', 'un', 36
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Petit gâteau de chocolate');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 36, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Sorvete de baunilha', 'kg', 5
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Sorvete de baunilha');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 5, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Torta de limão porcionada', 'un', 28
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Torta de limão porcionada');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 28, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Laranja pera', 'kg', 24
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Laranja pera');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 24, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Gelo', 'kg', 20
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Gelo');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 20, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Água com gás', 'L', 16
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Água com gás');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 16, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Xarope de frutas vermelhas', 'L', 4
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Xarope de frutas vermelhas');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 4, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

INSERT INTO ingrediente (nome, unidade_medida, quantidade_estoque)
SELECT 'Limão tahiti', 'kg', 5
WHERE NOT EXISTS (SELECT 1 FROM ingrediente WHERE nome = 'Limão tahiti');
INSERT INTO movimentacao_estoque (id_ingrediente, tipo, quantidade, chave_evento)
SELECT LAST_INSERT_ID(), 'entrada', 5, CONCAT('seed:', LAST_INSERT_ID())
WHERE ROW_COUNT() = 1;

-- As fotos são da biblioteca local. Só os pratos novos recebem fichas técnicas.
INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Bruschetta de tomate e manjericão', 'Pão italiano tostado com tomate fresco, manjericão e azeite.', 24, 1, '/assets/img/products/bruschetta.jpg'
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Bruschetta de tomate e manjericão');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Pão italiano' AS ingrediente, 'kg' AS unidade, 0.12 AS quantidade
    UNION ALL
    SELECT 'Tomate italiano', 'kg', 0.09
    UNION ALL
    SELECT 'Manjericão', 'kg', 0.008
    UNION ALL
    SELECT 'Azeite de oliva', 'L', 0.015
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Risoto de cogumelos', 'Arroz arbóreo cremoso com cogumelos salteados e parmesão.', 49, 1, '/assets/img/products/risoto.jpg'
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Risoto de cogumelos');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Arroz arbóreo' AS ingrediente, 'kg' AS unidade, 0.11 AS quantidade
    UNION ALL
    SELECT 'Cogumelo paris', 'kg', 0.12
    UNION ALL
    SELECT 'Parmesão', 'kg', 0.035
    UNION ALL
    SELECT 'Caldo de legumes', 'L', 0.35
    UNION ALL
    SELECT 'Manteiga', 'kg', 0.025
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Nhoque ao sugo', 'Nhoque de batata com molho de tomate, parmesão e manjericão.', 42, 1, '/assets/img/products/nhoque.jpg'
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Nhoque ao sugo');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Nhoque de batata' AS ingrediente, 'kg' AS unidade, 0.24 AS quantidade
    UNION ALL
    SELECT 'Molho de tomate', 'kg', 0.16
    UNION ALL
    SELECT 'Parmesão', 'kg', 0.025
    UNION ALL
    SELECT 'Manjericão', 'kg', 0.005
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Hambúrguer artesanal', 'Hambúrguer bovino com cheddar, alface, tomate e maionese da casa.', 39, 1, '/assets/img/products/burger.jpg'
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Hambúrguer artesanal');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Hambúrguer bovino' AS ingrediente, 'kg' AS unidade, 0.16 AS quantidade
    UNION ALL
    SELECT 'Pão brioche', 'un', 1
    UNION ALL
    SELECT 'Cheddar', 'kg', 0.04
    UNION ALL
    SELECT 'Alface crespa', 'kg', 0.025
    UNION ALL
    SELECT 'Tomate italiano', 'kg', 0.04
    UNION ALL
    SELECT 'Maionese', 'kg', 0.025
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Petit gâteau com sorvete', 'Bolinho quente de chocolate com uma bola de sorvete de baunilha.', 28, 1, '/assets/img/products/petit-gateau.jpg'
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Petit gâteau com sorvete');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Petit gâteau de chocolate' AS ingrediente, 'un' AS unidade, 1 AS quantidade
    UNION ALL
    SELECT 'Sorvete de baunilha', 'kg', 0.08
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Torta de limão', 'Fatia de torta cítrica com base crocante e cobertura de merengue.', 22, 1, '/assets/img/products/torta-limao.jpg'
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Torta de limão');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Torta de limão porcionada' AS ingrediente, 'un' AS unidade, 1 AS quantidade
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Suco de laranja', 'Suco natural espremido na hora, servido com gelo.', 15, 1, '/assets/img/products/suco-laranja.jpg'
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Suco de laranja');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Laranja pera' AS ingrediente, 'kg' AS unidade, 0.55 AS quantidade
    UNION ALL
    SELECT 'Gelo', 'kg', 0.08
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Soda italiana de frutas vermelhas', 'Água com gás, xarope de frutas vermelhas, limão e gelo.', 18, 1, '/assets/img/products/soda-italiana.jpg'
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Soda italiana de frutas vermelhas');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Água com gás' AS ingrediente, 'L' AS unidade, 0.25 AS quantidade
    UNION ALL
    SELECT 'Xarope de frutas vermelhas', 'L', 0.05
    UNION ALL
    SELECT 'Limão tahiti', 'kg', 0.025
    UNION ALL
    SELECT 'Gelo', 'kg', 0.09
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Pão tostado com cogumelos', 'Pão italiano com cogumelos na manteiga e lascas de parmesão.', 29, 1, NULL
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Pão tostado com cogumelos');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Pão italiano' AS ingrediente, 'kg' AS unidade, 0.12 AS quantidade
    UNION ALL
    SELECT 'Cogumelo paris', 'kg', 0.12
    UNION ALL
    SELECT 'Manteiga', 'kg', 0.02
    UNION ALL
    SELECT 'Parmesão', 'kg', 0.02
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;

INSERT INTO prato (nome, descricao, preco, ativo, imagem)
SELECT 'Salada de folhas e tomate', 'Alface crespa, tomate italiano e manjericão com azeite e limão.', 26, 1, NULL
WHERE NOT EXISTS (SELECT 1 FROM prato WHERE nome = 'Salada de folhas e tomate');
SET @demo_prato_id = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), NULL);

INSERT INTO ficha_tecnica (id_prato, id_ingrediente, quantidade_necessaria)
SELECT @demo_prato_id, MIN(i.id_ingrediente), receita.quantidade
FROM (
    SELECT 'Alface crespa' AS ingrediente, 'kg' AS unidade, 0.11 AS quantidade
    UNION ALL
    SELECT 'Tomate italiano', 'kg', 0.1
    UNION ALL
    SELECT 'Manjericão', 'kg', 0.005
    UNION ALL
    SELECT 'Azeite de oliva', 'L', 0.015
    UNION ALL
    SELECT 'Limão tahiti', 'kg', 0.02
) AS receita
JOIN ingrediente i ON i.nome = receita.ingrediente AND i.unidade_medida = receita.unidade
WHERE @demo_prato_id IS NOT NULL
GROUP BY receita.ingrediente, receita.quantidade
HAVING COUNT(*) = 1;
