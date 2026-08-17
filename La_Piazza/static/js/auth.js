document.addEventListener("DOMContentLoaded", () => {

    initPasswordToggles();
    initPasswordStrength();
    initAuthForm();
    initAuthParticles();
    initInputEffects();

});


/* =========================================================
   MOSTRAR / OCULTAR SENHA
   ========================================================= */

function initPasswordToggles() {

    document.querySelectorAll(
        "[data-password-toggle]"
    ).forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const targetId =
                    button.dataset.passwordToggle;

                const input =
                    document.getElementById(
                        targetId
                    );

                if (!input) {
                    return;
                }


                const showing =
                    input.type === "text";


                input.type =
                    showing
                        ? "password"
                        : "text";


                const icon =
                    button.querySelector("i");


                if (icon) {

                    icon.className =
                        showing
                            ? "bi bi-eye"
                            : "bi bi-eye-slash";

                }


                button.setAttribute(
                    "aria-label",
                    showing
                        ? "Mostrar senha"
                        : "Ocultar senha"
                );

            }
        );

    });

}


/* =========================================================
   FORÇA DA SENHA
   ========================================================= */

function initPasswordStrength() {

    const password =
        document.querySelector(
            "[data-password-strength]"
        );


    const bar =
        document.getElementById(
            "passwordStrengthBar"
        );


    const label =
        document.getElementById(
            "passwordStrengthLabel"
        );


    if (
        !password
        ||
        !bar
        ||
        !label
    ) {
        return;
    }


    password.addEventListener(
        "input",
        () => {

            const value =
                password.value;


            let score = 0;


            if (value.length >= 8) {
                score++;
            }


            if (
                /[A-Z]/.test(value)
            ) {
                score++;
            }


            if (
                /[a-z]/.test(value)
            ) {
                score++;
            }


            if (
                /\d/.test(value)
            ) {
                score++;
            }


            if (
                /[^A-Za-z0-9]/.test(value)
            ) {
                score++;
            }


            updatePasswordStrength(
                score,
                value.length,
                bar,
                label
            );

        }
    );

}


function updatePasswordStrength(
    score,
    length,
    bar,
    label
) {

    if (!length) {

        bar.style.width = "0%";

        bar.dataset.level = "";

        label.textContent =
            "Digite uma senha";

        return;

    }


    const levels = [

        {
            width: "20%",
            text: "Muito fraca",
            level: "danger",
        },

        {
            width: "40%",
            text: "Fraca",
            level: "danger",
        },

        {
            width: "60%",
            text: "Razoável",
            level: "warning",
        },

        {
            width: "80%",
            text: "Boa",
            level: "good",
        },

        {
            width: "100%",
            text: "Excelente",
            level: "strong",
        },

    ];


    const item =
        levels[
            Math.max(
                0,
                score - 1
            )
        ];


    bar.style.width =
        item.width;


    bar.dataset.level =
        item.level;


    label.textContent =
        item.text;

}


/* =========================================================
   FORMULÁRIO
   ========================================================= */

function initAuthForm() {

    const forms =
        document.querySelectorAll(
            ".auth-form"
        );


    forms.forEach(form => {

        form.addEventListener(
            "submit",
            () => {

                const button =
                    form.querySelector(
                        ".auth-submit"
                    );


                if (!button) {
                    return;
                }


                if (!form.checkValidity()) {
                    return;
                }


                button.classList.add(
                    "is-loading"
                );


                button.disabled =
                    true;


                const text =
                    button.querySelector(
                        ".auth-submit-text"
                    );


                if (text) {

                    text.textContent =
                        "Aguarde...";

                }

            }
        );

    });

}


/* =========================================================
   EFEITOS NOS INPUTS
   ========================================================= */

function initInputEffects() {

    document.querySelectorAll(
        ".auth-field input"
    ).forEach(input => {

        const field =
            input.closest(
                ".auth-field"
            );


        if (!field) {
            return;
        }


        const update = () => {

            field.classList.toggle(
                "has-value",
                input.value.trim() !== ""
            );

        };


        input.addEventListener(
            "focus",
            () => {

                field.classList.add(
                    "is-focused"
                );

            }
        );


        input.addEventListener(
            "blur",
            () => {

                field.classList.remove(
                    "is-focused"
                );

                update();

            }
        );


        update();

    });

}


/* =========================================================
   PARTÍCULAS
   ========================================================= */

function initAuthParticles() {

    const container =
        document.querySelector(
            "[data-auth-particles]"
        );


    if (!container) {
        return;
    }


    const amount = 18;


    for (
        let i = 0;
        i < amount;
        i++
    ) {

        const particle =
            document.createElement(
                "span"
            );


        particle.className =
            "auth-particle";


        particle.style.left =
            `${Math.random() * 100}%`;


        particle.style.top =
            `${Math.random() * 100}%`;


        particle.style.animationDelay =
            `${Math.random() * 8}s`;


        particle.style.animationDuration =
            `${8 + Math.random() * 10}s`;


        particle.style.opacity =
            `${0.15 + Math.random() * 0.35}`;


        const size =
            2 + Math.random() * 5;


        particle.style.width =
            `${size}px`;

        particle.style.height =
            `${size}px`;


        container.appendChild(
            particle
        );

    }

}