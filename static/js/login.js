document.addEventListener("DOMContentLoaded", function () {

console.log("===============================login.js cargado");

/* ===============================
   CAPTCHA – imagen
   =============================== */
const btnCaptcha = document.getElementById("btn-refresh-captcha");
const captchaImg = document.getElementById("captcha-img");

if (btnCaptcha && captchaImg) {
    btnCaptcha.addEventListener("click", function () {
        captchaImg.src = "/captcha?ts=" + Date.now();
    });
}

/* ===============================
   CONTRASEÑA – mostrar / ocultar
   =============================== */
const input = document.getElementById("clave");
const button = document.getElementById("togglePassword");
const icon = document.getElementById("iconPassword");

if (input && button && icon) {

    button.addEventListener("click", function () {
        if (input.type === "password") {
            mostrar();
        } else {
            ocultar();
        }
    });

    button.addEventListener("mousedown", mostrar);
    button.addEventListener("touchstart", mostrar);

    button.addEventListener("mouseup", ocultar);
    button.addEventListener("mouseleave", ocultar);
    button.addEventListener("touchend", ocultar);

    input.addEventListener("blur", ocultar);
}

function mostrar() {
    input.type = "text";
    icon.classList.remove("bi-eye-fill");
    icon.classList.add("bi-eye-slash-fill");
}

function ocultar() {
    input.type = "password";
    icon.classList.remove("bi-eye-slash-fill");
    icon.classList.add("bi-eye-fill");
}

});