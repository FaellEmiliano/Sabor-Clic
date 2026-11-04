-- Migração aditiva do esquema de outubro. migrate-db verifica a existência de cada item.
ALTER TABLE `pedido` ADD COLUMN `chave_idempotencia` varchar(64) DEFAULT NULL;
ALTER TABLE `pedido` ADD COLUMN `hash_requisicao` varchar(64) DEFAULT NULL;
ALTER TABLE `pedido` ADD COLUMN `observacoes` varchar(500) DEFAULT NULL;
ALTER TABLE `pedido` ADD COLUMN `preparo_em` datetime DEFAULT NULL;
ALTER TABLE `pedido` ADD COLUMN `pronto_em` datetime DEFAULT NULL;
ALTER TABLE `pedido` ADD COLUMN `entregue_em` datetime DEFAULT NULL;
ALTER TABLE `pedido` ADD COLUMN `cancelado_em` datetime DEFAULT NULL;
ALTER TABLE `item_pedido` ADD COLUMN `nome_prato` varchar(120) DEFAULT NULL;
ALTER TABLE `pedido` ADD UNIQUE KEY `uq_pedido_idempotencia` (`id_sessao`,`chave_idempotencia`);
ALTER TABLE `bancada` ADD CONSTRAINT `chk_bancada_valor` CHECK (`valor_hora` >= 0);
ALTER TABLE `prato` ADD CONSTRAINT `chk_prato_valor` CHECK (`preco` >= 0);
ALTER TABLE `ingrediente` ADD CONSTRAINT `chk_ingrediente_valor` CHECK (`quantidade_estoque` >= 0);
ALTER TABLE `reserva` ADD CONSTRAINT `chk_reserva_valor` CHECK (`valor_total` >= 0);
ALTER TABLE `pedido` ADD CONSTRAINT `chk_pedido_valor` CHECK (`valor_total` >= 0);
ALTER TABLE `pedido` ADD CONSTRAINT `chk_pedido_tempo` CHECK (`tempo_estimado` IS NULL OR `tempo_estimado` >= 0);
ALTER TABLE `item_pedido` ADD CONSTRAINT `chk_item_valores` CHECK (`preco_unitario` >= 0 AND `subtotal` >= 0);
