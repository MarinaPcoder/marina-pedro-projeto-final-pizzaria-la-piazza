document.addEventListener(
    "DOMContentLoaded",
    () => {

        const dashboard =
            document.getElementById(
                "dashboard"
            );


        if (!dashboard) {
            return;
        }


        const initialDataElement =
            document.getElementById(
                "dashboard-initial-data"
            );


        if (!initialDataElement) {
            return;
        }


        const initialData =
            JSON.parse(
                initialDataElement.textContent
            );


        const state = {
            period:
                initialData.periodo || 7,

            charts: {},

            lastUpdate:
                new Date()
        };


        configureChartJS();

        initClock();

        initCounters();

        initStockBars();

        initStatusBadges();

        initMovementColors();

        initDashboardSearch();

        initChartExpansion();

        initCharts(
            initialData,
            state
        );

        initPeriodSelector(
            dashboard,
            state
        );

        initRefresh(
            dashboard,
            state
        );

        initAutoRefresh(
            dashboard,
            state
        );

        updateLastUpdate(
            state
        );

    }
);


/* =========================================================
   CHART.JS GLOBAL
   ========================================================= */

function configureChartJS() {

    if (
        typeof Chart === "undefined"
    ) {
        console.error(
            "Chart.js não foi carregado."
        );

        return;
    }


    Chart.defaults.color =
        "#96918b";

    Chart.defaults.borderColor =
        "rgba(255, 255, 255, 0.06)";

    Chart.defaults.font.family =
        '"DM Sans", sans-serif';

    Chart.defaults.animation.duration =
        950;

    Chart.defaults.animation.easing =
        "easeOutQuart";


    Chart.defaults.plugins.legend.labels.usePointStyle =
        true;

    Chart.defaults.plugins.legend.labels.pointStyle =
        "circle";

    Chart.defaults.plugins.legend.labels.boxWidth =
        7;

    Chart.defaults.plugins.legend.labels.boxHeight =
        7;

    Chart.defaults.plugins.legend.labels.padding =
        16;

}


/* =========================================================
   CORES
   ========================================================= */

const dashboardColors = {

    orange:
        "#fac564",

    orangeLight:
        "#ffd987",

    cream:
        "#f4ead8",

    green:
        "#65ad79",

    blue:
        "#648fc1",

    purple:
        "#9776bd",

    yellow:
        "#dba65a",

    red:
        "#cf6565",

    cyan:
        "#68aab0",

    muted:
        "#77716c",

};


/* =========================================================
   RELÓGIO + SAUDAÇÃO
   ========================================================= */

function initClock() {

    const clock =
        document.getElementById(
            "dashboardClock"
        );

    const dateElement =
        document.getElementById(
            "dashboardDate"
        );

    const greeting =
        document.getElementById(
            "dashboardGreeting"
        );


    const update = () => {

        const now =
            new Date();


        if (clock) {

            clock.textContent =
                new Intl.DateTimeFormat(
                    "pt-BR",
                    {
                        hour:
                            "2-digit",

                        minute:
                            "2-digit",

                        second:
                            "2-digit",
                    }
                ).format(
                    now
                );

        }


        if (dateElement) {

            dateElement.textContent =
                new Intl.DateTimeFormat(
                    "pt-BR",
                    {
                        weekday:
                            "long",

                        day:
                            "2-digit",

                        month:
                            "long",
                    }
                ).format(
                    now
                );

        }


        if (greeting) {

            const hour =
                now.getHours();


            if (hour < 12) {

                greeting.textContent =
                    "Bom dia";

            } else if (
                hour < 18
            ) {

                greeting.textContent =
                    "Boa tarde";

            } else {

                greeting.textContent =
                    "Boa noite";

            }

        }

    };


    update();

    setInterval(
        update,
        1000
    );

}


/* =========================================================
   CONTADORES ANIMADOS
   ========================================================= */

