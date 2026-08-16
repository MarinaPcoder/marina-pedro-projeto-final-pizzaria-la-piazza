from django.shortcuts import render

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)

from django.db.models import (
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
)

from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from cardapio.models import Pizza

from estoque.models import (
    ItemEstoque,
    MovimentacaoEstoque,
)

from pedidos.models import (
    ItemPedido,
    Pedido,
)


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def obter_valor_choice(model, campo, termo):
    """
    Localiza o valor real de uma opção de TextChoices
    procurando tanto pelo valor quanto pelo texto exibido.

    Isso evita depender diretamente de coisas como:
    Pedido.StatusPedido.CANCELADO
    """

    choices = model._meta.get_field(
        campo
    ).choices

    termo = termo.lower()

    for valor, nome in choices:

        texto = (
            f"{valor} {nome}"
        ).lower()

        if termo in texto:
            return valor

    return None


def percentual(parte, total):

    if not total:
        return 0

    return round(
        (parte / total) * 100,
        1
    )


def expressao_valor_item():

    return ExpressionWrapper(
        F("itens__quantidade")
        * F("itens__preco_unitario"),

        output_field=DecimalField(
            max_digits=14,
            decimal_places=2,
        ),
    )


def pedidos_sem_cancelados(queryset):

    valor_cancelado = obter_valor_choice(
        Pedido,
        "status",
        "cancel",
    )

    if valor_cancelado is not None:

        queryset = queryset.exclude(
            status=valor_cancelado
        )

    return queryset


def calcular_faturamento(queryset):

    resultado = queryset.aggregate(
        total=Sum(
            expressao_valor_item()
        )
    )["total"]

    return resultado or Decimal("0.00")


# =========================================================
# DADOS DOS GRÁFICOS
# =========================================================

