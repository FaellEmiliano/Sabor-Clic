-- Modelo físico final, escrito em SQL. MySQL 8 / InnoDB / utf8mb4.
-- Não apaga tabelas ou registros existentes. Atualizações de tabelas legadas usam migrate-db.

CREATE TABLE IF NOT EXISTS `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(180) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  `senha_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `cliente` (
  `id_usuario` int NOT NULL,
  `endereco_entrega` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  CONSTRAINT `fk_cliente_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `cozinheiro` (
  `id_usuario` int NOT NULL,
  `turno` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `especialidade` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  CONSTRAINT `fk_cozinheiro_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `administrador` (
  `id_usuario` int NOT NULL,
  PRIMARY KEY (`id_usuario`),
  CONSTRAINT `fk_administrador_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `bancada` (
  `id_bancada` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `valor_hora` decimal(10,2) NOT NULL,
  `ativa` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_bancada`),
  CONSTRAINT `chk_bancada_valor` CHECK (`valor_hora` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `prato` (
  `id_prato` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `preco` decimal(10,2) NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_prato`),
  CONSTRAINT `chk_prato_valor` CHECK (`preco` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `ingrediente` (
  `id_ingrediente` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unidade_medida` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantidade_estoque` decimal(12,3) NOT NULL DEFAULT '0.000',
  PRIMARY KEY (`id_ingrediente`),
  CONSTRAINT `chk_ingrediente_valor` CHECK (`quantidade_estoque` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `reserva` (
  `id_reserva` int NOT NULL AUTO_INCREMENT,
  `id_cliente` int NOT NULL,
  `id_bancada` int NOT NULL,
  `inicio` datetime NOT NULL,
  `fim` datetime NOT NULL,
  `status` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `valor_total` decimal(10,2) NOT NULL DEFAULT '0.00',
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_reserva`),
  KEY `fk_reserva_cliente` (`id_cliente`),
  KEY `fk_reserva_bancada` (`id_bancada`),
  CONSTRAINT `fk_reserva_bancada` FOREIGN KEY (`id_bancada`) REFERENCES `bancada` (`id_bancada`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_reserva_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_reserva_periodo` CHECK ((`fim` > `inicio`)),
  CONSTRAINT `chk_reserva_valor` CHECK (`valor_total` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `sessao` (
  `id_sessao` int NOT NULL AUTO_INCREMENT,
  `id_reserva` int NOT NULL,
  `codigo_acesso` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `iniciado_em` datetime DEFAULT NULL,
  `encerrado_em` datetime DEFAULT NULL,
  PRIMARY KEY (`id_sessao`),
  UNIQUE KEY `id_reserva` (`id_reserva`),
  UNIQUE KEY `codigo_acesso` (`codigo_acesso`),
  CONSTRAINT `fk_sessao_reserva` FOREIGN KEY (`id_reserva`) REFERENCES `reserva` (`id_reserva`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `pedido` (
  `id_pedido` int NOT NULL AUTO_INCREMENT,
  `id_sessao` int NOT NULL,
  `status` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `valor_total` decimal(10,2) NOT NULL DEFAULT '0.00',
  `tempo_estimado` int DEFAULT NULL,
  `endereco_entrega` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `chave_idempotencia` varchar(64) DEFAULT NULL,
  `hash_requisicao` varchar(64) DEFAULT NULL,
  `observacoes` varchar(500) DEFAULT NULL,
  `preparo_em` datetime DEFAULT NULL,
  `pronto_em` datetime DEFAULT NULL,
  `entregue_em` datetime DEFAULT NULL,
  `cancelado_em` datetime DEFAULT NULL,
  PRIMARY KEY (`id_pedido`),
  KEY `fk_pedido_sessao` (`id_sessao`),
  CONSTRAINT `fk_pedido_sessao` FOREIGN KEY (`id_sessao`) REFERENCES `sessao` (`id_sessao`) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE KEY `uq_pedido_idempotencia` (`id_sessao`,`chave_idempotencia`),
  CONSTRAINT `chk_pedido_valor` CHECK (`valor_total` >= 0),
  CONSTRAINT `chk_pedido_tempo` CHECK (`tempo_estimado` IS NULL OR `tempo_estimado` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `item_pedido` (
  `id_item_pedido` int NOT NULL AUTO_INCREMENT,
  `id_pedido` int NOT NULL,
  `id_prato` int NOT NULL,
  `quantidade` int NOT NULL,
  `preco_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `nome_prato` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`id_item_pedido`),
  KEY `fk_item_pedido_pedido` (`id_pedido`),
  KEY `fk_item_pedido_prato` (`id_prato`),
  CONSTRAINT `fk_item_pedido_pedido` FOREIGN KEY (`id_pedido`) REFERENCES `pedido` (`id_pedido`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_item_pedido_prato` FOREIGN KEY (`id_prato`) REFERENCES `prato` (`id_prato`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_item_pedido_quantidade` CHECK ((`quantidade` > 0)),
  CONSTRAINT `chk_item_valores` CHECK (`preco_unitario` >= 0 AND `subtotal` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `ficha_tecnica` (
  `id_prato` int NOT NULL,
  `id_ingrediente` int NOT NULL,
  `quantidade_necessaria` decimal(12,3) NOT NULL,
  PRIMARY KEY (`id_prato`,`id_ingrediente`),
  KEY `fk_ficha_tecnica_ingrediente` (`id_ingrediente`),
  CONSTRAINT `fk_ficha_tecnica_ingrediente` FOREIGN KEY (`id_ingrediente`) REFERENCES `ingrediente` (`id_ingrediente`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ficha_tecnica_prato` FOREIGN KEY (`id_prato`) REFERENCES `prato` (`id_prato`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_ficha_quantidade` CHECK ((`quantidade_necessaria` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `ingrediente_substituicao` (
  `id_ingrediente_original` int NOT NULL,
  `id_ingrediente_substituto` int NOT NULL,
  `prioridade` int NOT NULL DEFAULT '1',
  `fator_conversao` decimal(10,4) NOT NULL DEFAULT '1.0000',
  PRIMARY KEY (`id_ingrediente_original`,`id_ingrediente_substituto`),
  KEY `fk_substituicao_substituto` (`id_ingrediente_substituto`),
  CONSTRAINT `fk_substituicao_original` FOREIGN KEY (`id_ingrediente_original`) REFERENCES `ingrediente` (`id_ingrediente`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_substituicao_substituto` FOREIGN KEY (`id_ingrediente_substituto`) REFERENCES `ingrediente` (`id_ingrediente`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_substituicao_fator` CHECK ((`fator_conversao` > 0)),
  CONSTRAINT `chk_substituicao_prioridade` CHECK ((`prioridade` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `sessao_autenticacao` (
  `id_sessao_auth` varchar(64) NOT NULL,
  `id_usuario` int NOT NULL,
  `versao_senha` varchar(64) NOT NULL,
  `criado_em` datetime NOT NULL,
  `ultimo_acesso` datetime NOT NULL,
  `expira_em` datetime NOT NULL,
  `revogada` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_sessao_auth`),
  KEY `ix_auth_usuario` (`id_usuario`),
  CONSTRAINT `fk_auth_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `limite_acesso` (
  `chave` varchar(64) NOT NULL,
  `inicio` datetime NOT NULL,
  `tentativas` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`chave`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `evento_auditoria` (
  `id_evento` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `criado_em` datetime NOT NULL,
  `acao` varchar(12) NOT NULL,
  `recurso` varchar(255) NOT NULL,
  `resultado` int NOT NULL,
  `correlacao` varchar(64) NOT NULL,
  PRIMARY KEY (`id_evento`),
  KEY `ix_auditoria_criado` (`criado_em`),
  CONSTRAINT `fk_auditoria_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `movimentacao_estoque` (
  `id_movimentacao` int NOT NULL AUTO_INCREMENT,
  `id_ingrediente` int NOT NULL,
  `id_ingrediente_original` int DEFAULT NULL,
  `id_pedido` int DEFAULT NULL,
  `tipo` varchar(20) NOT NULL,
  `quantidade` decimal(12,3) NOT NULL,
  `chave_evento` varchar(100) NOT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_movimentacao`),
  UNIQUE KEY `uq_movimento_evento` (`chave_evento`),
  KEY `ix_movimento_ingrediente` (`id_ingrediente`),
  KEY `ix_movimento_pedido` (`id_pedido`),
  CONSTRAINT `fk_movimento_ingrediente` FOREIGN KEY (`id_ingrediente`) REFERENCES `ingrediente` (`id_ingrediente`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_movimento_original` FOREIGN KEY (`id_ingrediente_original`) REFERENCES `ingrediente` (`id_ingrediente`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_movimento_pedido` FOREIGN KEY (`id_pedido`) REFERENCES `pedido` (`id_pedido`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_movimento_quantidade` CHECK (`quantidade` <> 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
