from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

BASE = Path('Documentação/Documentacao_Sabor_e_Clic_3_Bimestre_Revisada.docx')
OUT = Path('Documentação/Documentacao_Sabor_e_Clic_3_Bimestre_V3_Base_Revisada.docx')

doc = Document(BASE)

# Padroniza a terminologia atual sem desmontar a estrutura original.
def replace_text_in_paragraph(p, replacements):
    for run in p.runs:
        txt = run.text
        for old, new in replacements.items():
            txt = txt.replace(old, new)
        run.text = txt

replacements = {
    'Party': 'Sessão',
    'PARTY': 'SESSÃO',
    'party': 'sessão',
}

for p in doc.paragraphs:
    replace_text_in_paragraph(p, replacements)
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                replace_text_in_paragraph(p, replacements)

# Mantém a documentação anterior integral e acrescenta a atualização consolidada.
doc.add_page_break()

p = doc.add_paragraph()
p.style = doc.styles['Heading 1'] if 'Heading 1' in doc.styles else doc.styles['Normal']
r = p.add_run('ATUALIZAÇÃO DA IMPLEMENTAÇÃO — 3º BIMESTRE')
r.bold = True

p = doc.add_paragraph()
p.add_run(
    'Esta seção atualiza a documentação original com o estado mais recente do projeto, '
    'integrando o protótipo estático do front-end, os scripts JavaScript exigidos no terceiro '
    'bimestre e a estrutura inicial do back-end Flask. O objetivo desta etapa continua sendo '
    'demonstrar arquitetura, fluxos e regras fundamentais com dados simulados, sem antecipar '
    'a integração completa prevista para o quarto bimestre.'
)

# 1. Visão integrada
h = doc.add_heading('1. Visão integrada da implementação atual', level=2)
for text in [
    'A aplicação está organizada em três camadas principais: interface HTML/CSS, lógica de interação em JavaScript e estrutura inicial de back-end em Flask.',
    'No estado atual, o front-end utiliza dados simulados e armazenamento local para demonstrar os fluxos. O back-end define contratos de endpoints e modelos simulados, ainda sem persistência definitiva no banco de dados.',
    'A arquitetura definitiva manterá o mesmo fluxo conceitual: Reserva → Sessão → Cardápio/Carrinho → Pedido → KDS. A integração real entre JavaScript e Flask será feita por Fetch API e JSON no quarto bimestre.'
]:
    doc.add_paragraph(text)

# 2. Front-end
h = doc.add_heading('2. Front-end atual', level=2)
doc.add_paragraph(
    'O front-end está estruturado como uma aplicação multipágina (MPA), com páginas separadas por perfil de usuário. '
    'As telas usam os mesmos componentes visuais e dados simulados para manter consistência entre cliente, cozinha e administração.'
)

def add_bullets(items):
    for item in items:
        p = doc.add_paragraph(style='List Bullet' if 'List Bullet' in doc.styles else 'Normal')
        p.add_run(item)

add_bullets([
    'Acesso: index.html (login simulado).',
    'Cliente: início, bancadas, reservas, sessão, cardápio, carrinho e pedidos.',
    'Cozinha: dashboard, KDS, pedidos, disponibilidade do cardápio/estoque e histórico.',
    'Administrador: dashboard, reservas, bancadas, produtos, ingredientes, substituições, usuários e relatórios.'
])

doc.add_paragraph(
    'Essas páginas funcionam como protótipo navegável da aplicação final e permitem demonstrar os principais fluxos sem depender do banco de dados ou do servidor Flask.'
)

# 3. JavaScript
h = doc.add_heading('3. JavaScript — lógica do 3º bimestre', level=2)
doc.add_paragraph(
    'A lógica JavaScript foi separada por responsabilidade para evitar um arquivo monolítico e tornar explícitos os conteúdos avaliados no terceiro bimestre.'
)