function initCounters() {

    const counters =
        document.querySelectorAll(
            "[data-counter]"
        );


    counters.forEach(
        counter => {

            const target =
                Number(
                    String(
                        counter.dataset.counter
                    ).replace(
                        ",",
                        "."
                    )
                ) || 0;


            const currency =
                counter.dataset.currency ===
                "true";


            animateCounter(
                counter,
                target,
                currency
            );

        }
    );

}


function animateCounter(
    element,
    target,
    currency
) {

    const duration =
        1100;

    const startTime =
        performance.now();


    const formatter =
        new Intl.NumberFormat(
            "pt-BR",
            currency
                ? {
                    style:
                        "currency",

                    currency:
                        "BRL",
                }
                : {
                    maximumFractionDigits:
                        0,
                }
        );


    const frame = (
        currentTime
    ) => {

        const elapsed =
            currentTime
            - startTime;


        const progress =
            Math.min(
                elapsed / duration,
                1
            );


        const eased =
            1
            - Math.pow(
                1 - progress,
                4
            );


        const value =
            target
            * eased;


        element.textContent =
            formatter.format(
                currency
                    ? value
                    : Math.round(
                        value
                    )
            );


        if (progress < 1) {

            requestAnimationFrame(
                frame
            );

        }

    };


    requestAnimationFrame(
        frame
    );

}


/* =========================================================
   BARRAS DE ESTOQUE
   ========================================================= */

function initStockBars() {

    const bars =
        document.querySelectorAll(
            ".stock-progress-bar"
        );


    requestAnimationFrame(
        () => {

            bars.forEach(
                bar => {

                    const current =
                        Number(
                            String(
                                bar.dataset.stockCurrent
                            ).replace(
                                ",",
                                "."
                            )
                        ) || 0;


                    const minimum =
                        Number(
                            String(
                                bar.dataset.stockMinimum
                            ).replace(
                                ",",
                                "."
                            )
                        ) || 0;


                    let percent;


                    if (minimum <= 0) {

                        percent = 100;

                    } else {

                        percent =
                            (
                                current
                                / minimum
                            )
                            * 100;

                    }


                    percent =
                        Math.max(
                            4,
                            Math.min(
                                percent,
                                100
                            )
                        );


                    setTimeout(
                        () => {

                            bar.style.width =
                                `${percent}%`;

                        },
                        220
                    );

                }
            );

        }
    );

}


/* =========================================================
   STATUS DOS PEDIDOS
   ========================================================= */

function initStatusBadges() {

    document.querySelectorAll(
        ".dashboard-status"
    ).forEach(
        element => {

            const text =
                normalizeText(
                    element.dataset.status
                );


            if (
                text.includes(
                    "entreg"
                )
                ||
                text.includes(
                    "pronto"
                )
            ) {

                element.classList.add(
                    "status-success"
                );

            } else if (
                text.includes(
                    "cancel"
                )
            ) {

                element.classList.add(
                    "status-danger"
                );

            } else if (
                text.includes(
                    "preparo"
                )
                ||
                text.includes(
                    "pendente"
                )
            ) {

                element.classList.add(
                    "status-warning"
                );

            } else {

                element.classList.add(
                    "status-info"
                );

            }

        }
    );

}


/* =========================================================
   CORES DAS MOVIMENTAÇÕES
   ========================================================= */

function initMovementColors() {

    document.querySelectorAll(
        ".movement-dot"
    ).forEach(
        dot => {

            const type =
                normalizeText(
                    dot.dataset.movement
                );


            if (
                type.includes(
                    "entrada"
                )
            ) {

                dot.classList.add(
                    "entrada"
                );

            } else if (
                type.includes(
                    "saida"
                )
            ) {

                dot.classList.add(
                    "saida"
                );

            } else if (
                type.includes(
                    "perda"
                )
            ) {

                dot.classList.add(
                    "perda"
                );

            }

        }
    );

}


/* =========================================================
   BUSCA DO DASHBOARD
   ========================================================= */

