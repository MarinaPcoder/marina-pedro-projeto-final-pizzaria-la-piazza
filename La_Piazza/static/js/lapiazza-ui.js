document.addEventListener("DOMContentLoaded", () => {

    initNavbar();
    initMobileMenu();
    initScrollProgress();
    initRevealAnimations();
    initBackToTop();
    initToasts();
    initRippleButtons();
    initFormLoading();
});


/* =========================================================
   NAVBAR
   ========================================================= */

function initNavbar() {

    const navbar = document.querySelector(".lp-navbar");

    if (!navbar) {
        return;
    }


    const updateNavbar = () => {

        if (window.scrollY > 20) {

            navbar.classList.add(
                "is-scrolled"
            );

        } else {

            navbar.classList.remove(
                "is-scrolled"
            );

        }

    };


    updateNavbar();

    window.addEventListener(
        "scroll",
        updateNavbar,
        {
            passive: true
        }
    );

}


/* =========================================================
   MENU MOBILE
   ========================================================= */

function initMobileMenu() {

    const button = document.querySelector(
        "[data-lp-menu-toggle]"
    );

    const menu = document.querySelector(
        "[data-lp-menu]"
    );


    if (!button || !menu) {
        return;
    }


    button.addEventListener(
        "click",
        () => {

            const open = menu.classList.toggle(
                "is-open"
            );

            button.setAttribute(
                "aria-expanded",
                String(open)
            );

            button.innerHTML = open
                ? "✕"
                : "☰";

        }
    );


    menu.querySelectorAll("a").forEach(
        link => {

            link.addEventListener(
                "click",
                () => {

                    menu.classList.remove(
                        "is-open"
                    );

                    button.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                    button.innerHTML = "☰";

                }
            );

        }
    );

}


/* =========================================================
   PROGRESSO DE ROLAGEM
   ========================================================= */

function initScrollProgress() {

    const bar = document.querySelector(
        ".lp-scroll-progress"
    );


    if (!bar) {
        return;
    }


    const update = () => {

        const documentHeight =
            document.documentElement.scrollHeight -
            window.innerHeight;


        const progress =
            documentHeight <= 0
                ? 0
                : (
                    window.scrollY /
                    documentHeight
                ) * 100;


        bar.style.width =
            `${progress}%`;

    };


    update();

    window.addEventListener(
        "scroll",
        update,
        {
            passive: true
        }
    );

}


/* =========================================================
   REVEAL COM INTERSECTION OBSERVER
   ========================================================= */

function initRevealAnimations() {

    const elements = document.querySelectorAll(
        ".lp-reveal"
    );


    if (!elements.length) {
        return;
    }


    if (!("IntersectionObserver" in window)) {

        elements.forEach(
            element => {

                element.classList.add(
                    "is-visible"
                );

            }
        );

        return;
    }


    const observer = new IntersectionObserver(

        entries => {

            entries.forEach(
                entry => {

                    if (!entry.isIntersecting) {
                        return;
                    }


                    entry.target.classList.add(
                        "is-visible"
                    );


                    observer.unobserve(
                        entry.target
                    );

                }
            );

        },

        {
            threshold: 0.12
        }

    );


    elements.forEach(
        element => {

            observer.observe(
                element
            );

        }
    );

}


/* =========================================================
   VOLTAR AO TOPO
   ========================================================= */

function initBackToTop() {

    const button = document.querySelector(
        "[data-lp-back-top]"
    );


    if (!button) {
        return;
    }


    const update = () => {

        button.classList.toggle(
            "is-visible",
            window.scrollY > 450
        );

    };


    update();


    window.addEventListener(
        "scroll",
        update,
        {
            passive: true
        }
    );


    button.addEventListener(
        "click",
        () => {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        }
    );

}


/* =========================================================
   DJANGO MESSAGES COMO TOASTS
   ========================================================= */

function initToasts() {

    const toasts = document.querySelectorAll(
        ".lp-toast"
    );


    toasts.forEach(
        toast => {

            const closeButton = toast.querySelector(
                ".lp-toast-close"
            );

            const progress = toast.querySelector(
                ".lp-toast-progress"
            );


            let timer;


            const close = () => {

                clearTimeout(timer);

                toast.classList.add(
                    "is-leaving"
                );


                setTimeout(
                    () => {

                        toast.remove();

                    },
                    300
                );

            };


            if (progress) {

                progress.animate(
                    [
                        {
                            transform: "scaleX(1)"
                        },

                        {
                            transform: "scaleX(0)"
                        }
                    ],
                    {
                        duration: 5000,
                        easing: "linear"
                    }
                );

            }


            timer = setTimeout(
                close,
                5000
            );


            if (closeButton) {

                closeButton.addEventListener(
                    "click",
                    close
                );

            }

        }
    );

}


/* =========================================================
   RIPPLE NOS BOTÕES
   ========================================================= */

function initRippleButtons() {

    document.querySelectorAll(
        ".btn"
    ).forEach(
        button => {

            button.addEventListener(
                "click",
                event => {

                    const rect =
                        button.getBoundingClientRect();


                    const size =
                        Math.max(
                            rect.width,
                            rect.height
                        );


                    const ripple =
                        document.createElement(
                            "span"
                        );


                    ripple.className =
                        "lp-ripple";


                    ripple.style.width =
                        `${size}px`;

                    ripple.style.height =
                        `${size}px`;

                    ripple.style.left =
                        `${
                            event.clientX -
                            rect.left -
                            size / 2
                        }px`;

                    ripple.style.top =
                        `${
                            event.clientY -
                            rect.top -
                            size / 2
                        }px`;


                    button.appendChild(
                        ripple
                    );


                    ripple.addEventListener(
                        "animationend",
                        () => ripple.remove()
                    );

                }
            );

        }
    );

}


/* =========================================================
   LOADING AO ENVIAR FORMULÁRIOS
   ========================================================= */

function initFormLoading() {

    const loader = document.querySelector(
        "[data-lp-loader]"
    );


    if (!loader) {
        return;
    }


    document.querySelectorAll(
        "form"
    ).forEach(
        form => {

            form.addEventListener(
                "submit",
                event => {

                    /*
                     * Só mostramos o loader se o HTML
                     * estiver válido.
                     */

                    if (!form.checkValidity()) {
                        return;
                    }


                    /*
                     * Formulários marcados com
                     * data-no-loader não usam loading.
                     */

                    if (
                        form.hasAttribute(
                            "data-no-loader"
                        )
                    ) {
                        return;
                    }


                    loader.classList.add(
                        "is-active"
                    );

                }
            );

        }
    );

}