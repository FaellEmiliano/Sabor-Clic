# Modelo relacional final

A reserva pode existir sem sessão; um prato pode existir sem vendas. As tabelas de segurança e movimentações integram o esquema final. Triggers não são utilizadas.

```mermaid
erDiagram
    usuario ||--o| cliente : especializa
    usuario ||--o| cozinheiro : especializa
    usuario ||--o| administrador : especializa
    cliente ||--o{ reserva : solicita
    bancada ||--o{ reserva : utiliza
    reserva ||--o| sessao : gera_no_checkin
    sessao ||--o{ pedido : origina
    pedido ||--|{ item_pedido : possui
    prato ||--o{ item_pedido : referencia
    prato ||--o{ ficha_tecnica : receita
    ingrediente ||--o{ ficha_tecnica : compoe
    ingrediente ||--o{ ingrediente_substituicao : original
    ingrediente ||--o{ ingrediente_substituicao : substituto
    usuario ||--o{ sessao_autenticacao : autentica
    usuario o|--o{ evento_auditoria : registra
    ingrediente ||--o{ movimentacao_estoque : saldo
    ingrediente o|--o{ movimentacao_estoque : original_consumido
    pedido o|--o{ movimentacao_estoque : consome_ou_estorna
    bancada {
        int id_bancada PK
        string nome
        string descricao
        decimal valor_hora
        boolean ativa
    }
    ingrediente {
        int id_ingrediente PK
        string nome
        string unidade_medida
        decimal quantidade_estoque
    }
    limite_acesso {
        string chave PK
        datetime inicio
        int tentativas
    }
    prato {
        int id_prato PK
        string nome
        string descricao
        decimal preco
        boolean ativo
    }
    usuario {
        int id_usuario PK
        string nome
        string email
        boolean ativo
        string senha_hash
    }
    administrador {
        int id_usuario PK, FK
    }
    cliente {
        int id_usuario PK, FK
        string endereco_entrega
    }
    cozinheiro {
        int id_usuario PK, FK
        string turno
        string especialidade
    }
    evento_auditoria {
        int id_evento PK
        int id_usuario FK
        datetime criado_em
        string acao
        string recurso
        int resultado
        string correlacao
    }
    ficha_tecnica {
        int id_prato PK, FK
        int id_ingrediente PK, FK
        decimal quantidade_necessaria
    }
    ingrediente_substituicao {
        int id_ingrediente_original PK, FK
        int id_ingrediente_substituto PK, FK
        int prioridade
        decimal fator_conversao
    }
    sessao_autenticacao {
        string id_sessao_auth PK
        int id_usuario FK
        string versao_senha
        datetime criado_em
        datetime ultimo_acesso
        datetime expira_em
        boolean revogada
    }
    reserva {
        int id_reserva PK
        int id_cliente FK
        int id_bancada FK
        datetime inicio
        datetime fim
        string status
        decimal valor_total
        datetime criado_em
    }
    sessao {
        int id_sessao PK
        int id_reserva FK
        string codigo_acesso
        string status
        datetime criado_em
        datetime iniciado_em
        datetime encerrado_em
    }
    pedido {
        int id_pedido PK
        int id_sessao FK
        string status
        decimal valor_total
        int tempo_estimado
        string endereco_entrega
        string chave_idempotencia
        string hash_requisicao
        string observacoes
        datetime preparo_em
        datetime pronto_em
        datetime entregue_em
        datetime cancelado_em
        datetime criado_em
    }
    item_pedido {
        int id_item_pedido PK
        int id_pedido FK
        int id_prato FK
        string nome_prato
        int quantidade
        decimal preco_unitario
        decimal subtotal
    }
    movimentacao_estoque {
        int id_movimentacao PK
        int id_ingrediente FK
        int id_ingrediente_original FK
        int id_pedido FK
        string tipo
        decimal quantidade
        string chave_evento
        datetime criado_em
    }
```

Os campos, tipos e restrições completos estão em Dicionario_final.pdf e 01_modelo_fisico.sql. A cardinalidade mínima de um item por pedido é assegurada pelo checkout transacional; a FK por si só não obriga a existência de filhos. A criação de um único perfil por conta é assegurada pelo fluxo da API, sem triggers de exclusividade entre especializações.