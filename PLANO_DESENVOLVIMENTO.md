# Estado do desenvolvimento e plano de conclusão

> Atualização da execução: as etapas de segurança, fluxo, SQL aditivo, estoque transacional, POO, testes, revisão e documentação foram implementadas após esta auditoria. Triggers foram excluídas por instrução do usuário. O texto abaixo preserva o diagnóstico original; o estado atual está em README.md, VERIFICACAO.md e Documentação/final. A aplicação no MySQL real aguarda execução administrativa de APLICAR_MIGRACAO.sql, pois a conta de runtime não tem DDL.

Auditoria de 02/11/2026, branch local `backend`, base versionada `d542e8b`, incluindo as mudanças locais ainda não commitadas. Este documento registra uma análise; não implementa as pendências listadas.

## Diagnóstico

O projeto está em **MVP integrado, com implementação e validação ainda incompletas para a entrega do quarto bimestre**. Já existe comunicação frontend → Flask → banco e um fluxo básico de reserva → sessão → pedido → cozinha. Isso não equivale a cumprir todos os requisitos acadêmicos ou a estar pronto para produção.

O principal trabalho restante está em quatro frentes: estoque/triggers/SQL, POO obrigatória no JavaScript, segurança com evidências e homologação visual/funcional. A revisão anterior focou a integração e não esgotou esses requisitos; esta auditoria corrige essa visão de escopo.

## Cobertura da análise

- Inventário de 109 arquivos do projeto, sem `.git`, ambiente virtual, bytecode ou conteúdo do `.env`.
- Mapa de 91 arquivos relevantes: 58 de código, 27 documentos/interfaces, quatro PDFs e dois diagramas. Imagens decorativas foram inventariadas, sem tratá-las como regras de negócio.
- Leitura dos quatro PDFs, totalizando 78 páginas, e inspeção visual de DER/MER.
- Inspeção de configuração, SQL, models, rotas ativas e antigas, controllers, scripts JS, HTMLs, CSS, assets, testes, dependências e documentação Markdown.
- Testes automatizados e reproduções adicionais em SQLite descartável. No MySQL real, somente consultas de leitura durante esta auditoria.
- Não foi validada fidelidade pixel a pixel ao Figma nem completada a operação de todos os formulários em navegador real. O login administrativo e a abertura do Dashboard foram observados no navegador interno antes da interrupção do teste.

Arquivos de apoio: `tmp/auditoria/inventario.json`, textos dos PDFs em `tmp/auditoria/`, `graphify-out/graph.html`, `graphify-out/graph.json` e `graphify-out/GRAPH_REPORT.md`.

## Fontes e interpretação

| Fonte local | Referências relevantes | Uso nesta análise |
| --- | --- | --- |
| [Enunciado](D:/Sabor-Clic/Documentação/Versão2_ProjetoIntegrador31082026.pdf) | pp. 2–5 | Requisitos acadêmicos, arquitetura, POO JS, entrega SQL e datas |
| [Documentação do terceiro bimestre](D:/Sabor-Clic/Documentação/Documentacao_Sabor_e_Clic_3_Bimestre.pdf) | pp. 12–16, 23–29, 41–44 | Regras de domínio, protótipo e próximos passos; descreve uma versão histórica |
| [Plano de segurança](D:/Sabor-Clic/Documentação/Seguranca_Sabor_e_Clic_3_Bimestre_ABNT.pdf) | pp. 4–14 | Matriz alvo, validação, OWASP, logout, auditoria e evidências previstas |
| [Dicionário](D:/Sabor-Clic/Documentação/Dicionario_de_Dados_Sabor_e_Clic.pdf) | pp. 10–13 | Consistência, substituições e decisões de cardinalidade |
| [README atual](D:/Sabor-Clic/README.md) e [verificação anterior](D:/Sabor-Clic/VERIFICACAO.md) | versão local | Contratos da integração atual e limites já declarados |