function initDashboardSearch() {

    const input =
        document.getElementById(
            "dashboardSearch"
        );

    const noResults =
        document.getElementById(
            "dashboardNoResults"
        );


    if (!input) {
        return;
    }


    const elements =
        document.querySelectorAll(
            "[data-search]"
        );


    const filter = () => {

        const query =
            normalizeText(
                input.value.trim()
            );


        let visible =
            0;


        elements.forEach(
            element => {

                const content =
                    normalizeText(
                        element.dataset.search
                    );


                const match =
                    !query
                    ||
                    content.includes(
                        query
                    );


                element.classList.toggle(
                    "dashboard-hidden-by-search",
                    !match
                );


                if (match) {
                    visible++;
                }

            }
        );


        if (noResults) {

            noResults.hidden =
                !query
                || visible > 0;

        }

    };


    input.addEventListener(
        "input",
        filter
    );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "/"
                &&
                document.activeElement
                    !== input
            ) {

                const tag =
                    document.activeElement
                        ?.tagName
                        ?.toLowerCase();


                if (
                    tag === "input"
                    ||
                    tag === "textarea"
                ) {
                    return;
                }


                event.preventDefault();

                input.focus();

            }


            if (
                event.key ===
                    "Escape"
                &&
                document.activeElement
                    === input
            ) {

                input.value = "";

                input.blur();

                filter();

            }

        }
    );

}


/* =========================================================
   PLUGIN — TEXTO CENTRAL DO DOUGHNUT
   ========================================================= */

const centerTextPlugin = {

    id:
        "centerText",


    afterDraw(
        chart,
        args,
        options
    ) {

        if (
            chart.config.type
            !== "doughnut"
        ) {
            return;
        }


        const {
            ctx,
            chartArea
        } = chart;


        if (!chartArea) {
            return;
        }


        const total =
            chart.data.datasets[0].data.reduce(
                (
                    sum,
                    value
                ) =>
                    sum
                    + Number(
                        value
                    ),
                0
            );


        const x =
            (
                chartArea.left
                + chartArea.right
            ) / 2;

        const y =
            (
                chartArea.top
                + chartArea.bottom
            ) / 2;


        ctx.save();


        ctx.textAlign =
            "center";

        ctx.textBaseline =
            "middle";


        ctx.fillStyle =
            "#f4ead8";

        ctx.font =
            "700 28px DM Sans";


        ctx.fillText(
            total,
            x,
            y - 7
        );


        ctx.fillStyle =
            "#77716c";

        ctx.font =
            "500 10px DM Sans";


        ctx.fillText(
            "PEDIDOS",
            x,
            y + 17
        );


        ctx.restore();

    }

};


/* =========================================================
   CRIAÇÃO DOS GRÁFICOS
   ========================================================= */

function initCharts(
    data,
    state
) {

    if (
        typeof Chart === "undefined"
    ) {
        return;
    }


    Chart.register(
        centerTextPlugin
    );


    createOrdersChart(
        data,
        state
    );

    createStatusChart(
        data,
        state
    );

    createPizzasChart(
        data,
        state
    );

    createRevenueChart(
        data,
        state
    );

    createHealthChart(
        data,
        state
    );

    createStockChart(
        data,
        state
    );

}


/* =========================================================
   GRÁFICO 1 — PEDIDOS / LINHA
   ========================================================= */

function createOrdersChart(
    data,
    state
) {

    const canvas =
        document.getElementById(
            "ordersChart"
        );


    if (!canvas) {
        return;
    }


    const ctx =
        canvas.getContext(
            "2d"
        );


    const gradient =
        ctx.createLinearGradient(
            0,
            0,
            0,
            380
        );


    gradient.addColorStop(
        0,
        "rgba(250, 197, 100, 0.32)"
    );

    gradient.addColorStop(
        1,
        "rgba(250, 197, 100, 0)"
    );


    state.charts.orders =
        new Chart(
            canvas,
            {

                type:
                    "line",

                data: {

                    labels:
                        data.labels,

                    datasets: [
                        {

                            label:
                                "Pedidos",

                            data:
                                data.pedidos_por_dia,

                            borderColor:
                                dashboardColors.orangeLight,

                            backgroundColor:
                                gradient,

                            fill:
                                true,

                            tension:
                                .4,

                            borderWidth:
                                2,

                            pointRadius:
                                3,

                            pointHoverRadius:
                                7,

                            pointBackgroundColor:
                                dashboardColors.orangeLight,

                        }
                    ]

                },

                options:
                    baseCartesianOptions(),

            }
        );

}