def gerar_dados_dashboard(periodo=7):

    periodos_validos = {
        7,
        15,
        30,
    }

    if periodo not in periodos_validos:
        periodo = 7


    hoje = timezone.localdate()

    inicio = (
        hoje
        - timedelta(
            days=periodo - 1
        )
    )


    # =====================================================
    # PEDIDOS DO PERÍODO
    # =====================================================

    pedidos_periodo = Pedido.objects.filter(
        criado_em__date__range=(
            inicio,
            hoje,
        )
    )

    pedidos_validos = pedidos_sem_cancelados(
        pedidos_periodo
    )


    # =====================================================
    # PEDIDOS POR DIA
    # =====================================================

    pedidos_por_dia_query = (
        pedidos_periodo
        .annotate(
            dia=TruncDate(
                "criado_em"
            )
        )
        .values(
            "dia"
        )
        .annotate(
            total=Count(
                "id"
            )
        )
        .order_by(
            "dia"
        )
    )


    pedidos_por_dia_map = {
        item["dia"]: item["total"]
        for item
        in pedidos_por_dia_query
    }


    # =====================================================
    # FATURAMENTO POR DIA
    # =====================================================

    faturamento_query = (
        pedidos_validos
        .annotate(
            dia=TruncDate(
                "criado_em"
            )
        )
        .values(
            "dia"
        )
        .annotate(
            total=Sum(
                expressao_valor_item()
            )
        )
        .order_by(
            "dia"
        )
    )


    faturamento_map = {
        item["dia"]:
            float(
                item["total"] or 0
            )

        for item
        in faturamento_query
    }


    # =====================================================
    # DATAS COMPLETAS
    # =====================================================

    datas = [
        inicio
        + timedelta(
            days=i
        )

        for i
        in range(
            periodo
        )
    ]


    labels = [
        data.strftime(
            "%d/%m"
        )

        for data
        in datas
    ]


    pedidos_diarios = [
        pedidos_por_dia_map.get(
            data,
            0,
        )

        for data
        in datas
    ]


    faturamento_diario = [
        faturamento_map.get(
            data,
            0,
        )

        for data
        in datas
    ]


    ticket_medio = []

    for pedidos, faturamento in zip(
        pedidos_diarios,
        faturamento_diario,
    ):

        if pedidos:

            ticket = (
                faturamento
                / pedidos
            )

        else:
            ticket = 0

        ticket_medio.append(
            round(
                ticket,
                2,
            )
        )


    # =====================================================
    # PIZZAS MAIS VENDIDAS
    # =====================================================

    itens_pedido = ItemPedido.objects.filter(
        pedido__criado_em__date__range=(
            inicio,
            hoje,
        )
    )


    valor_cancelado = obter_valor_choice(
        Pedido,
        "status",
        "cancel",
    )


    if valor_cancelado is not None:

        itens_pedido = itens_pedido.exclude(
            pedido__status=valor_cancelado
        )


    pizzas_mais_vendidas = (
        itens_pedido
        .values(
            "pizza__nome"
        )
        .annotate(
            total=Sum(
                "quantidade"
            )
        )
        .order_by(
            "-total"
        )[:6]
    )


    pizzas_labels = [
        item["pizza__nome"]
        for item
        in pizzas_mais_vendidas
    ]

    pizzas_valores = [
        item["total"]
        for item
        in pizzas_mais_vendidas
    ]


    # =====================================================
    # PEDIDOS POR STATUS
    # =====================================================

    status_choices = dict(
        Pedido._meta.get_field(
            "status"
        ).choices
    )


    status_query = (
        pedidos_periodo
        .values(
            "status"
        )
        .annotate(
            total=Count(
                "id"
            )
        )
        .order_by(
            "-total"
        )
    )


    status_labels = [
        status_choices.get(
            item["status"],
            item["status"],
        )

        for item
        in status_query
    ]


    status_valores = [
        item["total"]
        for item
        in status_query
    ]


    # =====================================================
    # ESTOQUE POR CATEGORIA
    # =====================================================

    estoque_categorias = (
        ItemEstoque.objects
        .filter(
            ativo=True
        )
        .values(
            "categoria__nome"
        )
        .annotate(
            total=Count(
                "id"
            )
        )
        .order_by(
            "-total"
        )
    )


    estoque_labels = [
        item[
            "categoria__nome"
        ] or "Sem categoria"

        for item
        in estoque_categorias
    ]


    estoque_valores = [
        item["total"]
        for item
        in estoque_categorias
    ]


    # =====================================================
    # SAÚDE OPERACIONAL
    # =====================================================

    total_pizzas = (
        Pizza.objects
        .count()
    )

    pizzas_disponiveis = (
        Pizza.objects
        .filter(
            disponivel=True
        )
        .count()
    )


    pizzas_com_receita = (
        Pizza.objects
        .filter(
            receita__isnull=False
        )
        .distinct()
        .count()
    )


    total_itens = (
        ItemEstoque.objects
        .filter(
            ativo=True
        )
        .count()
    )


    itens_baixos = (
        ItemEstoque.objects
        .filter(
            ativo=True,
            quantidade_atual__lte=F(
                "estoque_minimo"
            ),
        )
        .count()
    )


    estoque_saudavel = (
        total_itens
        - itens_baixos
    )


    total_periodo = (
        pedidos_periodo.count()
    )

    validos_periodo = (
        pedidos_validos.count()
    )


    entregue = obter_valor_choice(
        Pedido,
        "status",
        "entreg",
    )


    if entregue is not None:

        pedidos_entregues = (
            pedidos_periodo
            .filter(
                status=entregue
            )
            .count()
        )

    else:
        pedidos_entregues = 0


    saude_labels = [
        "Pizzas disponíveis",
        "Estoque saudável",
        "Pedidos concluídos",
        "Sem cancelamentos",
        "Receitas cadastradas",
    ]


    saude_valores = [
        percentual(
            pizzas_disponiveis,
            total_pizzas,
        ),

        percentual(
            estoque_saudavel,
            total_itens,
        ),

        percentual(
            pedidos_entregues,
            validos_periodo,
        ),

        percentual(
            validos_periodo,
            total_periodo,
        ),

        percentual(
            pizzas_com_receita,
            total_pizzas,
        ),
    ]


    return {

        "periodo": periodo,

        "labels": labels,

        "pedidos_por_dia": (
            pedidos_diarios
        ),

        "faturamento_por_dia": (
            faturamento_diario
        ),

        "ticket_medio": (
            ticket_medio
        ),

        "pizzas": {
            "labels":
                pizzas_labels,

            "valores":
                pizzas_valores,
        },

        "status": {
            "labels":
                status_labels,

            "valores":
                status_valores,
        },

        "estoque": {
            "labels":
                estoque_labels,

            "valores":
                estoque_valores,
        },

        "saude": {
            "labels":
                saude_labels,

            "valores":
                saude_valores,
        },
    }


