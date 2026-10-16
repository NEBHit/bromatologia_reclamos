function validarCaracterEnNro(e){
    // Permitidos: backspace, delete, tab, escape, enter
    if ([46, 8, 9, 27, 13].includes(e.keyCode) ||
        // Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
        (e.ctrlKey && [65, 67, 86, 88].includes(e.keyCode)) ||
        // Flechas
        (e.keyCode >= 35 && e.keyCode <= 39)) {
        return;
    }

    // Si no es un número (tecla 0-9), prevenimos el evento
    if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) &&
        (e.keyCode < 96 || e.keyCode > 105)) {
        e.preventDefault();
    }
};

function validarLongitudNro(e, maxLength){ 
    let valor = e.target.value;

    // Elimina todo lo que no sea dígito
    valor = valor.replace(/\D/g, '');

    // Limita a 7 dígitos
    if (valor.length > maxLength) {
        valor = valor.slice(0, maxLength);
    }

    e.target.value = valor;
};