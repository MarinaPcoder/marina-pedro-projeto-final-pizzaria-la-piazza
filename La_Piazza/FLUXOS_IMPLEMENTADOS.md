# Fluxos de compra e gerenciamento

## Regras implementadas

- Visitantes podem consultar o cardapio e montar um carrinho na sessao.
- Para enviar o pedido, e preciso entrar em uma conta do grupo Cliente. O cadastro publico atribui esse grupo automaticamente.
- Uma conta pode participar de Cliente e Funcionario ao mesmo tempo. Um funcionario sem Cliente registra pedidos para outros compradores, mas nao compra em nome proprio no checkout.
- A gestao exige Funcionario (ou superusuario) e a permissao especifica de cada operacao. `is_staff` libera o Django Admin, nao substitui esses grupos.
- No site, `usuario` e o comprador autenticado, `origem` e SITE e `registrado_por` fica vazio. No balcao, `usuario` e o cliente selecionado, `origem` e BALCAO e `registrado_por` e o funcionario autenticado.
- Cada cliente ve somente seus pedidos e enderecos. O dono do endereco e definido pelo servidor, nunca pelo formulario enviado.
- O checkout permite retirada ou entrega. Entrega exige um endereco ativo do comprador. O pedido guarda uma copia do endereco, preservada mesmo se o cadastro mudar.
- Precos sao obtidos do banco. Se mudarem depois da inclusao no carrinho, o checkout apresenta o novo total e exige novo envio. Uma chave unica evita duplicar pedidos ao reenviar o mesmo checkout.
- O pagamento previsto e na entrega ou retirada; nao foi adicionado um gateway de pagamento.

## Status e estoque

O checkout cria um pedido PENDENTE. A equipe confere e confirma o pedido pela pagina de detalhes da gestao. A confirmacao soma os ingredientes das receitas multiplicados pelas quantidades de pizzas e registra a saida de estoque em uma transacao. Se um ingrediente faltar, estiver inativo ou vencido, ou uma pizza estiver sem receita/disponibilidade, a operacao e desfeita integralmente. Confirmar novamente nao baixa estoque outra vez.

Fluxos permitidos:

- Retirada: PENDENTE -> CONFIRMADO -> EM_PREPARO -> PRONTO -> ENTREGUE.
- Entrega: PENDENTE -> CONFIRMADO -> EM_PREPARO -> PRONTO -> SAIU_ENTREGA -> ENTREGUE.
- Cancelamento: somente PENDENTE -> CANCELADO, pelo cliente dono ou pela equipe.

Pedidos confirmados nao permitem edicao ou exclusao de itens. O formulario comum nao permite escolher status livremente; a equipe usa as acoes de transicao. Pedidos e itens ficam somente para consulta no Django Admin, para preservar as mesmas regras. A operacao acontece em `/gerenciamento/pedidos/`.

O campo `estoque_baixado_em` registra a confirmacao e `concluido_em` registra quando o pedido chegou a ENTREGUE. O acompanhamento do cliente mostra o status atual e oferece o botao de atualizacao.

## Indicadores

O dashboard permanece em `Piazza/dashboard.py`, acessivel por `/painel/`; nao foi recriado o app painel. Ele consulta o banco para mostrar pedidos criados hoje, pedidos pendentes, itens ativos com estoque baixo, faturamento e pizzas mais vendidas.

Faturamento e ticket medio consideram somente pedidos ENTREGUES, na data de `concluido_em`. Pizzas mais vendidas tambem consideram entregas concluidas no periodo escolhido. Sao valores operacionais dos pedidos, sem conciliacao de pagamentos. A contagem de pedidos por dia usa a data de criacao.

Para pedidos que ja estavam ENTREGUES antes desta alteracao, a migracao preenche `concluido_em` com a ultima atualizacao registrada. Essa e uma referencia historica aproximada, pois o sistema anterior nao guardava a data de conclusao separadamente.

## Preparar o banco

```bash
python3 manage.py migrate
python3 manage.py configurar_grupos
python3 manage.py carga_exemplo
python3 manage.py criar_admin --username admin
```

`configurar_grupos` sincroniza as permissoes dos grupos Cliente e Funcionario com as listas de `usuarios/permissions.py`. Nao muda os membros dos grupos.

`carga_exemplo` tambem configura os grupos e cria categorias, ingredientes com saldo inicial, pizzas e receitas de exemplo. Nao sobrescreve pizzas, receitas ou saldos existentes. Registra as entradas iniciais somente para ingredientes novos. Se um ingrediente de mesmo nome tiver outra unidade, interrompe a carga para evitar uma receita com unidades erradas.

