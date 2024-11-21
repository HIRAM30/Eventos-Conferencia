// Función para mostrar una alerta
function showAlert(message, type = 'info') {
    const alerta = document.createElement('div');
    alerta.classList.add('alerta', type, 'show');
    alerta.innerHTML = `
        <span>${message}</span>
        <button class="close-btn" onclick="closeAlert(this)">X</button>
    `;
    document.body.appendChild(alerta);

    // Ocultar la alerta después de 5 segundos
    setTimeout(() => {
        alerta.classList.remove('show');
        setTimeout(() => alerta.remove(), 500); // Eliminar el elemento después de la animación
    }, 5000);
}

// Función para cerrar la alerta
function closeAlert(button) {
    const alerta = button.parentElement;
    alerta.classList.remove('show');
    setTimeout(() => alerta.remove(), 500); // Eliminar el elemento después de la animación
}