/* =========================================================
   GRÁFICO 2 — STATUS / DOUGHNUT
   ========================================================= */

function createStatusChart(
    data,
    state
) {

    const canvas =
        document.getElementById(
            "statusChart"
        );


    if (!canvas) {
        return;
    }


    state.charts.status =
        new Chart(
            canvas,
            {

                type:
                    "doughnut",

                data: {

                    labels:
                        data.status.labels,

                    datasets: [
                        {

                            data:
                                data.status.valores,

                            backgroundColor:
                                chartPalette(
                                    data.status.valores.length
                                ),

                            borderWidth:
                                0,

                            hoverOffset:
                                8,

                        }
                    ]

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    cutout:
                        "72%",

                    plugins: {

                        legend: {

                            position:
                                "bottom",

                        },

                    }

                },

            }
        );

}


/* =========================================================
   GRÁFICO 3 — PIZZAS / BARRA HORIZONTAL
   ========================================================= */

function createPizzasChart(
    data,
    state
) {

    const canvas =
        document.getElementById(
            "pizzasChart"
        );


    if (!canvas) {
        return;
    }


    state.charts.pizzas =
        new Chart(
            canvas,
            {

                type:
                    "bar",

                data: {

                    labels:
                        data.pizzas.labels,

                    datasets: [
                        {

                            label:
                                "Unidades",

                            data:
                                data.pizzas.valores,

                            backgroundColor:
                                dashboardColors.orange,

                            borderRadius:
                                8,

                            borderSkipped:
                                false,

                            barThickness:
                                18,

                        }
                    ]

                },

                options: {

                    ...baseCartesianOptions(),

                    indexAxis:
                        "y",

                    plugins: {

                        legend: {
                            display:
                                false
                        },

                    }

                },

            }
        );

}


/* =========================================================
   GRÁFICO 4 — FATURAMENTO + TICKET MÉDIO
   ========================================================= */

function createRevenueChart(
    data,
    state
) {

    const canvas =
        document.getElementById(
            "revenueChart"
        );


    if (!canvas) {
        return;
    }


    state.charts.revenue =
        new Chart(
            canvas,
            {

                type:
                    "bar",

                data: {

                    labels:
                        data.labels,

                    datasets: [

                        {

                            type:
                                "bar",

                            label:
                                "Faturamento",

                            data:
                                data.faturamento_por_dia,

                            backgroundColor:
                                "rgba(101, 173, 121, .48)",

                            borderColor:
                                dashboardColors.green,

                            borderWidth:
                                1,

                            borderRadius:
                                7,

                            yAxisID:
                                "y",

                        },

                        {

                            type:
                                "line",

                            label:
                                "Ticket médio",

                            data:
                                data.ticket_medio,

                            borderColor:
                                dashboardColors.orangeLight,

                            backgroundColor:
                                dashboardColors.orangeLight,

                            borderWidth:
                                2,

                            tension:
                                .4,

                            pointRadius:
                                2,

                            pointHoverRadius:
                                6,

                            yAxisID:
                                "y1",

                        }

                    ]

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    interaction: {

                        mode:
                            "index",

                        intersect:
                            false,

                    },

                    scales: {

                        x:
                            axisStyle(),

                        y: {

                            ...axisStyle(),

                            beginAtZero:
                                true,

                            position:
                                "left",

                            ticks: {

                                ...axisStyle().ticks,

                                callback:
                                    value =>
                                        formatMoney(
                                            value
                                        )

                            }

                        },

                        y1: {

                            ...axisStyle(),

                            beginAtZero:
                                true,

                            position:
                                "right",

                            grid: {
                                display:
                                    false
                            },

                            ticks: {

                                color:
                                    "#77716c",

                                callback:
                                    value =>
                                        formatMoney(
                                            value
                                        )

                            }

                        }

                    }

                },

            }
        );

}


