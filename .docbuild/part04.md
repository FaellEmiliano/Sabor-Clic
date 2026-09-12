As bancadas representam os espaços físicos que podem ser reservados. Os dados simulados incluem nome, capacidade, preço, status, recursos disponíveis e imagem. O cliente consulta essas informações antes de iniciar o fluxo de reserva.

A reserva associa o cliente a uma bancada e a um período. No desenho funcional do Sabor & Clic, uma reserva ativa disponibiliza uma Sessão. A Sessão é o ambiente de uso durante o período reservado e concentra os pedidos, consumo e acompanhamento da experiência.

Embora o back-end simulado atual trabalhe diretamente com id_reserva na criação do pedido, essa escolha já é compatível com a regra de negócio: a reserva é a origem do contexto da Sessão. A versão final poderá manter a sessão como entidade explícita ou derivá-la da reserva ativa, conforme a modelagem consolidada.

# 16. SEGURANÇA

A versão atual possui mecanismos de segurança apenas em nível de protótipo. O front-end identifica perfis usando localStorage e impede navegação casual para páginas de outro perfil por redirecionamento. Esse comportamento não é considerado autenticação real e não deverá ser usado como proteção definitiva.

O back-end possui estrutura de configuração para SECRET_KEY e exemplos de login/cadastro, mas o fluxo final de autenticação, sessão, cookies e autorização ainda será implementado. Na versão definitiva, o servidor deverá ser a fonte de verdade para as permissões.

• Sessões Flask/cookies seguros.

• Hash de senha e armazenamento seguro.

• RBAC para Cliente, Cozinheiro e Administrador.

• Validação de todas as entradas no servidor.

• Consultas SQL parametrizadas.

• Proteção das rotas administrativas e do KDS.

• Sanitização e prevenção de vulnerabilidades comuns.

# 17. ESTADO ATUAL DA IMPLEMENTAÇÃO

| Área | Estado | Observação |

| --- | --- | --- |

| Protótipo MPA | Implementado | 21 páginas internas + login, com navegação real. |

| Design e componentes | Implementado no protótipo | Interface completa para os três perfis. |

| Dados de demonstração | Implementado | Produtos, bancadas, perfis, pedidos e indicadores simulados. |

| Cardápio dinâmico | Implementado no front-end | DOM + filtros por categoria. |

| Carrinho | Implementado no front-end | Adicionar, remover, quantidade e total; persistência local. |

| Validação de reserva | Implementado no front-end | Validação demonstrativa. |

| Login por perfil | Implementado como simulação | LocalStorage; não é autenticação real. |

| Estrutura Flask | Parcial / simulada | Controllers e contratos de endpoints. |

| Banco de dados em execução | Planejado | Modelagem pronta; persistência final fica para próxima etapa. |

| Fetch API entre front e Flask | Planejado | Integração do 4º bimestre. |

| Autenticação segura/RBAC no servidor | Planejado | Será implementado no back-end definitivo. |



# 18. ATENDIMENTO AOS REQUISITOS DO 3º BIMESTRE

| Requisito | Situação | Evidência/abordagem |

| --- | --- | --- |

| DER | Concluído | DER_saborclic.png. |

| Dicionário de dados | Concluído | Dicionario_de_Dados_Sabor_e_Clic. |

| Protótipo / telas | Concluído | MPA com áreas Cliente, Cozinha e Admin. |

| Cardápio Digital | Concluído no protótipo | cliente_cardapio.html + catalog.js. |

| KDS | Concluído no protótipo | cozinha_kds.html. |

| Arrays e objetos JS | Concluído | data.js e módulos de lógica. |

| forEach | Concluído | catalog.js e cart.js. |

| for...of | Concluído | validation.js e components.js. |

| for...in | Concluído | Busca de perfil em objeto de usuários. |

| Manipulação do DOM | Concluído | catalog.js, site.js e renderização das páginas. |

| Validação de formulários | Concluído | validation.js e login.js. |

| Cálculos em memória | Concluído | cart.js. |

| Estrutura Flask | Parcial / adequada ao escopo | run.py, config.py, app e controllers. |

| Rotas fundamentais | Representadas como contratos simulados | Controllers de autenticação, reserva, pedido e KDS. |

| JSON / integração inicial | Planejada no contrato | Dados estruturados preparados; Fetch real fica para o 4º bi. |

| Segurança / RBAC | Planejado e documentado | Separação de perfis no protótipo + estratégia de servidor definida. |



# 19. PRÓXIMOS PASSOS PARA O 4º BIMESTRE

• Registrar as rotas Flask reais e padronizar respostas JSON.

• Implementar os models de acesso ao banco de dados.

• Criar o banco físico e sincronizá-lo com DER/MER/dicionário.

• Substituir dados simulados do front-end por requisições Fetch API.

• Implementar classes ES6+ onde forem úteis para o domínio do front-end.

• Adicionar async/await e tratamento de erros nas operações HTTP.