Os PDFs do terceiro bimestre não provam o estado atual do código. Algumas promessas desses PDFs precisam ser implementadas; outras precisam ser formalmente revistas. Não se deve acrescentar funcionalidades só porque apareceram como ilustração no protótipo.

## Onde estamos

| Área | Estado | Evidência e limite |
| --- | --- | --- |
| Inicialização e persistência | Implementadas | Flask inicia, 13 tabelas mapeadas, MySQL acessível; testes de escrita usam SQLite |
| API ativa | Implementada | Um Blueprint `api`, com 29 padrões de URL; rotas em `backend/app/routes/api_routes.py` |
| Autenticação | Parcial | Hash, cookie, CSRF, papéis e isolamento; faltam revogação efetiva no logout e limitação de tentativas |
| Frontend integrado | Implementado no fluxo básico | 21 telas autenticadas mais login/cadastro usam Fetch; não há classes ES6 de domínio |
| Reservas | Parcial | Criar, consultar, cancelar, reagendar e impedir conflitos; PATCH ainda aceita passado |
| Sessões | Implementadas no fluxo básico | Início dentro da janela, código gerado e encerramento condicionado aos pedidos; política de expiração operacional precisa ser definida |
| Pedidos | Parcial | Criação atômica, quantidade positiva e preço oficial; não verifica/baixa ingredientes e não tem idempotência |
| KDS | Parcial | Estados recebido → em preparo → pronto → entregue e polling; falta UI de tempo estimado, prioridades e histórico temporal completo |
| CRUD administrativo | Implementado no fluxo básico | Usuários, bancadas, pratos, ingredientes, fichas e substituições; operação de todos os formulários ainda precisa de homologação visual |
| Estoque e substituições | Cadastro implementado | Não há motor de consumo, movimentações ou aplicação das regras cadastradas |
| SQL da entrega | Incompleto | Só há `backend/database/SCHEMA.sql`; faltam os quatro scripts exigidos e dados mínimos |
| Relatórios | Parcial | Totais acumulados e receitas concluídas; sem consultas analíticas SQL de entrega, filtros por período, ticket/tempo médio e desempenho por bancada |
| Segurança e implantação | Parcial | Algumas proteções no servidor; faltam evidências OWASP, auditoria, configuração estável e roteiro de implantação |
| Documentação e entrega | Parcial | Material histórico existe; falta documentação final correspondente ao comportamento atual e itens referidos mas não presentes |

No MySQL real, a auditoria encontrou um usuário administrador e nenhum cliente, cozinheiro, bancada, prato, ingrediente, reserva ou pedido. Foram encontradas **zero triggers** no esquema. `SECRET_KEY` não está configurada no ambiente carregado: a aplicação usa a chave aleatória temporária prevista no código.

## Pendências confirmadas por reprodução

Executadas sem alterar dados reais. O script [reproduzir_limites.py](D:/Sabor-Clic/tmp/auditoria/reproduzir_limites.py) reproduz os quatro casos abaixo:

| Caso | Resultado atual | Resultado necessário |
| --- | --- | --- |
| Guardar cópia de um cookie autenticado, fazer logout e reutilizar a cópia | `/api/me` responde 200 | A sessão revogada deve responder 401; limpar o cookie do navegador não basta |
| Reagendar uma reserva confirmada para início e fim no passado | PATCH responde 200 | Rejeitar o período no backend, assim como ocorre na criação |
| Pedir prato com ficha técnica cujo ingrediente está com saldo zero | POST responde 201 | Aplicar a política de estoque/substituição e rejeitar ou atender com substituto válido de forma transacional |
| Reenviar o mesmo checkout | POST responde 201 com novo pedido | Reenvio da mesma operação deve ser reconhecido por chave de idempotência; pedidos intencionalmente iguais continuam permitidos |

Referências de código: `controllers/http.py::protect`, `routes/api_routes.py::logout`, `controllers/operacao_controller.py::reserve` e `::checkout`.

Outros pontos encontrados por inspeção:

- Login/cadastro sem limitação de tentativas ou eventos estruturados de segurança.
- As operações são registradas apenas pelos logs básicos do servidor; não há trilha de quem alterou pedido, estoque, usuário ou reserva.
- Regras de estoque não são protegidas no SQL: `ingrediente.quantidade_estoque` não possui CHECK de não negatividade. Outros valores monetários também dependem da validação da API, sem CHECK correspondente no dump.
- O backend suporta `tempo_estimado` e cancelamento administrativo de pedido, mas a interface atual não fornece controles para essas ações. O checkout não oferece endereço específico do pedido.
- Não há registros de início/fim de preparo por transição; portanto tempo médio histórico não pode ser calculado de forma fiel apenas com `criado_em` e o status final.
- A listagem de bancadas mostra atividade do cadastro, não disponibilidade por intervalo escolhido.
- Cada página carrega todos os recursos do seu perfil; administradores fazem dez consultas HTTP por carregamento/polling. Listagens e filtros carregam o conjunto inteiro antes de filtrar; não há paginação. `order_json` faz consultas adicionais por pedido/item.
- Há dez módulos antigos de rotas e dez controllers de entidade que não participam da API registrada. Mantê-los junto da implementação ativa torna manutenção e avaliação arquitetural confusas.
- Parte da regra de negócio e do CRUD está diretamente em `api_routes.py`, além de existir uma segunda camada de controllers antiga. A arquitetura MVC exigida precisa ficar clara e coerente.
- `catalog.js` é um arquivo sem comportamento, mas ainda é carregado no cardápio. Há funções/utilitários e estilos ligados a componentes antigos a revisar.
- `a11y.js` tem controles úteis, mas seu `JSON.parse` inicial não trata dados locais corrompidos. Não há laudo de teclado, contraste, foco e responsividade.
- Não há pipeline de CI, migrações versionadas, auditoria datada de dependências, rotina de backup/restauração ou configuração de servidor de produção no repositório.

## Requisitos formais ainda não atendidos

### JavaScript

O enunciado, p. 3, exige classes ES6+, herança, métodos estáticos e atributos privados `#`. O código atual usa funções e objetos; Fetch/async/await/try/catch já estão presentes, mas não substituem POO.

Plano: introduzir classes com responsabilidade real, como `Usuario`, `Prato`, `ItemPedido`, `Carrinho` e `Pedido`; preservar dados privados e expor métodos de alteração. Usar herança somente com uma relação de domínio justificável e demonstrável, sem criar classes vazias para cumprir rubrica. Separar entidades, API, estado e renderização. Cobrir totais/quantidades/serialização com testes e manter os contratos HTTP existentes.

### Banco de dados

O enunciado, p. 5, pede:

1. `01_modelo_fisico.sql`: tabelas, PK/FK/CHECK/índices escritos e versionados.
2. `02_insercoes_basicas.sql`: dados mínimos coerentes para demonstrar os três perfis e o fluxo completo, sem credenciais reais fixadas no projeto.
3. `11_queries_relatorios.sql`: consultas de vendas, estoque e ocupação.
4. `20_triggers.sql`: automação de regras de negócio e baixa de estoque.

O plano de segurança, p. 4, descreve SQL escrito pela equipe, sem geração automática do esquema por ORM. Atualmente `init-db` usa `db.create_all()`. É necessário alinhar a inicialização ao compromisso documentado. O uso de SQLAlchemy para mapear/acessar tabelas é uma decisão distinta de usar ORM como única fonte de DDL.

Não executar o dump atual sobre dados reais: ele contém `DROP TABLE`. A evolução deve ter scripts revisados e estratégia de migração/backup.

### Divergências do dicionário para o modelo físico

São propostas históricas a reconciliar, não alterações que devam ser aplicadas cegamente:

| Campo | Dicionário PDF | Models/dump atuais |
| --- | --- | --- |
| Usuário: nome / e-mail | VARCHAR(150) / VARCHAR(254) | VARCHAR(120) / VARCHAR(180) |
| Cozinheiro: turno | VARCHAR(30) | VARCHAR(50) |
| Prato: nome | VARCHAR(100) | VARCHAR(120) |
| Ingrediente: nome / unidade | VARCHAR(100) / VARCHAR(10) | VARCHAR(120) / VARCHAR(30) |
| Código de sessão | VARCHAR(128) | VARCHAR(100) |
| Fator de substituição | DECIMAL(12,6) | DECIMAL(10,4) |
| Estados | Propostas como AGUARDANDO, EM_USO e CRIADA; VARCHAR(20) | recebido, em_andamento e criação diretamente ativa; VARCHAR(40) |

Os testes de mapeamento comparam models com o dump SQL, portanto não detectam essas divergências documentais. Depois de aprovar o contrato final, atualizar os três artefatos de forma conjunta.

### Documentação e artefatos

A documentação histórica declara DOCX do dicionário e arquivo `EER_saborclic.mwb`; eles não foram localizados no inventário. Também não foi localizada uma apresentação final. Isso significa ausência no repositório, não prova de que os integrantes não os possuam em outro lugar.

É preciso produzir a documentação final ABNT, atualizar matriz de permissões e endpoints, registrar evidências OWASP e dos testes, revisar DER/MER/dicionário e montar apresentação/roteiro de demonstração. O repositório ainda tem alterações locais não commitadas, inclusive a integração; esse estado ainda não é reproduzível a partir do último commit sozinho.

## Decisões de domínio antes de ampliar o modelo

1. **Consumo de estoque:** definir o evento de baixa (confirmação/aceite/preparo), reversão em cancelamento e comportamento de retries. Triggers e Python não podem descontar o mesmo consumo duas vezes.
2. **Substituições:** definir algoritmo por prioridade, fator/unidade e disponibilidade; decidir como registrar o ingrediente efetivamente consumido e eventuais ciclos. Uma tabela de movimentações pode ser necessária, mas deve ser refletida no DER/dicionário.
3. **Reserva–sessão:** o DER indica 1:1 obrigatório nos dois lados; o fluxo atual deixa a reserva sem sessão até o check-in. Alinhar cardinalidade para reserva com zero/uma sessão ou criar sessão pendente na reserva.
4. **Prato–item:** permitir cadastrar pratos ainda não vendidos; o mínimo de um item no DER precisa ser revisto conforme já apontado no próprio dicionário.
5. **Perfis:** decidir se cada usuário pode ter um ou vários perfis. Há três tabelas de especialização e a API escolhe um papel por precedência; a exclusividade não é garantida no banco.
6. **Protótipo versus esquema:** capacidade/pessoas, categorias/imagens, observações e estoque mínimo aparecem em partes da documentação/interface histórica, mas não nos models atuais. Confirmar quais entram na entrega e atualizar modelo/interface/documentação juntos.
7. **Acesso público:** a matriz de segurança prevê consulta pública de bancadas/cardápio; a API atual exige login. Escolher e documentar uma única política.
8. **Encerramento:** definir tratamento de sessão expirada, reserva não comparecida e atendimento com múltiplas sessões abertas por cliente. Definir o uso real de `codigo_acesso`.

Não encontrei cobrança online, gateway de pagamento, emissão fiscal ou envio de notificações como bloqueadores explícitos do núcleo exigido pelo enunciado. Não os priorizaria antes dos itens obrigatórios acima.

## Ordem de execução proposta