table = doc.add_table(rows=1, cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = 'Table Grid'
for i, text in enumerate(['Arquivo', 'Responsabilidade', 'Conteúdos demonstrados']):
    table.rows[0].cells[i].text = text
rows = [
    ('data.js', 'Dados simulados e estado compartilhado', 'arrays, objetos literais, for...in'),
    ('site.js', 'Navegação, sessão simulada e helpers gerais', 'DOM, localStorage, eventos'),
    ('components.js', 'Componentes visuais reutilizáveis', 'for...of, templates e composição de interface'),
    ('catalog.js', 'Renderização dinâmica e filtros do cardápio', 'forEach, arrays e DOM'),
    ('cart.js', 'Carrinho e cálculos em memória', 'find, filter, reduce, forEach, subtotal e total'),
    ('validation.js', 'Validação da reserva', 'for...of, validação de entradas e feedback ao usuário'),
    ('login.js', 'Login de demonstração', 'validação de formulário e seleção de perfil'),
    ('views.js', 'Registro das telas do protótipo', 'renderização das páginas e dados simulados'),
    ('a11y.js', 'Acessibilidade de interface', 'comportamentos auxiliares e navegação acessível'),
]
for row in rows:
    cells = table.add_row().cells
    for i, val in enumerate(row):
        cells[i].text = val

doc.add_paragraph(
    'Nesta etapa, Fetch API, async/await, tratamento de erros HTTP e classes ES6+ não são necessários para a entrega. '
    'Esses recursos serão utilizados na integração real com o back-end no quarto bimestre.'
)

# 4. Fluxos JS simulados
h = doc.add_heading('4. Fluxos funcionais demonstrados no front-end', level=2)
add_bullets([
    'Cardápio: produtos armazenados em arrays de objetos são renderizados dinamicamente no DOM e podem ser filtrados por categoria.',
    'Carrinho: itens podem ser adicionados e removidos; quantidades, subtotais e valor total são calculados em memória.',
    'Reserva: o formulário executa validações simples antes de apresentar confirmação simulada.',
    'Perfis: o login utiliza contas de demonstração e localStorage para direcionar cliente, cozinheiro e administrador às respectivas áreas.',
    'KDS: a interface demonstra visualmente a fila de pedidos e seus estados, ainda sem sincronização real com o servidor.'
])

# 5. Backend simulado
h = doc.add_heading('5. Back-end Flask simulado', level=2)
doc.add_paragraph(
    'O back-end do terceiro bimestre tem caráter estrutural. Ele demonstra como a aplicação Flask será organizada e quais '
    'endpoints fundamentais existirão, mas utiliza modelos simulados e ainda não realiza persistência definitiva.'
)
add_bullets([
    'run.py: ponto de inicialização do servidor Flask.',
    'config.py: concentra configurações principais da aplicação.',
    'app/__init__.py: criação/configuração inicial da aplicação.',
    'controller/auth_controller.py: exemplos de cadastro, consulta de usuário e login.',
    'controller/reserva_controller.py: consulta de bancadas e criação/consulta de reservas.',
    'controller/pedidos_controller.py: cardápio, criação/consulta de pedidos e consulta do KDS.'
])

# 6. Endpoints
h = doc.add_heading('6. Endpoints fundamentais definidos', level=2)
table = doc.add_table(rows=1, cols=4)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = 'Table Grid'
for i, text in enumerate(['Método', 'Endpoint', 'Finalidade', 'Estado atual']):
    table.rows[0].cells[i].text = text
endpoints = [
    ('POST', '/api/cadastro', 'Cadastrar cliente', 'Simulado'),
    ('GET', '/api/cadastro/<id>', 'Consultar usuário por ID', 'Simulado'),
    ('POST', '/api/login', 'Validar login', 'Simulado'),
    ('GET', '/api/bancadas', 'Listar bancadas', 'Simulado'),
    ('POST', '/api/reservas', 'Criar reserva', 'Simulado'),
    ('GET', '/api/reservas/<id>', 'Consultar reserva', 'Simulado'),
    ('GET', '/api/cardapio', 'Obter cardápio', 'Simulado'),
    ('POST', '/api/pedido/cadastro', 'Criar pedido vinculado à reserva', 'Simulado'),
    ('GET', '/api/pedido/<id>', 'Consultar pedido', 'Simulado'),
    ('GET', '/api/kds/<id>', 'Obter representação do pedido para o KDS', 'Simulado'),
]
for row in endpoints:
    cells = table.add_row().cells
    for i, val in enumerate(row):
        cells[i].text = val

# 7. Integração conceitual
h = doc.add_heading('7. Integração entre os sistemas', level=2)
doc.add_paragraph(
    'Mesmo com front-end e back-end ainda simulados, os dois lados foram organizados para representar o mesmo domínio. '
    'O front-end já apresenta as telas e ações que futuramente chamarão os endpoints Flask, enquanto o back-end define '
    'os contratos básicos correspondentes.'
)

flow = [
    '1. O cliente seleciona uma bancada e informa os dados da reserva.',
    '2. A reserva representa o vínculo entre cliente, bancada e período de uso.',
    '3. A reserva dá acesso a uma Sessão, que será o contexto de uso durante o período reservado.',
    '4. Na Sessão, o cliente consulta o cardápio e monta o carrinho.',
    '5. Ao finalizar, o pedido é criado associado à reserva/sessão.',
    '6. O pedido passa a ser exibido no KDS do cozinheiro.',
    '7. No sistema completo, alterações de estado feitas no KDS serão persistidas no back-end e refletidas no front-end.'
]
for item in flow:
    doc.add_paragraph(item)

# 8. Contratos futuros
h = doc.add_heading('8. Contratos previstos para a integração no 4º bimestre', level=2)
doc.add_paragraph(
    'A implementação atual evita criar uma API descartável. Os dados simulados já seguem uma estrutura próxima da versão final, '
    'permitindo substituir gradualmente os mocks por requisições HTTP.'
)
add_bullets([
    'Reserva: cliente, bancada, data, horário e quantidade de pessoas.',
    'Pedido: identificador da reserva/sessão e lista de itens com quantidade.',
    'Cardápio: identificador, nome, categoria, descrição, preço e disponibilidade.',
    'KDS: pedido, itens, bancada/sessão, horário e estado de preparo.'
])

# 9. Segurança
h = doc.add_heading('9. Segurança na etapa atual', level=2)
doc.add_paragraph(
    'O login e o controle de perfis atuais têm função exclusivamente demonstrativa e utilizam localStorage. '
    'Eles não representam autenticação segura. No quarto bimestre, a autenticação será transferida para Flask, '
    'com sessões/cookies, controle de acesso por perfil (RBAC), validação também no servidor e consultas parametrizadas ao banco.'
)

# 10. Atendimento aos requisitos
h = doc.add_heading('10. Atendimento aos requisitos do 3º bimestre', level=2)
table = doc.add_table(rows=1, cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = 'Table Grid'
for i, text in enumerate(['Requisito', 'Situação', 'Evidência']):
    table.rows[0].cells[i].text = text
reqs = [
    ('DER conceitual', 'Concluído', 'Documentação existente e arquivo do brModelo'),
    ('Dicionário de dados', 'Concluído', 'Documento específico na pasta Documentação'),
    ('Protótipo e páginas principais', 'Concluído', 'FrontEnd com áreas de cliente, cozinha e administrador'),
    ('Cardápio digital', 'Concluído como protótipo funcional', 'cliente_cardapio.html + catalog.js'),
    ('KDS', 'Concluído como protótipo visual', 'cozinha_kds.html / views.js'),
    ('Arrays e objetos literais', 'Concluído', 'data.js'),
    ('for...of / for...in / forEach', 'Concluído', 'components.js, data.js, catalog.js/cart.js'),
    ('Manipulação dinâmica do DOM', 'Concluído', 'catalog.js e scripts de interface'),
    ('Validação de formulários', 'Concluído em nível inicial', 'validation.js e login.js'),
    ('Cálculos em memória', 'Concluído', 'cart.js'),
    ('Estrutura Flask', 'Concluída em nível inicial', 'run.py, config.py e app'),
    ('Endpoints fundamentais', 'Concluídos como exemplos simulados', 'controllers do back-end'),
    ('Integração JS ↔ Flask', 'Planejada para o 4º bimestre', 'Fetch/JSON ainda não conectados'),
]
for row in reqs:
    cells = table.add_row().cells
    for i, val in enumerate(row):
        cells[i].text = val

# 11. Estado final da etapa
h = doc.add_heading('11. Estado da primeira entrega e próximos passos', level=2)
doc.add_paragraph(
    'Ao final do terceiro bimestre, o projeto possui modelagem de dados, identidade e protótipos das interfaces, '
    'uma aplicação front-end navegável com lógicas JavaScript fundamentais e uma estrutura de back-end Flask que '
    'define os principais contratos do sistema. A etapa seguinte substituirá progressivamente os dados simulados por '
    'persistência real, integrará o front-end ao Flask por Fetch API e aplicará autenticação, autorização e regras de negócio completas.'
)

# Normalização leve apenas nos novos parágrafos não tabelares, sem tocar imagens.
for p in doc.paragraphs:
    if p.text.startswith('ATUALIZAÇÃO DA IMPLEMENTAÇÃO'):
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

# Salvar preservando o pacote DOCX original e seus recursos incorporados.
doc.save(OUT)
print(OUT)
