document.addEventListener("DOMContentLoaded", () => {

    const page =
        document.querySelector(".pizza-page");

    if (!page) {
        return;
    }

    initPizzaSearch(page);
    initCategoryFilter(page);
    initViewToggle();
    initKeyboardShortcut();
    initPizzaCardTilt();
});


/* =========================================================
   BUSCA COM DEBOUNCE
   ========================================================= */

function initPizzaSearch(page) {

    const input =
        document.getElementById("pizzaSearch");

    const form =
        document.getElementById("pizzaFilterForm");

    if (!input || !form) {
        return;
    }

    let timer = null;


    input.addEventListener("input", () => {

        clearTimeout(timer);

        page.classList.add(
            "is-filtering"
        );


        timer = setTimeout(() => {

            form.submit();

        }, 550);

    });

}


/* =========================================================
   FILTRO DE CATEGORIA
   ========================================================= */

function initCategoryFilter(page) {

    const select =
        document.getElementById(
            "pizzaCategoryFilter"
        );

    const form =
        document.getElementById(
            "pizzaFilterForm"
        );

    if (!select || !form) {
        return;
    }


    select.addEventListener(
        "change",
        () => {

            page.classList.add(
                "is-filtering"
            );

            form.submit();

        }
    );

}


/* =========================================================
   GRID / LIST VIEW
   ========================================================= */

function initViewToggle() {

    const grid =
        document.getElementById(
            "pizzaGrid"
        );

    const buttons =
        document.querySelectorAll(
            "[data-pizza-view]"
        );

    if (!grid || !buttons.length) {
        return;
    }


    const savedView =
        localStorage.getItem(
            "lapiazza-pizza-view"
        ) || "grid";


    applyView(
        savedView,
        grid,
        buttons
    );


    buttons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const view =
                    button.dataset.pizzaView;

                applyView(
                    view,
                    grid,
                    buttons
                );

                localStorage.setItem(
                    "lapiazza-pizza-view",
                    view
                );

            }
        );

    });

}


function applyView(
    view,
    grid,
    buttons
) {

    grid.classList.toggle(
        "list-view",
        view === "list"
    );


    buttons.forEach(button => {

        button.classList.toggle(
            "active",
            button.dataset.pizzaView === view
        );

    });

}


/* =========================================================
   ATALHO /
   ========================================================= */

function initKeyboardShortcut() {

    const search =
        document.getElementById(
            "pizzaSearch"
        );

    if (!search) {
        return;
    }


    document.addEventListener(
        "keydown",
        event => {

            const tag =
                document.activeElement
                    ?.tagName
                    ?.toLowerCase();


            if (
                event.key === "/"
                &&
                tag !== "input"
                &&
                tag !== "textarea"
            ) {

                event.preventDefault();

                search.focus();

                search.select();

            }

        }
    );

}


/* =========================================================
   EFEITO 3D SUTIL
   ========================================================= */

function initPizzaCardTilt() {

    if (
        window.matchMedia(
            "(pointer: coarse)"
        ).matches
    ) {
        return;
    }


    document.querySelectorAll(
        ".pizza-card"
    ).forEach(card => {

        card.addEventListener(
            "mousemove",
            event => {

                const rect =
                    card.getBoundingClientRect();


                const x =
                    event.clientX
                    - rect.left;

                const y =
                    event.clientY
                    - rect.top;


                const centerX =
                    rect.width / 2;

                const centerY =
                    rect.height / 2;


                const rotateX =
                    (
                        centerY - y
                    ) / 35;

                const rotateY =
                    (
                        x - centerX
                    ) / 35;


                card.style.transform =
                    `
                    perspective(900px)
                    translateY(-7px)
                    rotateX(${rotateX}deg)
                    rotateY(${rotateY}deg)
                    `;

            }
        );


        card.addEventListener(
            "mouseleave",
            () => {

                card.style.transform = "";

            }
        );

    });

}


/* =========================================================
   FORMULÁRIO / PREVIEW
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initPizzaFormPreview();
    initPizzaDescriptionCounter();

});


function initPizzaFormPreview() {

    const nameInput =
        document.getElementById("id_nome");

    const descriptionInput =
        document.getElementById("id_descricao");

    const priceInput =
        document.getElementById("id_preco");

    const categoryInput =
        document.getElementById("id_categoria");

    const imageInput =
        document.getElementById("id_imagem");


    const previewName =
        document.getElementById("previewPizzaName");

    const previewDescription =
        document.getElementById(
            "previewPizzaDescription"
        );

    const previewPrice =
        document.getElementById(
            "previewPizzaPrice"
        );

    const previewCategory =
        document.getElementById(
            "previewPizzaCategory"
        );

    const previewImage =
        document.getElementById(
            "previewPizzaImage"
        );


    if (nameInput && previewName) {

        nameInput.addEventListener(
            "input",
            () => {

                previewName.textContent =
                    nameInput.value.trim()
                    || "Nome da pizza";

            }
        );

    }


    if (
        descriptionInput
        &&
        previewDescription
    ) {

        descriptionInput.addEventListener(
            "input",
            () => {

                previewDescription.textContent =
                    descriptionInput.value.trim()
                    || "A descrição aparecerá aqui.";

            }
        );

    }


    if (priceInput && previewPrice) {

        priceInput.addEventListener(
            "input",
            () => {

                const value =
                    Number(
                        priceInput.value
                            .replace(",", ".")
                    );


                previewPrice.textContent =
                    Number.isFinite(value)
                        ? value.toLocaleString(
                            "pt-BR",
                            {
                                style: "currency",
                                currency: "BRL"
                            }
                        )
                        : "R$ 0,00";

            }
        );

    }


    if (
        categoryInput
        &&
        previewCategory
    ) {

        const updateCategory = () => {

            const option =
                categoryInput.options[
                    categoryInput.selectedIndex
                ];


            previewCategory.textContent =
                option?.text
                || "Categoria";

        };


        categoryInput.addEventListener(
            "change",
            updateCategory
        );


        updateCategory();

    }


    if (imageInput && previewImage) {

        imageInput.addEventListener(
            "change",
            () => {

                const file =
                    imageInput.files?.[0];


                if (!file) {
                    return;
                }


                if (
                    !file.type.startsWith(
                        "image/"
                    )
                ) {
                    return;
                }


                const reader =
                    new FileReader();


                reader.addEventListener(
                    "load",
                    event => {

                        previewImage.innerHTML = "";

                        const img =
                            document.createElement(
                                "img"
                            );


                        img.src =
                            event.target.result;

                        img.alt =
                            "Pré-visualização da pizza";


                        previewImage.appendChild(
                            img
                        );

                    }
                );


                reader.readAsDataURL(
                    file
                );

            }
        );

    }

}


/* =========================================================
   CONTADOR
   ========================================================= */

function initPizzaDescriptionCounter() {

    const input =
        document.getElementById(
            "id_descricao"
        );

    const counter =
        document.getElementById(
            "pizzaDescriptionCount"
        );


    if (!input || !counter) {
        return;
    }


    const update = () => {

        counter.textContent =
            `${input.value.length} caracteres`;

    };


    input.addEventListener(
        "input",
        update
    );


    update();

}