| Etapa | Prioridade | Trabalho | Critério de conclusão |
| --- | --- | --- | --- |
| 1 — Corrigir segurança e bordas | P0 | Revogar sessão no servidor; rate limit; chave persistente; reagendamento futuro; proteção contra reenvio; logs sem segredos | Reproduções passam a 401/400; retry não cria pedido extra; eventos e limitação são demonstráveis |
| 2 — Fechar regras do modelo | P0 | Resolver as oito decisões acima e registrar o desenho aprovado | DER/MER/dicionário e contrato operacional não se contradizem |
| 3 — Implementar SQL e estoque | P0 | Quatro scripts; CHECKs; dados mínimos; movimentações se aprovadas; consumo/substituição/triggers em transação | Pedido consome exatamente o necessário uma vez; falta de saldo não deixa pedido parcial; cancelamento segue política; concorrência verificada em MySQL isolado |
| 4 — POO e arquitetura | P0 acadêmico | Classes JS obrigatórias, encapsulamento, herança justificável e estáticos; consolidar rotas/controllers ativos | Rubrica ES6 demonstrável, sem regressão de fluxo; caminho MVC único e compreensível |
| 5 — Completar operação e UI | P1 | Tempo estimado, cancelamento administrativo, endereço se no escopo; filtros/disponibilidade; métricas SQL e histórico temporal; fidelidade ao protótipo aprovado | Cada ação prevista possui tela, validação e persistência correspondente |
| 6 — Homologar | P0 de entrega | Navegador real nos três perfis, formulários, erros, mobile/teclado; MySQL concorrente, rollback, triggers, restore e auditoria de dependências | Evidências reproduzíveis, sem erros de console; duas reservas simultâneas não coexistem; estoque não fica negativo |
| 7 — Fechar entrega | P0 de entrega | PDFs finais, apresentação, SQL, roteiro, README e commits dos integrantes | Checkout limpo instala e executa; artefatos coincidem com o código demonstrado |

Paginação, otimização de consultas/polling, recuperação de senha e configuração de implantação vêm depois de assegurar os requisitos de negócio e da disciplina, salvo se a avaliação exigir publicação.

## Prazos encontrados nos documentos

O enunciado local registra **03/11 para Segurança**, **07/11/2026 às 23h55 para a entrega final**, e apresentações da turma 213 em **12/11 e 19/11** (turma 231: 10/11 e 17/11). São as datas do documento de 31/08, não uma confirmação de que o professor não as atualizou.

Considerando a data desta auditoria, a sequência sugerida é priorizar as evidências de segurança para 03/11; fechar SQL/estoque e POO antes de polir funcionalidades extras; reservar a etapa final para MySQL/navegador, documentação e empacotamento. Isso é priorização por dependências, não promessa de prazo de implementação.

## Evidências e limites

- Reexecução nesta auditoria: **26 testes Python passaram**; **3 testes JS de datas passaram**; sintaxe dos scripts JS passou.
- Reexecução do teste integrado: **1 teste passou**, exercitando o JavaScript real das 21 telas, HTTP, SQLite descartável, checkout, etapas do pedido e escape de conteúdo.
- O teste integrado usa DOM mínimo em VM Node. Não equivale a 21 testes de navegador e não cobre os eventos de todos os formulários.
- Os quatro casos de borda acima foram reproduzidos separadamente; ainda não fazem parte da suíte de regressão atual. Testes existentes passando não demonstram sua correção.
- MySQL real: conexão, contagens, presença de tabelas e ausência de triggers verificadas por leitura. Não houve teste de concorrência ou gravação de negócio nesse banco.
- Mapa auxiliar: 751 nós, 1.617 arestas e 38 comunidades. Os pontos centrais incluem `get`, `fail`, CRUD/modelos e o roteador; um vínculo relevante liga o consumo previsto no dicionário à ausência reconhecida no README. O grafo inclui código legado e não representa somente caminhos ativos.
- Diagnóstico do mapa: 83 referências sem definição no corpus, uma autoaresta e 42 colapsos por par em grafo não direcionado; SQL foi analisado diretamente porque falta o parser opcional. Essas limitações estão em `GRAPH_HEALTH.json`; conclusões desta auditoria foram verificadas nos arquivos e testes, não inferidas só pelo grafo.
- Uso de tokens da extração semântica não é disponibilizado pelas ferramentas; zeros nos metadados não são medição de custo.

## Próximo bloco recomendado

Começar pela etapa 1, criando testes de regressão para logout revogado e reagendamento no passado, e fechando as decisões de consumo/estorno antes de escrever triggers. Em seguida executar SQL/estoque e POO como prioridades obrigatórias da entrega. Nenhuma alteração adicional no sistema foi feita por esta auditoria.