/* =========================================================
   GRÁFICO 5 — RADAR
   ========================================================= */

function createHealthChart(
    data,
    state
) {

    const canvas =
        document.getElementById(
            "healthChart"
        );


    if (!canvas) {
        return;
    }


    state.charts.health =
        new Chart(
            canvas,
            {

                type:
                    "radar",

                data: {

                    labels:
                        data.saude.labels,

                    datasets: [
                        {

                            label:
                                "Saúde operacional",

                            data:
                                data.saude.valores,

                            backgroundColor:
                                "rgba(250, 197, 100, .18)",

                            borderColor:
                                dashboardColors.orangeLight,

                            borderWidth:
                                2,

                            pointBackgroundColor:
                                dashboardColors.cream,

                            pointBorderColor:
                                dashboardColors.orange,

                            pointRadius:
                                3,

                        }
                    ]

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    scales: {

                        r: {

                            beginAtZero:
                                true,

                            max:
                                100,

                            ticks: {

                                display:
                                    false,

                            },

                            grid: {

                                color:
                                    "rgba(255,255,255,.06)",

                            },

                            angleLines: {

                                color:
                                    "rgba(255,255,255,.06)",

                            },

                            pointLabels: {

                                color:
                                    "#97918b",

                                font: {
                                    size:
                                        10
                                }

                            },

                        }

                    },

                    plugins: {

                        legend: {
                            display:
                                false
                        },

                    }

                },

            }
        );

}


/* =========================================================
   GRÁFICO 6 — POLAR AREA
   ========================================================= */

function createStockChart(
    data,
    state
) {

    const canvas =
        document.getElementById(
            "stockChart"
        );


    if (!canvas) {
        return;
    }


    state.charts.stock =
        new Chart(
            canvas,
            {

                type:
                    "polarArea",

                data: {

                    labels:
                        data.estoque.labels,

                    datasets: [
                        {

                            data:
                                data.estoque.valores,

                            backgroundColor:
                                chartPalette(
                                    data.estoque.valores.length,
                                    .52
                                ),

                            borderColor:
                                "rgba(255,255,255,.06)",

                            borderWidth:
                                1,

                        }
                    ]

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    scales: {

                        r: {

                            ticks: {
                                display:
                                    false
                            },

                            grid: {

                                color:
                                    "rgba(255,255,255,.05)",

                            },

                            angleLines: {

                                color:
                                    "rgba(255,255,255,.04)",

                            }

                        }

                    },

                    plugins: {

                        legend: {

                            position:
                                "bottom",

                        }

                    }

                },

            }
        );

}


/* =========================================================
   CONFIGURAÇÕES PADRÃO
   ========================================================= */

function baseCartesianOptions() {

    return {

        responsive:
            true,

        maintainAspectRatio:
            false,

        interaction: {

            mode:
                "index",

            intersect:
                false,

        },

        plugins: {

            legend: {

                position:
                    "top",

                align:
                    "end",

            },

        },

        scales: {

            x:
                axisStyle(),

            y: {

                ...axisStyle(),

                beginAtZero:
                    true,

            },

        },

    };

}


function axisStyle() {

    return {

        grid: {

            color:
                "rgba(255,255,255,.045)",

            drawBorder:
                false,

        },

        border: {
            display:
                false
        },

        ticks: {

            color:
                "#77716c",

            font: {
                size:
                    9
            },

        },

    };

}


/* =========================================================
   ALTERAÇÃO DE PERÍODO
   ========================================================= */

