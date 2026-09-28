<div align="center">

<img src="docs/banner.png" width="100%" alt="La Piazza Banner">

# 🍕 La Piazza

### Sistema Web de Gerenciamento para Pizzaria

<p>
Uma plataforma completa para gerenciamento de cardápio, estoque, pedidos e administração de uma pizzaria moderna.
</p>

<br>

<img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/Django-6.0-green?style=for-the-badge&logo=django">
<img src="https://img.shields.io/badge/SQLite-Database-lightgrey?style=for-the-badge&logo=sqlite">
<img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge">

</div>

---

# 🍕 Sobre o Projeto

O **La Piazza** é um sistema web desenvolvido para gerenciamento interno de uma pizzaria, permitindo controlar diferentes setores da operação através de uma única plataforma.

O projeto foi desenvolvido utilizando o framework **Django**, seguindo uma arquitetura organizada baseada no padrão **MVT (Model - View - Template)**.

A aplicação busca representar um ambiente real de gerenciamento, oferecendo recursos para:

- 🍕 Controle do cardápio;
- 📦 Gerenciamento de estoque;
- 🛒 Controle de pedidos;
- 👥 Administração de usuários;
- 🔐 Controle de acesso e permissões;
- 📊 Dashboard administrativo com indicadores.

---

# 🎯 Objetivo do Projeto

O objetivo principal é desenvolver uma solução capaz de organizar os processos internos de uma pizzaria, reduzindo controles manuais e centralizando informações importantes para administração do negócio.

Através do sistema, funcionários e administradores conseguem visualizar, cadastrar, editar e controlar informações essenciais para o funcionamento da empresa.

---

# ✨ Funcionalidades

## 🔐 Autenticação e Usuários

O sistema possui controle de usuários com:

- Cadastro de contas;
- Login e logout;
- Controle de permissões;
- Área administrativa protegida;
- Gerenciamento através do Django Admin.

---

# 🍕 Módulo de Cardápio

Responsável pelo gerenciamento dos produtos oferecidos pela pizzaria.

Funcionalidades:

✅ Cadastro de categorias de pizza;  
✅ Cadastro de pizzas;  
✅ Edição e exclusão de produtos;  
✅ Controle de informações do cardápio;  
✅ Organização dos produtos por categorias.

---

# 📦 Módulo de Estoque

Permite controlar os ingredientes e materiais utilizados pela pizzaria.

Funcionalidades:

✅ Cadastro de categorias de estoque;  
✅ Cadastro de itens;  
✅ Controle de quantidade disponível;  
✅ Registro de movimentações;  
✅ Organização dos produtos armazenados.

---

# 🛒 Módulo de Pedidos

Responsável pelo controle dos pedidos realizados.

Funcionalidades:

✅ Cadastro de pedidos;  
✅ Controle de status;  
✅ Associação de produtos;  
✅ Organização dos atendimentos;  
✅ Controle administrativo.

---

# 📊 Dashboard Administrativo

O sistema possui um painel administrativo com informações importantes para acompanhamento da operação.

Inclui:

- Indicadores gerais;
- Informações de pedidos;
- Dados do estoque;
- Visualização administrativa;
- Gráficos e elementos interativos.

---

# 🛠️ Tecnologias Utilizadas

## Backend

| Tecnologia | Descrição |
|---|---|
| Python | Linguagem principal |
| Django | Framework web |
| Django ORM | Comunicação com banco de dados |
| SQLite | Banco de dados utilizado |
| Django Admin | Administração do sistema |

---

## Frontend

| Tecnologia | Descrição |
|---|---|
| HTML5 | Estrutura das páginas |
| CSS3 | Estilização da interface |
| JavaScript | Interações e componentes dinâmicos |
| Bootstrap/CSS personalizado | Responsividade e design |

---

## Ferramentas

| Ferramenta | Utilização |
|---|---|
| Git | Controle de versão |
| GitHub | Hospedagem do código |
| Graphviz | Criação dos diagramas do banco |
| VS Code | Desenvolvimento |

---

# 🏗️ Arquitetura do Sistema

O projeto utiliza o padrão arquitetural **MVT (Model - View - Template)** do Django.

Estrutura principal:

```
La_Piazza
│
├── cardapio
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates
│
├── estoque
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates
│
├── pedidos
│   ├── models.py
│   ├── views.py
│   └── templates
│
├── usuarios
│   ├── autenticação
│   └── permissões
│
├── painel
│   └── dashboard administrativo
│
├── static
│   ├── css
│   └── js
│
├── Templates
│
├── docs
│   └── diagramas
│
└── manage.py
```

---

# 🚀 Como Executar o Projeto Localmente

## 1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
```

Acesse a pasta:

```bash
cd La_Piazza
```

---

# 2. Criar ambiente virtual

Linux:

```bash
python3 -m venv .venv
```

Ativar:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

---

# 3. Instalar dependências

Execute:

```bash
pip install -r requirements.txt
```

---

# 4. Configurar banco de dados

Execute as migrações:

```bash
python manage.py migrate
```

---

# 5. Criar superusuário inicial

Para acessar a área administrativa:

```bash
python manage.py createsuperuser
```

Preencha:

```
Usuário:
Email:
Senha:
```

Esse usuário terá permissões administrativas para testes.

---

# 6. Executar aplicação

Inicie o servidor:

```bash
python manage.py runserver
```

Acesse:

```
http://127.0.0.1:8000/
```

---

# 🔗 Principais Endereços

Página inicial:

```
http://127.0.0.1:8000/
```

Admin Django:

```
http://127.0.0.1:8000/admin/
```

Dashboard:

```
http://127.0.0.1:8000/painel/
```

---

# 🧪 Testes Realizados

Foram realizados testes de:

✅ Criação de usuários;  
✅ Login e autenticação;  
✅ Controle de permissões;  
✅ CRUD de pizzas;  
✅ CRUD de categorias;  
✅ CRUD de estoque;  
✅ CRUD de pedidos;  
✅ Integração com banco de dados;  
✅ Funcionamento do painel administrativo.

---

# 👥 Equipe

Projeto desenvolvido por:

**Marina e Pedro**

Projeto Final - Desenvolvimento Web

---

# 📌 Status do Projeto

🚧 Em desenvolvimento

Possíveis melhorias futuras:

- Sistema de pagamentos;
- Relatórios financeiros;
- Integração com pedidos online;
- Aplicação mobile;
- Melhorias de acessibilidade;
- Novos indicadores administrativos.

---

<div align="center">

## 🍕 La Piazza

### Tecnologia transformando a gestão de uma pizzaria.

</div>