# =========================================================
# DASHBOARD
# =========================================================

@login_required
@permission_required(
    "pedidos.view_pedido",
    raise_exception=True,
)
def dashboard(request):

    hoje = timezone.localdate()


    # =====================================================
    # PEDIDOS DE HOJE
    # =====================================================

    pedidos_hoje_query = (
        Pedido.objects
        .filter(
            criado_em__date=hoje
        )
    )


    pedidos_hoje = (
        pedidos_hoje_query
        .count()
    )


    pedidos_validos_hoje = (
        pedidos_sem_cancelados(
            pedidos_hoje_query
        )
    )


    faturamento_hoje = (
        calcular_faturamento(
            pedidos_validos_hoje
        )
    )


    quantidade_validos = (
        pedidos_validos_hoje
        .count()
    )


    if quantidade_validos:

        ticket_medio_hoje = (
            faturamento_hoje
            / quantidade_validos
        )

    else:
        ticket_medio_hoje = (
            Decimal("0.00")
        )


    # =====================================================
    # INDICADORES
    # =====================================================

    pizzas_disponiveis = (
        Pizza.objects
        .filter(
            disponivel=True
        )
        .count()
    )


    estoque_baixo = (
        ItemEstoque.objects
        .filter(
            ativo=True,
            quantidade_atual__lte=F(
                "estoque_minimo"
            ),
        )
        .count()
    )


    movimentacoes_hoje = (
        MovimentacaoEstoque.objects
        .filter(
            criada_em__date=hoje
        )
        .count()
    )


    # =====================================================
    # ÚLTIMOS PEDIDOS
    # =====================================================

    ultimos_pedidos = (
        Pedido.objects
        .select_related(
            "usuario"
        )
        .prefetch_related(
            "itens"
        )
        .order_by(
            "-criado_em"
        )[:7]
    )


    # =====================================================
    # ESTOQUE EM ALERTA
    # =====================================================

    itens_estoque_baixo = (
        ItemEstoque.objects
        .filter(
            ativo=True,
            quantidade_atual__lte=F(
                "estoque_minimo"
            ),
        )
        .select_related(
            "categoria"
        )
        .order_by(
            "quantidade_atual"
        )[:7]
    )


    # =====================================================
    # MOVIMENTAÇÕES RECENTES
    # =====================================================

    movimentacoes_recentes = (
        MovimentacaoEstoque.objects
        .select_related(
            "item",
            "responsavel",
        )
        .order_by(
            "-criada_em"
        )[:7]
    )


    contexto = {

        "pedidos_hoje":
            pedidos_hoje,

        "faturamento_hoje":
            faturamento_hoje,

        "ticket_medio_hoje":
            ticket_medio_hoje,

        "pizzas_disponiveis":
            pizzas_disponiveis,

        "estoque_baixo":
            estoque_baixo,

        "movimentacoes_hoje":
            movimentacoes_hoje,

        "ultimos_pedidos":
            ultimos_pedidos,

        "itens_estoque_baixo":
            itens_estoque_baixo,

        "movimentacoes_recentes":
            movimentacoes_recentes,

        "dados_iniciais":
            gerar_dados_dashboard(
                7
            ),
    }


    return render(
        request,
        "painel/dashboard.html",
        contexto,
    )


# =========================================================
# API PARA ATUALIZAÇÃO DOS GRÁFICOS
# =========================================================

@login_required
@permission_required(
    "pedidos.view_pedido",
    raise_exception=True,
)
def dashboard_dados(request):

    try:

        periodo = int(
            request.GET.get(
                "periodo",
                7,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        periodo = 7


    dados = gerar_dados_dashboard(
        periodo
    )


    return JsonResponse(
        dados
    )