function initPeriodSelector(
    dashboard,
    state
) {

    const buttons =
        document.querySelectorAll(
            ".period-button"
        );


    buttons.forEach(
        button => {

            button.addEventListener(
                "click",
                async () => {

                    const period =
                        Number(
                            button.dataset.period
                        );


                    if (
                        period
                        === state.period
                    ) {
                        return;
                    }


                    buttons.forEach(
                        item =>
                            item.classList.remove(
                                "active"
                            )
                    );


                    button.classList.add(
                        "active"
                    );


                    state.period =
                        period;


                    await fetchDashboardData(
                        dashboard,
                        state
                    );

                }
            );

        }
    );

}


/* =========================================================
   REFRESH MANUAL
   ========================================================= */

function initRefresh(
    dashboard,
    state
) {

    const button =
        document.getElementById(
            "dashboardRefresh"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        async () => {

            button.classList.add(
                "loading"
            );


            await fetchDashboardData(
                dashboard,
                state
            );


            setTimeout(
                () => {

                    button.classList.remove(
                        "loading"
                    );

                },
                350
            );

        }
    );

}


/* =========================================================
   AUTOREFRESH
   ========================================================= */

function initAutoRefresh(
    dashboard,
    state
) {

    setInterval(
        () => {

            if (
                document.hidden
            ) {
                return;
            }


            fetchDashboardData(
                dashboard,
                state,
                false
            );

        },
        60000
    );

}


/* =========================================================
   FETCH DA API DJANGO
   ========================================================= */

async function fetchDashboardData(
    dashboard,
    state,
    loading = true
) {

    const endpoint =
        dashboard.dataset.endpoint;


    if (!endpoint) {
        return;
    }


    if (loading) {

        dashboard.classList.add(
            "is-fetching"
        );

    }


    try {

        const url =
            new URL(
                endpoint,
                window.location.origin
            );


        url.searchParams.set(
            "periodo",
            state.period
        );


        const response =
            await fetch(
                url,
                {
                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest"
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        updateCharts(
            data,
            state
        );


        state.lastUpdate =
            new Date();


        updateLastUpdate(
            state
        );


    } catch (error) {

        console.error(
            "Erro ao atualizar dashboard:",
            error
        );


    } finally {

        dashboard.classList.remove(
            "is-fetching"
        );

    }

}


/* =========================================================
   ATUALIZA OS GRÁFICOS SEM RECARREGAR
   ========================================================= */

function updateCharts(
    data,
    state
) {

    updateChart(
        state.charts.orders,
        data.labels,
        [
            data.pedidos_por_dia
        ]
    );


    updateChart(
        state.charts.status,
        data.status.labels,
        [
            data.status.valores
        ]
    );


    updateChart(
        state.charts.pizzas,
        data.pizzas.labels,
        [
            data.pizzas.valores
        ]
    );


    updateChart(
        state.charts.revenue,
        data.labels,
        [
            data.faturamento_por_dia,
            data.ticket_medio,
        ]
    );


    updateChart(
        state.charts.health,
        data.saude.labels,
        [
            data.saude.valores
        ]
    );


    updateChart(
        state.charts.stock,
        data.estoque.labels,
        [
            data.estoque.valores
        ]
    );


    if (
        state.charts.status
    ) {

        state.charts.status
            .data.datasets[0]
            .backgroundColor =
                chartPalette(
                    data.status.valores.length
                );


        state.charts.status.update();

    }


    if (
        state.charts.stock
    ) {

        state.charts.stock
            .data.datasets[0]
            .backgroundColor =
                chartPalette(
                    data.estoque.valores.length,
                    .52
                );


        state.charts.stock.update();

    }

}


function updateChart(
    chart,
    labels,
    datasets
) {

    if (!chart) {
        return;
    }


    chart.data.labels =
        labels;


    datasets.forEach(
        (
            data,
            index
        ) => {

            if (
                chart.data.datasets[index]
            ) {

                chart.data.datasets[index].data =
                    data;

            }

        }
    );


    chart.update();

}


/* =========================================================
   EXPANDIR GRÁFICO
   ========================================================= */

function initChartExpansion() {

    const buttons =
        document.querySelectorAll(
            ".chart-expand"
        );


    const closeExpanded = () => {

        const card =
            document.querySelector(
                ".dashboard-chart-card.is-expanded"
            );


        if (!card) {
            return;
        }


        card.classList.remove(
            "is-expanded"
        );


        document.body.classList.remove(
            "dashboard-chart-open"
        );


        const icon =
            card.querySelector(
                ".chart-expand i"
            );


        if (icon) {

            icon.className =
                "bi bi-arrows-fullscreen";

        }


        setTimeout(
            resizeAllCharts,
            100
        );

    };


    buttons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const card =
                        button.closest(
                            ".dashboard-chart-card"
                        );


                    if (!card) {
                        return;
                    }


                    const alreadyExpanded =
                        card.classList.contains(
                            "is-expanded"
                        );


                    closeExpanded();


                    if (
                        !alreadyExpanded
                    ) {

                        card.classList.add(
                            "is-expanded"
                        );


                        document.body.classList.add(
                            "dashboard-chart-open"
                        );


                        const icon =
                            button.querySelector(
                                "i"
                            );


                        if (icon) {

                            icon.className =
                                "bi bi-fullscreen-exit";

                        }


                        setTimeout(
                            resizeAllCharts,
                            100
                        );

                    }

                }
            );

        }
    );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape"
            ) {

                closeExpanded();

            }

        }
    );

}


