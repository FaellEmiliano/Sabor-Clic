# Verificação da implementação

Referência: 02/11/2026. A implementação foi ampliada após a auditoria original. Triggers foram excluídas por instrução explícita do usuário; estoque funciona por transações no backend.

## Verificações executadas

- Python: 41 testes aprovados na suíte de models/API e novas regressões para logout revogado, rate limit, reagendamento no passado, consumo/estorno, substituição, idempotência, auditoria, paginação, fuso e senhas preservadas.
- JavaScript: 8 testes aprovados, incluindo HTTP integrado; entidades com herança e campos privados, centavos, quantidades, recuperação de estado, payload de pedido e validação de datas.
- HTTP integrado: JavaScript de produção, API e banco SQLite descartável nas 21 telas. Regressões incluem mais de 50 pratos/ingredientes/reservas/pedidos e totais da sessão sem truncamento.
- MySQL 8.0.46 descartável: migração repetível, seeds repetíveis, ausência de triggers, baixa/estorno, cookie revogado, checkout idempotente, dois pedidos concorrentes disputando saldo, duas reservas simultâneas no mesmo intervalo, consultas SQL e round-trip de backup/restauração.
- pip-audit: 14 dependências, nenhuma vulnerabilidade conhecida retornada na consulta de 02/11/2026. Resultado em `output/evidencias/dependencias.json`; esse resultado é datado e não é uma garantia permanente.
- Revisão em dois eixos: correções de senha e paginação identificadas e tratadas. O tamanho dos handlers e das views continua como oportunidade futura de modularização por domínio.

## Navegador interno do ChatGPT

No ambiente descartável foram observados:

1. Login administrativo, cadastro de bancada e edição de tarifa.
2. Consulta de ingredientes e movimentações reais de consumo.
3. Login do cliente, seleção de prato, alteração explícita de quantidade e atualização do total.
4. Envio do pedido com endereço e observações, e persistência do valor calculado no servidor.
5. Login da cozinha, visualização no KDS, gravação de estimativa, início do preparo, pronto, entrega e histórico.
6. Criação de reserva futura e valor por duração; formulário de reagendamento com horário local preservado.
7. Encerramento da sessão após concluir o pedido.
8. Nenhum erro/warning de console observado no fluxo consultado da cozinha.
9. Paginação com mais de 50 registros e edição do prato correto após abrir e cancelar o formulário de ficha técnica.

Capturas: `output/evidencias/admin-bancada.png`, `cliente-pedido.png` e `cozinha-kds.png`.

## Implantação local pendente

O banco real possui a conta administrativa criada anteriormente, mas o usuário MySQL de runtime não tem CREATE/ALTER. Por isso a nova versão ainda depende da execução administrativa de `backend/database/APLICAR_MIGRACAO.sql`. O script está preparado e um snapshot dos dados anteriores foi salvo em `output/backups/pre-migracao-20261102.json`, fora do Git.

Não foram instaladas triggers nem alteradas as tabelas reais. Após aplicar o SQL com conta administrativa, reiniciar o Flask e executar o smoke test real. Manter a conta de runtime com somente DML.

## Limites

A configuração do workflow ainda precisa executar no GitHub após envio do código. Não foram publicados serviços externos, certificados HTTPS, testes de carga prolongados, certificação WCAG ou comparação pixel a pixel ao Figma. Os testes em VM Node não substituem os testes reais de browser; ambos são descritos separadamente acima. O arquivo Workbench `.mwb` histórico não foi inventado: o esquema final é fornecido em SQL e o dicionário é regenerado a partir dos modelos atuais.
