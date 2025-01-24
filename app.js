document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('form-encuesta');
  const nombresInput = document.getElementById('nombres');
  const rucInput = document.getElementById('ruc');
  const correoInput = document.getElementById('correo');
  const crearEncuestaBtn = document.getElementById('crear-encuesta');

  // Validación en tiempo real
  function validarFormulario() {
    const nombresValido = nombresInput.value.trim() !== '';
    const rucValido = validarRUC();
    const correoValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correoInput.value.trim());

    crearEncuestaBtn.disabled = !(nombresValido && rucValido && correoValido);
  }

  // Validación específica para RUC
  function validarRUC() {
    const ruc = rucInput.value.trim();
    const rucLength = ruc.length;
    
    // Limpiar clases anteriores
    rucInput.classList.remove('borde-valido', 'borde-invalido', 'borde-pendiente');
    
    if (rucLength === 0) {
      return false;
    } else if (rucLength === 11 && /^\d+$/.test(ruc)) {
      rucInput.classList.add('borde-valido');
      return true;
    } else if (rucLength < 11) {
      rucInput.classList.add('borde-pendiente');
      return false;
    } else {
      rucInput.classList.add('borde-invalido');
      return false;
    }
  }

  // Mostrar mensajes de error
  function mostrarError(input, mensaje) {
    const errorDiv = document.getElementById(`${input.id}-error`);
    errorDiv.textContent = mensaje;
    input.classList.add('error');
  }

  // Limpiar errores
  function limpiarErrores() {
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    document.querySelectorAll('input').forEach(input => input.classList.remove('error'));
  }

  // Event listeners para validación en tiempo real
  nombresInput.addEventListener('input', validarFormulario);
  rucInput.addEventListener('input', validarFormulario);
  correoInput.addEventListener('input', validarFormulario);

  // Validación inicial
  validarFormulario();
});
