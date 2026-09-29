from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from estoque.models import ItemEstoque, MovimentacaoEstoque
from pedidos.models import ItemPedido, Pedido, STATUS_PEDIDO_CHOICES
from pizza.models import Pizza
from usuarios.views import funcionario_required


# Páginas de erro
# Erro 403 - Acesso negado
def erro_403(
    request,
    exception=None,
):

    return render(
        request,
        "erros/403.html",
        status=403,
    )


# Erro 404 - Página não encontrada
def erro_404(
    request,
    exception=None,
):

    return render(
        request,
        "erros/404.html",
        status=404,
    )


# Cálculos e consultas dos indicadores do painel
def percentual(parte, total):
    return round(parte / total * 100, 1) if total else 0


def expressao_valor_item():
    return ExpressionWrapper(
        F("itens__quantidade") * F("itens__preco_unitario"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )


def calcular_faturamento(queryset):
    return queryset.filter(status="ENTREGUE").aggregate(total=Sum(expressao_valor_item()))["total"] or Decimal("0.00")


def gerar_dados_dashboard(periodo=7):
    if periodo not in {7, 15, 30}:
        periodo = 7
    hoje = timezone.localdate()
    inicio = hoje - timedelta(days=periodo - 1)
    pedidos = Pedido.objects.filter(criado_em__date__range=(inicio, hoje))
    entregues = Pedido.objects.filter(status="ENTREGUE", concluido_em__date__range=(inicio, hoje))
    diarios = {
        linha["dia"]: linha["total"] for linha in pedidos.annotate(dia=TruncDate("criado_em"))
        .values("dia").annotate(total=Count("id")).order_by("dia")
    }
    vendas = {
        linha["dia"]: linha for linha in entregues.annotate(dia=TruncDate("concluido_em"))
        .values("dia").annotate(total=Sum(expressao_valor_item()), quantidade=Count("id", distinct=True)).order_by("dia")
    }
    datas = [inicio + timedelta(days=i) for i in range(periodo)]
    faturamento = [float(vendas.get(dia, {}).get("total") or 0) for dia in datas]
    tickets = [round(valor / vendas[dia]["quantidade"], 2) if dia in vendas else 0 for dia, valor in zip(datas, faturamento)]
    pizzas = list(ItemPedido.objects.filter(pedido__in=entregues).values("pizza_id", "pizza__nome")
                  .annotate(total=Sum("quantidade")).order_by("-total", "pizza__nome")[:6])
    status = list(pedidos.values("status").annotate(total=Count("id")).order_by("status"))
    estoque = list(ItemEstoque.objects.filter(ativo=True).values("categoria__nome").annotate(total=Count("id")).order_by("categoria__nome"))
    total_itens = ItemEstoque.objects.filter(ativo=True).count()
    baixos = ItemEstoque.objects.filter(ativo=True, quantidade_atual__lte=F("estoque_minimo")).count()
    total_pizzas = Pizza.objects.count()
    total_pedidos = pedidos.count()
    return {
        "periodo": periodo,
        "labels": [dia.strftime("%d/%m") for dia in datas],
        "pedidos_por_dia": [diarios.get(dia, 0) for dia in datas],
        "faturamento_por_dia": faturamento,
        "ticket_medio": tickets,
        "pizzas": {"labels": [p["pizza__nome"] for p in pizzas], "valores": [p["total"] for p in pizzas]},
        "status": {"labels": [dict(STATUS_PEDIDO_CHOICES)[p["status"]] for p in status], "valores": [p["total"] for p in status]},
        "estoque": {"labels": [p["categoria__nome"] for p in estoque], "valores": [p["total"] for p in estoque]},
        "saude": {
            "labels": ["Pizzas disponiveis", "Estoque saudavel", "Pedidos concluidos", "Sem cancelamentos", "Receitas cadastradas"],
            "valores": [
                percentual(Pizza.objects.filter(disponivel=True, categoria__ativa=True).count(), total_pizzas),
                percentual(total_itens - baixos, total_itens),
                percentual(pedidos.filter(status="ENTREGUE").count(), total_pedidos),
                percentual(pedidos.exclude(status="CANCELADO").count(), total_pedidos),
                percentual(Pizza.objects.filter(receita__isnull=False).distinct().count(), total_pizzas),
            ],
        },
    }


# Views do painel administrativo
@login_required
@funcionario_required
@permission_required("pedidos.view_pedido", raise_exception=True)
def dashboard(request):
    hoje = timezone.localdate()
    pedidos_hoje = Pedido.objects.filter(criado_em__date=hoje)
    vendas_hoje = Pedido.objects.filter(status="ENTREGUE", concluido_em__date=hoje)
    entregues = vendas_hoje.count()
    faturamento = calcular_faturamento(vendas_hoje)
    baixos = ItemEstoque.objects.filter(ativo=True, quantidade_atual__lte=F("estoque_minimo"))
    pendentes = Pedido.objects.filter(status="PENDENTE")
    return render(request, "painel/dashboard.html", {
        "pedidos_hoje": pedidos_hoje.count(),
        "faturamento_hoje": faturamento,
        "ticket_medio_hoje": faturamento / entregues if entregues else Decimal("0.00"),
        "pedidos_pendentes": pendentes.count(),
        "pizzas_disponiveis": Pizza.objects.filter(disponivel=True, categoria__ativa=True).count(),
        "estoque_baixo": baixos.count(),
        "movimentacoes_hoje": MovimentacaoEstoque.objects.filter(criada_em__date=hoje).count(),
        "ultimos_pedidos": Pedido.objects.select_related("usuario").prefetch_related("itens").order_by("-criado_em")[:7],
        "itens_estoque_baixo": baixos.select_related("categoria").order_by("quantidade_atual")[:7],
        "movimentacoes_recentes": MovimentacaoEstoque.objects.select_related("item", "responsavel").order_by("-criada_em")[:7],
        "dados_iniciais": gerar_dados_dashboard(),
    })


@login_required
@funcionario_required
@permission_required("pedidos.view_pedido", raise_exception=True)
def dashboard_dados(request):
    try:
        periodo = int(request.GET.get("periodo", 7))
    except (TypeError, ValueError):
        periodo = 7
    return JsonResponse(gerar_dados_dashboard(periodo))