`criar_admin` pede uma senha interativamente, valida a senha e cria um Usuario superusuario. Se o administrador ja existir, preserva seus dados e senha; se o nome pertencer a uma conta comum, exige outro nome. Para automacao, aceita `DJANGO_SUPERUSER_PASSWORD` no ambiente junto com `--noinput`, sem senha fixa no codigo. Administradores que desejarem comprar pelo site tambem precisam pertencer a Cliente.

As migracoes e a configuracao dos grupos foram executadas no banco local. A carga de exemplos e a criacao de administrador foram testadas em banco de teste; nao foram usadas para substituir os dados locais existentes.

## Arquivos criados nesta implementacao

| Arquivo | Funcao |
| --- | --- |
| `pedidos/cart.py` | Leitura do carrinho da sessao, calculo de totais e renovacao da chave de checkout quando o carrinho muda. |
| `pedidos/forms.py` | Reune formularios da gestao e da compra publica, incluindo quantidade e entrega. |
| `pedidos/views.py` | Reune a gestao de pedidos com carrinho, checkout e acompanhamento do cliente. |
| `pedidos/urls.py` | Mantem as rotas da gestao e as rotas publicas no namespace `compras`. |
| `pedidos/services.py` | Centraliza confirmacao, consumo das receitas e transicoes de status; reutiliza o servico de movimentacao de estoque existente. |
| `pedidos/decorators.py` | Bloqueia o pedido durante edicoes e impede alterar pedidos que deixaram de ser pendentes. |
| `usuarios/forms.py` | Reune os formularios da gestao e do endereco do proprio cliente. |
| `usuarios/views.py` | Reune a gestao com o cadastro e gerenciamento de enderecos do cliente. |
| `usuarios/management/commands/configurar_grupos.py` | Comando para criar/sincronizar grupos e permissoes. |
| `usuarios/management/commands/criar_admin.py` | Comando para criar administrador com senha informada de forma segura. |
| `pizza/management/commands/carga_exemplo.py` | Comando idempotente de categorias, pizzas, ingredientes, saldos e receitas. |
| `usuarios/management/__init__.py` e `usuarios/management/commands/__init__.py` | Identificam os pacotes Python dos comandos de usuarios. |
| `pizza/management/__init__.py` e `pizza/management/commands/__init__.py` | Identificam os pacotes Python dos comandos de cardapio. |
| `Templates/pedidos/publico/base.html` | Estrutura comum das telas de compra e exibicao das mensagens. |
| `Templates/pedidos/publico/carrinho.html` | Itens, quantidades, remocao e total do carrinho. |
| `Templates/pedidos/publico/checkout.html` | Escolha do atendimento/endereco, resumo e envio do pedido. |
| `Templates/pedidos/publico/lista.html` | Historico paginado dos pedidos do cliente. |
| `Templates/pedidos/publico/detalhe.html` | Itens, total, endereco historico, status e cancelamento permitido. |
| `Templates/usuarios/enderecos.html` | Lista dos enderecos ativos com acoes de gerenciamento. |
| `Templates/usuarios/endereco_form.html` | Tela de criacao e edicao de endereco proprio. |
| `static/css/compras.css` | Layout responsivo e estilos das telas de compra. |
| `pedidos/migrations/0004_pedido_checkout_token_and_more.py` | Adiciona a chave unica de checkout e amplia o campo de endereco historico para texto. |
| `pedidos/migrations/0005_pedido_concluido_em.py` | Adiciona a data de conclusao e preenche pedidos anteriormente entregues. |
| `FLUXOS_IMPLEMENTADOS.md` | Este documento, com regras, comandos e explicacao dos arquivos. |

Os arquivos existentes de modelos, formularios, views, rotas, admin e templates foram ajustados para ligar essas partes. `Templates/pizza/menu.html` e os blocos de produtos da pagina inicial agora usam as pizzas do banco. `usuarios/urls.py` continua concentrando as rotas de usuarios; `context_processors.py` continua informando aos templates se o usuario e cliente ou funcionario.

## Verificar e executar

```bash
python3 manage.py check
python3 manage.py makemigrations --check --dry-run
python3 manage.py runserver 127.0.0.1:8001
```

Pontos de entrada: `/menu/`, `/compras/carrinho/`, `/compras/meus-pedidos/`, `/conta/enderecos/`, `/gerenciamento/pedidos/` e `/painel/`.