function resizeAllCharts() {

    if (
        typeof Chart === "undefined"
    ) {
        return;
    }


    Object.values(
        Chart.instances
    ).forEach(
        chart =>
            chart.resize()
    );

}


/* =========================================================
   ATUALIZAÇÃO
   ========================================================= */

function updateLastUpdate(
    state
) {

    const element =
        document.getElementById(
            "lastUpdate"
        );


    if (!element) {
        return;
    }


    element.textContent =
        `Atualizado às ${
            new Intl.DateTimeFormat(
                "pt-BR",
                {
                    hour:
                        "2-digit",

                    minute:
                        "2-digit",
                }
            ).format(
                state.lastUpdate
            )
        }`;

}


/* =========================================================
   UTILITÁRIOS
   ========================================================= */

function chartPalette(
    amount,
    alpha = 1
) {

    const colors = [

        dashboardColors.orange,
        dashboardColors.green,
        dashboardColors.blue,
        dashboardColors.purple,
        dashboardColors.yellow,
        dashboardColors.red,
        dashboardColors.cyan,
        dashboardColors.orangeLight,

    ];


    return Array.from(
        {
            length:
                amount
        },

        (
            _,
            index
        ) => {

            const color =
                colors[
                    index
                    % colors.length
                ];


            if (
                alpha === 1
            ) {
                return color;
            }


            return hexToRgba(
                color,
                alpha
            );

        }
    );

}


function hexToRgba(
    hex,
    alpha
) {

    const value =
        hex.replace(
            "#",
            ""
        );


    const r =
        parseInt(
            value.substring(
                0,
                2
            ),
            16
        );

    const g =
        parseInt(
            value.substring(
                2,
                4
            ),
            16
        );

    const b =
        parseInt(
            value.substring(
                4,
                6
            ),
            16
        );


    return (
        `rgba(${r}, ${g}, ${b}, ${alpha})`
    );

}


function formatMoney(
    value
) {

    return new Intl.NumberFormat(
        "pt-BR",
        {
            style:
                "currency",

            currency:
                "BRL",

            maximumFractionDigits:
                0,
        }
    ).format(
        value
    );

}


function normalizeText(
    value
) {

    return String(
        value || ""
    )
        .normalize(
            "NFD"
        )
        .replace(
            /[\u0300-\u036f]/g,
            ""
        )
        .toLowerCase();

}