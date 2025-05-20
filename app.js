const PYTHON_GOOGLE_MOCK = `
import sys
from unittest import mock

google_mock = mock.MagicMock()
google_mock.files.upload.return_value.popitem.return_value = ["examen.txt", None]
sys.modules['google.colab'] = google_mock
`
const OUTPUT_FILENAMES = {
    'papel.py': 'output.txt',
    'moodle.py': 'salida.xml'
}
const SCRIPTS = {};
const statusEl = document.getElementById('status');
var pyodide = null;
// Variables para imágenes asociadas a preguntas
const imagenesSubidas = {};
const asignacionImagenes = {};
let preguntasCargadas = [];


// Elementos DOM para navegación entre pasos
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const step4 = document.getElementById('step4');
const step1Nav = document.getElementById('step1-nav');
const step2Nav = document.getElementById('step2-nav');
const step3Nav = document.getElementById('step3-nav');
const step4Nav = document.getElementById('step4-nav');

// Botones de navegación
const btnToStep2 = document.getElementById('btn-to-step2');
const btnToStep1FromStep2 = document.getElementById('btn-to-step1-from-2');
const btnToStep3 = document.getElementById('btn-to-step3');
const btnToStep2FromStep3 = document.getElementById('btn-to-step2-from-3');
const btnToStep4 = document.getElementById('btn-to-step4');
const btnToStep3FromStep4 = document.getElementById('btn-to-step3-from-4');

// Elementos para los tipos de preguntas
const multirespuestaInput = document.getElementById('multirespuesta');
const verdaderoFalsoInput = document.getElementById('verdadero_falso');
const respuestaCortaInput = document.getElementById('respuesta_corta');
const rellenarEspaciosInput = document.getElementById('rellenar_espacios');

// Elementos para la configuración de cada tipo
const multirespuestaConfig = document.getElementById('multirespuesta-config');
const verdaderoFalsoConfig = document.getElementById('verdadero_falso-config');
const respuestaCortaConfig = document.getElementById('respuesta_corta-config');
const rellenarEspaciosConfig = document.getElementById('rellenar_espacios-config');

// Elementos para el generador de prompt
const generarPromptBtn = document.getElementById('generar-prompt');
const copyPromptBtn = document.getElementById('copy-prompt');
const promptOutput = document.getElementById('prompt-output');
const promptContainer = document.getElementById('prompt-container');

// Estilos CSS para los modos de generación
document.head.insertAdjacentHTML('beforeend', `
<style>
.opciones-modo {
    margin-top: 15px;
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 5px;
    border-left: 3px solid #1095c1;
}

/* Mejora visual para las opciones */
fieldset {
    margin-bottom: 1rem;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
}

legend {
    font-weight: bold;
    padding: 0 0.5rem;
}

small {
    display: block;
    margin-top: 0.25rem;
    color: #666;
}

/* Resaltar inputs numéricos */
input[type="number"] {
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 0.5rem;
}

input[type="number"]:focus {
    border-color: #1095c1;
    box-shadow: 0 0 0 2px rgba(16, 149, 193, 0.2);
}
</style>
`);

const loadingTimeout = setTimeout(function () {
    const statusEl = document.getElementById('status');
    const errorMessageEl = document.getElementById('error-message');

    // Si después de 10 segundos todavía está cargando, mostrar mensaje de error
    if (statusEl && !statusEl.hidden) {
        if (errorMessageEl) errorMessageEl.classList.remove('hidden');
        console.error("Timeout durante la carga de scripts o Pyodide");
    }
}, 10000);


// Cargar los scripts y Pyodide
Promise.all([
    fetch('papel.py').then(res => res.text()).catch(err => {
        console.error("Error al cargar papel.py:", err);
        return null;
    }),
    fetch('moodle.py').then(res => res.text()).catch(err => {
        console.error("Error al cargar moodle.py:", err);
        return null;
    }),
    fetch('papel.py').then(res => res.text()).catch(() => null),
    fetch('moodle.py').then(res => res.text()).catch(() => null),
    loadPyodide().catch(err => {
        console.error("Error al cargar Pyodide:", err);
        throw err; // Propagar el error para manejarlo en el catch general
    }),
]).then(([papel, moodle, papelEnhanced, moodleEnhanced, _pyodide]) => {
    // Cancelar el timeout ya que la carga fue exitosa
    clearTimeout(loadingTimeout);

    // Comprobar si los scripts principales se cargaron correctamente
    if (!papel || !moodle) {
        throw new Error("No se pudieron cargar los scripts principales");
    }

    // Guardar los scripts originales
    SCRIPTS['papel.py'] = papel;
    SCRIPTS['moodle.py'] = moodle;

    // Guardar los scripts mejorados si existen
    if (papelEnhanced) SCRIPTS['papel.py'] = papelEnhanced;
    if (moodleEnhanced) SCRIPTS['moodle.py'] = moodleEnhanced;

    // Habilitar la interfaz
    step1.classList.remove('hidden');
    statusEl.hidden = true;

    // Asignar pyodide
    pyodide = _pyodide;
    console.log("Pyodide ready");

}).catch(error => {
    // Cancelar el timeout en caso de error
    clearTimeout(loadingTimeout);

    // Mostrar mensaje de error
    const statusEl = document.getElementById('status');
    const errorMessageEl = document.getElementById('error-message');

    if (statusEl) statusEl.innerHTML = "Error al cargar. Por favor, recargue la página.";
    if (errorMessageEl) errorMessageEl.classList.remove('hidden');

    console.error("Error durante la inicialización:", error);
});

// Función para actualizar la visibilidad de las configuraciones
function updateConfigVisibility() {
    // Mostrar/ocultar configuraciones según los tipos de preguntas seleccionados
    multirespuestaConfig.classList.toggle('hidden', parseInt(multirespuestaInput.value) <= 0);
    verdaderoFalsoConfig.classList.toggle('hidden', parseInt(verdaderoFalsoInput.value) <= 0);
    respuestaCortaConfig.classList.toggle('hidden', parseInt(respuestaCortaInput.value) <= 0);
    rellenarEspaciosConfig.classList.toggle('hidden', parseInt(rellenarEspaciosInput.value) <= 0);
}

// Event listeners para los inputs de tipos de preguntas
[multirespuestaInput, verdaderoFalsoInput, respuestaCortaInput, rellenarEspaciosInput].forEach(input => {
    input.addEventListener('change', updateConfigVisibility);
});

// NUEVO: Funciones para gestionar modos de generación
// Funciones para alternar entre modos de generación en la pestaña Tema
function toggleModoGeneracionTema() {
    const modoSeleccionado = document.querySelector('input[name="modo_generacion_tema"]:checked').value;
    const opcionesExamenesSeparados = document.getElementById('examenes-separados-tema');
    const opcionesPreguntasAdicionales = document.getElementById('preguntas-adicionales-tema');
    
    if (modoSeleccionado === 'examenes_separados') {
        opcionesExamenesSeparados.classList.remove('hidden');
        opcionesPreguntasAdicionales.classList.add('hidden');
    } else {
        opcionesExamenesSeparados.classList.add('hidden');
        opcionesPreguntasAdicionales.classList.remove('hidden');
    }
}

// Función para alternar entre modos de generación en la pestaña Apuntes
function toggleModoGeneracionApuntes() {
    const modoSeleccionado = document.querySelector('input[name="modo_generacion_apuntes"]:checked').value;
    const opcionesExamenesSeparados = document.getElementById('examenes-separados-apuntes');
    const opcionesPreguntasAdicionales = document.getElementById('preguntas-adicionales-apuntes');
    
    if (modoSeleccionado === 'examenes_separados') {
        opcionesExamenesSeparados.classList.remove('hidden');
        opcionesPreguntasAdicionales.classList.add('hidden');
    } else {
        opcionesExamenesSeparados.classList.add('hidden');
        opcionesPreguntasAdicionales.classList.remove('hidden');
    }
}

// Inicializar valores para las preguntas adicionales según las preguntas base
function updateAdditionalQuestions() {
    const multiBase = parseInt(multirespuestaInput.value) || 0;
    const vfBase = parseInt(verdaderoFalsoInput.value) || 0;
    const rcBase = parseInt(respuestaCortaInput.value) || 0;
    const reBase = parseInt(rellenarEspaciosInput.value) || 0;
    
    // Actualizar valores mínimos para ambos paneles
    
    // Panel de tema
    const multiAdicionalesTema = document.getElementById('multi_adicionales_tema');
    const vfAdicionalesTema = document.getElementById('vf_adicionales_tema');
    const rcAdicionalesTema = document.getElementById('rc_adicionales_tema');
    const reAdicionalesTema = document.getElementById('re_adicionales_tema');
    
    if (multiAdicionalesTema) {
        multiAdicionalesTema.placeholder = "Número de preguntas adicionales";
        multiAdicionalesTema.min = 0; // Establecer el mínimo como atributo
        if (multiAdicionalesTema.value === "" || isNaN(parseInt(multiAdicionalesTema.value))) {
            multiAdicionalesTema.value = "0"; // Valor por defecto sensato
        }
    }
    
    if (vfAdicionalesTema) {
        vfAdicionalesTema.placeholder = "Número de preguntas adicionales";
        vfAdicionalesTema.min = 0;
        if (vfAdicionalesTema.value === "" || isNaN(parseInt(vfAdicionalesTema.value))) {
            vfAdicionalesTema.value = "0";
        }
    }
    
    if (rcAdicionalesTema) {
        rcAdicionalesTema.placeholder = "Número de preguntas adicionales";
        rcAdicionalesTema.min = 0;
        if (rcAdicionalesTema.value === "" || isNaN(parseInt(rcAdicionalesTema.value))) {
            rcAdicionalesTema.value = "0";
        }
    }
    
    if (reAdicionalesTema) {
        reAdicionalesTema.placeholder = "Número de preguntas adicionales";
        reAdicionalesTema.min = 0;
        if (reAdicionalesTema.value === "" || isNaN(parseInt(reAdicionalesTema.value))) {
            reAdicionalesTema.value = "0";
        }
    }
    
    // Panel de apuntes
    const multiAdicionalesApuntes = document.getElementById('multi_adicionales_apuntes');
    const vfAdicionalesApuntes = document.getElementById('vf_adicionales_apuntes');
    const rcAdicionalesApuntes = document.getElementById('rc_adicionales_apuntes');
    const reAdicionalesApuntes = document.getElementById('re_adicionales_apuntes');
    
    if (multiAdicionalesApuntes) {
        multiAdicionalesApuntes.placeholder = "Número de preguntas adicionales";
        multiAdicionalesApuntes.min = 0;
        if (multiAdicionalesApuntes.value === "" || isNaN(parseInt(multiAdicionalesApuntes.value))) {
            multiAdicionalesApuntes.value = "0";
        }
    }
    
    if (vfAdicionalesApuntes) {
        vfAdicionalesApuntes.placeholder = "Número de preguntas adicionales";
        vfAdicionalesApuntes.min = 0;
        if (vfAdicionalesApuntes.value === "" || isNaN(parseInt(vfAdicionalesApuntes.value))) {
            vfAdicionalesApuntes.value = "0";
        }
    }
    
    if (rcAdicionalesApuntes) {
        rcAdicionalesApuntes.placeholder = "Número de preguntas adicionales";
        rcAdicionalesApuntes.min = 0;
        if (rcAdicionalesApuntes.value === "" || isNaN(parseInt(rcAdicionalesApuntes.value))) {
            rcAdicionalesApuntes.value = "0";
        }
    }
    
    if (reAdicionalesApuntes) {
        reAdicionalesApuntes.placeholder = "Número de preguntas adicionales";
        reAdicionalesApuntes.min = 0;
        if (reAdicionalesApuntes.value === "" || isNaN(parseInt(reAdicionalesApuntes.value))) {
            reAdicionalesApuntes.value = "0";
        }
    }
}

// Event listeners para navegación entre pasos - REORDENADOS
if (btnToStep2) {
    btnToStep2.addEventListener('click', () => {
        // Validar que haya al menos una pregunta seleccionada
        const totalQuestions = parseInt(multirespuestaInput.value) +
            parseInt(verdaderoFalsoInput.value) +
            parseInt(respuestaCortaInput.value) +
            parseInt(rellenarEspaciosInput.value);

        if (totalQuestions <= 0) {
            alert('Debe seleccionar al menos un tipo de pregunta');
            return;
        }

        // Cambiar paso - IR DIRECTO AL PASO 2 (Caracterización)
        step1.classList.add('hidden');
        step2.classList.remove('hidden');
        step1Nav.classList.remove('active');
        step2Nav.classList.add('active');
        
        // Actualizar la visibilidad de las configuraciones
        updateConfigVisibility();
    });
}

if (btnToStep1FromStep2) {
    btnToStep1FromStep2.addEventListener('click', () => {
        step2.classList.add('hidden');
        step1.classList.remove('hidden');
        step2Nav.classList.remove('active');
        step1Nav.classList.add('active');
    });
}

if (btnToStep3) {
    btnToStep3.addEventListener('click', () => {
        // Cambiar paso - IR AL PASO 3 (Generación con IA)
        step2.classList.add('hidden');
        step3.classList.remove('hidden');
        step2Nav.classList.remove('active');
        step3Nav.classList.add('active');
    });
}

if (btnToStep2FromStep3) {
    btnToStep2FromStep3.addEventListener('click', () => {
        step3.classList.add('hidden');
        step2.classList.remove('hidden');
        step3Nav.classList.remove('active');
        step2Nav.classList.add('active');
    });
}

if (btnToStep4) {
    btnToStep4.addEventListener('click', () => {
        step3.classList.add('hidden');
        step4.classList.remove('hidden');
        step3Nav.classList.remove('active');
        step4Nav.classList.add('active');
    });
}

if (btnToStep3FromStep4) {
    btnToStep3FromStep4.addEventListener('click', (e) => {
        // Añadir prevención por defecto para evitar cualquier comportamiento de envío de formulario
        e.preventDefault();

        // Solo cambiar de pantalla, sin generar el examen
        step4.classList.add('hidden');
        step3.classList.remove('hidden');
        step4Nav.classList.remove('active');
        step3Nav.classList.add('active');
    });
}

// Gestión de la interfaz para la generación de prompts
document.querySelectorAll('.panel-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        // Desactivar todas las pestañas y contenidos
        document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.panel-content').forEach(p => p.classList.remove('active'));
        
        // Activar la pestaña seleccionada y su contenido
        this.classList.add('active');
        const panelId = this.getAttribute('data-panel');
        document.getElementById(panelId).classList.add('active');
    });
});

// Listener para el botón de generar prompt
if (generarPromptBtn) {
    generarPromptBtn.addEventListener('click', generarPrompt);
}

// Listener para el botón de copiar prompt
if (copyPromptBtn) {
    copyPromptBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(promptOutput.textContent);
            copyPromptBtn.textContent = '¡Copiado!';
            setTimeout(() => {
                copyPromptBtn.textContent = 'Copiar al portapapeles';
            }, 2000);
        } catch (err) {
            console.error('Error al copiar: ', err);
            copyPromptBtn.textContent = 'Error al copiar';
            setTimeout(() => {
                copyPromptBtn.textContent = 'Copiar al portapapeles';
            }, 2000);
        }
    });
}

// Inicializar el apuntesContent como un objeto simulado para evitar errores
const apuntesContent = "PLACEHOLDER";

// Añadir event listeners después de que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar los modos de generación
    if (document.querySelector('input[name="modo_generacion_tema"]')) {
        toggleModoGeneracionTema();
        
        // Añadir listeners para los cambios en los radio buttons
        document.querySelectorAll('input[name="modo_generacion_tema"]').forEach(radio => {
            radio.addEventListener('change', toggleModoGeneracionTema);
        });
    }
    
    if (document.querySelector('input[name="modo_generacion_apuntes"]')) {
        toggleModoGeneracionApuntes();
        
        // Añadir listeners para los cambios en los radio buttons
        document.querySelectorAll('input[name="modo_generacion_apuntes"]').forEach(radio => {
            radio.addEventListener('change', toggleModoGeneracionApuntes);
        });
    }
    
    // Escuchar cambios en los valores base para actualizar los campos de adicionales
    if (multirespuestaInput && verdaderoFalsoInput && respuestaCortaInput && rellenarEspaciosInput) {
        [multirespuestaInput, verdaderoFalsoInput, respuestaCortaInput, rellenarEspaciosInput].forEach(input => {
            input.addEventListener('change', updateAdditionalQuestions);
        });
        
        // Ejecutar una vez para inicializar
        updateAdditionalQuestions();
    }

    // Inicializar estados de penalización
    togglePenalizacionConfig('multi');
    togglePenalizacionConfig('vf');

    // Asegurarse de que los radio buttons tengan listeners para cambios
    document.querySelectorAll('input[name="penalizacion_multi"], input[name="penalizacion_vf"]').forEach(radio => {
        radio.addEventListener('change', function () {
            togglePenalizacionConfig(this.name.split('_')[1]);
        });
    });
    // Cargar preguntas del archivo
const entradaInput = document.getElementById('entrada');
entradaInput.addEventListener('change', (e) => {
  const archivo = e.target.files[0];
  if (!archivo) return;
// Capturar imágenes seleccionadas por pregunta
preguntasCargadas.forEach((pregunta, idx) => {
    const select = document.getElementById(`select-img-${idx}`);
    asignacionImagenes[pregunta] = select.value || null;
  });
  
  const reader = new FileReader();
  reader.onload = function(evt) {
    const contenido = evt.target.result;
    preguntasCargadas = contenido.split('\n').filter(linea => linea.trim() !== '');
    mostrarAsignacionImagenes();
  };
  reader.readAsText(archivo);
});



// Mostrar select de imágenes para cada pregunta
function mostrarAsignacionImagenes() {
  const contenedor = document.getElementById('asignacion-imagenes');
  if (!contenedor) return;
  contenedor.innerHTML = '';

  if (preguntasCargadas.length === 0) return;

  preguntasCargadas.forEach((pregunta, idx) => {
    const div = document.createElement('div');
    div.style.marginBottom = '1rem';

    div.innerHTML = `
      <label><strong>Pregunta:</strong> ${pregunta}</label><br>
      <select id="select-img-${idx}">
        <option value="">-- Sin imagen --</option>
        ${Object.keys(imagenesSubidas).map(img => `<option value="${img}">${img}</option>`).join('')}
      </select>
    `;
    contenedor.appendChild(div);
  });
}

    // Generar el examen al enviar el formulario
    var form = document.getElementById('exam-form');
    if (form) {
        form.addEventListener("submit", processForm);
    }
});

// Función para generar el prompt optimizado
function generarPrompt() {
    // Obtener los tipos de preguntas seleccionados
    const multirespuesta = parseInt(multirespuestaInput.value) || 0;
    const verdaderoFalso = parseInt(verdaderoFalsoInput.value) || 0;
    const respuestaCorta = parseInt(respuestaCortaInput.value) || 0;
    const rellenarEspacios = parseInt(rellenarEspaciosInput.value) || 0;
    
    // Verificar que se ha seleccionado al menos un tipo de pregunta
    const totalPreguntas = multirespuesta + verdaderoFalso + respuestaCorta + rellenarEspacios;
    if (totalPreguntas <= 0) {
        alert('Por favor, seleccione al menos un tipo de pregunta.');
        return;
    }
    
    // Comprobar qué panel está activo
    const porTema = document.querySelector('.panel-tab[data-panel="tema-panel"]').classList.contains('active');
    const porApuntes = document.querySelector('.panel-tab[data-panel="apuntes-panel"]').classList.contains('active');
    
    // Obtener el número de opciones para las preguntas de opción múltiple
    const numOpcionesMulti = parseInt(document.getElementById('opciones_multirespuesta').value) || 4;
    
    let prompt = '';
    
    // Variables para modo de generación y cantidad de preguntas
    let modoGeneracion;
    let numExamenes = 1;
    let multiTotal, vfTotal, rcTotal, reTotal;
    
    if (porTema) {
        // Obtener modo de generación
        modoGeneracion = document.querySelector('input[name="modo_generacion_tema"]:checked').value;
        
        if (modoGeneracion === 'examenes_separados') {
            numExamenes = parseInt(document.getElementById('num_examenes').value) || 1;
            multiTotal = multirespuesta * numExamenes;
            vfTotal = verdaderoFalso * numExamenes;
            rcTotal = respuestaCorta * numExamenes;
            reTotal = rellenarEspacios * numExamenes;
        } else {
// Modo banco de preguntas - SUMAR el valor base y el adicional
multiTotal = multirespuesta + (parseInt(document.getElementById('multi_adicionales_tema').value) || 0);
vfTotal = verdaderoFalso + (parseInt(document.getElementById('vf_adicionales_tema').value) || 0);
rcTotal = respuestaCorta + (parseInt(document.getElementById('rc_adicionales_tema').value) || 0);
reTotal = rellenarEspacios + (parseInt(document.getElementById('re_adicionales_tema').value) || 0);
        }
        
        // Obtener datos del panel por tema
        const tema = document.getElementById('tema').value.trim();
        const dificultad = document.getElementById('dificultad').value;
        const indicaciones = document.getElementById('indicaciones-adicionales').value.trim();
        
        if (!tema) {
            alert('Por favor, especifique un tema para generar el prompt.');
            return;
        }
        
        // Construir el encabezado del prompt
        if (modoGeneracion === 'examenes_separados') {
            prompt = `Actúa como un experto en ${tema} y en diseño de preguntas de examen. Necesito crear ${numExamenes > 1 ? numExamenes + ' exámenes diferentes' : 'un examen'} sobre "${tema}" con una dificultad ${getDificultadTexto(dificultad)}.`;
        } else {
            prompt = `Actúa como un experto en ${tema} y en diseño de preguntas de examen. Necesito crear un banco de preguntas sobre "${tema}" con una dificultad ${getDificultadTexto(dificultad)}.`;
        }
        
        if (indicaciones) {
            prompt += `\n\nConsideraciones específicas: ${indicaciones}`;
        }
    } else if (porApuntes) {
        // Obtener modo de generación
        modoGeneracion = document.querySelector('input[name="modo_generacion_apuntes"]:checked').value;
        
        if (modoGeneracion === 'examenes_separados') {
            numExamenes = parseInt(document.getElementById('num_examenes_apuntes').value) || 1;
            multiTotal = multirespuesta * numExamenes;
            vfTotal = verdaderoFalso * numExamenes;
            rcTotal = respuestaCorta * numExamenes;
            reTotal = rellenarEspacios * numExamenes;
        } else {
// Modo banco de preguntas - CAMBIO: ahora sumamos el valor base y el adicional
multiTotal = multirespuesta + parseInt(document.getElementById('multi_adicionales_apuntes').value) || multirespuesta;
vfTotal = verdaderoFalso + parseInt(document.getElementById('vf_adicionales_apuntes').value) || verdaderoFalso;
rcTotal = respuestaCorta + parseInt(document.getElementById('rc_adicionales_apuntes').value) || respuestaCorta;
reTotal = rellenarEspacios + parseInt(document.getElementById('re_adicionales_apuntes').value) || rellenarEspacios;
        }
        
        // Prompt para generación basada en apuntes
        const instruccionesApuntes = document.getElementById('instrucciones-apuntes').value.trim();
        
        if (modoGeneracion === 'examenes_separados') {
            prompt = `Actúa como un profesor experto en diseño de preguntas de examen. Necesito crear ${numExamenes > 1 ? numExamenes + ' exámenes diferentes' : 'un examen'} basado EXCLUSIVAMENTE en los apuntes que proporcionaré junto con este prompt.\n\n`;
        } else {
            prompt = `Actúa como un profesor experto en diseño de preguntas de examen. Necesito crear un banco de preguntas basado EXCLUSIVAMENTE en los apuntes que proporcionaré junto con este prompt.\n\n`;
        }
        
        prompt += "IMPORTANTE: Las preguntas y respuestas deben extraerse ÚNICAMENTE del contenido de los apuntes que te proporcionaré, sin añadir información externa ni inventada. Usa solo los conceptos, definiciones, ejemplos y explicaciones que aparecen en el material que te facilitaré.";
        
        if (instruccionesApuntes) {
            prompt += `\n\nConsideraciones adicionales: ${instruccionesApuntes}`;
        }
    }

   
    
    
    // Añadir instrucciones sobre los tipos de preguntas requeridas
    prompt += "\n\n**REQUISITO CRÍTICO:** El formato de cada pregunta DEBE seguirse EXACTAMENTE como se indica, ya que el texto será procesado automáticamente por un sistema.";
    
    prompt += "\n\nNecesito que generes las siguientes preguntas con sus respuestas";
    
    if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
        prompt += `, distribuidas igualmente entre los ${numExamenes} exámenes:`;
    } else if (modoGeneracion === 'preguntas_adicionales') {
        prompt += " para mi banco de preguntas:";
    } else {
        prompt += ":";
    }
    
    const tiposPreguntas = [];
    if (multiTotal > 0) {
        if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
            tiposPreguntas.push(`- ${multiTotal} preguntas de opción múltiple (${multirespuesta} por examen)`);
        } else {
            tiposPreguntas.push(`- ${multiTotal} preguntas de opción múltiple`);
        }
    }
    
    if (vfTotal > 0) {
        if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
            tiposPreguntas.push(`- ${vfTotal} preguntas de verdadero/falso (${verdaderoFalso} por examen)`);
        } else {
            tiposPreguntas.push(`- ${vfTotal} preguntas de verdadero/falso`);
        }
    }
    
    if (rcTotal > 0) {
        if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
            tiposPreguntas.push(`- ${rcTotal} preguntas de respuesta corta (${respuestaCorta} por examen)`);
        } else {
            tiposPreguntas.push(`- ${rcTotal} preguntas de respuesta corta`);
        }
    }
    
    if (reTotal > 0) {
        if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
            tiposPreguntas.push(`- ${reTotal} preguntas de rellenar espacios (${rellenarEspacios} por examen)`);
        } else {
            tiposPreguntas.push(`- ${reTotal} preguntas de rellenar espacios`);
        }
    }
    
    prompt += "\n" + tiposPreguntas.join("\n");
    
    // Añadir énfasis en la cantidad exacta de preguntas
    prompt += "\n\n**MUY IMPORTANTE: Debes generar EXACTAMENTE el número de preguntas solicitado para cada tipo.** No generes menos preguntas de las indicadas para ningún tipo. Para este examen se requiere específicamente:";
    prompt += "\n- Opción múltiple: EXACTAMENTE " + multiTotal;
    if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
        prompt += ` (${multirespuesta} por examen)`;
    }
    
    prompt += "\n- Verdadero/Falso: EXACTAMENTE " + vfTotal;
    if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
        prompt += ` (${verdaderoFalso} por examen)`;
    }
    
    prompt += "\n- Respuesta corta: EXACTAMENTE " + rcTotal;
    if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
        prompt += ` (${respuestaCorta} por examen)`;
    }
    
    prompt += "\n- Rellenar espacios: EXACTAMENTE " + reTotal;
    if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
        prompt += ` (${rellenarEspacios} por examen)`;
    }
    
    // Añadir la instrucción crucial para NO incluir encabezados
    prompt += "\n\n**NO INCLUYAS ENCABEZADOS ni separadores de sección como \"## Preguntas de opción múltiple ##\" en el resultado final.**";
    
    // Instrucciones detalladas sobre el formato exacto
    prompt += "\n\n### FORMATO EXACTO PARA CADA TIPO DE PREGUNTA:";
    
    if (multiTotal > 0) {
        prompt += `\n\n**Opción múltiple:**
\`\`\`
[Enunciado de la pregunta]
$$$[Respuesta correcta]
[Opción incorrecta 1]
[Opción incorrecta 2]
${numOpcionesMulti >= 4 ? "[Opción incorrecta 3]\n" : ""}${numOpcionesMulti >= 5 ? "[Opción incorrecta 4]\n" : ""}${numOpcionesMulti >= 6 ? "[Opción incorrecta 5]\n" : ""}
\`\`\``;

        prompt += `\n\nCADA pregunta de opción múltiple debe tener EXACTAMENTE ${numOpcionesMulti} opciones (1 correcta y ${numOpcionesMulti-1} incorrectas).`;
    }
    
    if (vfTotal > 0) {
        prompt += `\n\n**Verdadero/Falso:**
\`\`\`
[Enunciado de la afirmación]
$$$Verdadero
Falso

\`\`\`
O:
\`\`\`
[Enunciado de la afirmación]
$$$Falso
Verdadero

\`\`\``;
    }
    
    if (rcTotal > 0) {
        prompt += `\n\n**Respuesta corta:**
\`\`\`
[Enunciado de la pregunta]
$$$[Respuesta correcta]

\`\`\``;

        // Siempre forzar respuestas de una sola palabra
        prompt += "\n\nLas respuestas a las preguntas de respuesta corta deben ser SIEMPRE de UNA SOLA PALABRA, concisa y específica.";
    }
    
    if (reTotal > 0) {
        prompt += `\n\n**Rellenar espacios:**
\`\`\`
Complete la frase: [primera parte de la frase] _____ [resto de la frase si aplica].
$$$[Palabra o frase que debe ir en el espacio]

\`\`\``;
    }
    
    // Reglas críticas que debe seguir
    prompt += "\n\n### REGLAS CRÍTICAS (LEER ANTES DE GENERAR):";
    prompt += "\n\n1. Separa cada pregunta con EXACTAMENTE UNA línea en blanco.";
    prompt += "\n2. NO numeres las preguntas.";
    prompt += "\n3. NO incluyas encabezados, títulos o textos introductorios.";
    prompt += "\n4. Marca SIEMPRE la respuesta correcta con exactamente tres símbolos de dólar (\"$$$\") sin espacios antes.";
    prompt += "\n5. Para las preguntas de verdadero/falso, utiliza SOLO las palabras \"Verdadero\" y \"Falso\" como opciones.";
    prompt += "\n6. Para las preguntas de rellenar espacios, usa EXACTAMENTE 5 guiones bajos (_____) para indicar el espacio.";
    prompt += "\n7. Las respuestas de las preguntas de respuesta corta DEBEN ser DE UNA SOLA PALABRA.";
    prompt += "\n8. No uses formatos especiales como negritas, cursivas o listas numeradas.";
    
    if (modoGeneracion === 'examenes_separados' && numExamenes > 1) {
        prompt += "\n9. Crea preguntas diferentes para cada uno de los exámenes, evitando repeticiones.";
    }
    
    // Añadir ejemplo de formato correcto
    prompt += "\n\n### EJEMPLO DE FORMATO CORRECTO PARA TODOS LOS TIPOS:";
    prompt += "\n\n```";
    
    // Ejemplo de pregunta de opción múltiple con el número correcto de opciones
    prompt += "\n¿Qué palabra clave se utiliza para heredar una clase en Java?";
    prompt += "\n$$$extends";
    prompt += "\nimplements";
    prompt += "\ninherits";
    if (numOpcionesMulti >= 4) prompt += "\nsuper";
    if (numOpcionesMulti >= 5) prompt += "\nthis";
    if (numOpcionesMulti >= 6) prompt += "\nclass";
    prompt += "\n";
    
    // Resto de ejemplos
    prompt += "\nEn Java, una clase puede heredar de múltiples clases directamente.";
    prompt += "\n$$$Falso";
    prompt += "\nVerdadero";
    prompt += "\n";
    
    prompt += "\n¿Qué palabra clave se utiliza para crear un nuevo objeto en Java?";
    prompt += "\n$$$new";
    prompt += "\n";
    
    prompt += "\nComplete la frase: En Java, una clase puede implementar múltiples _____ interfaces.";
    prompt += "\n$$$interfaces";
    prompt += "\n```";
    
    // Nota final importante
    prompt += "\n\n**NOTA FINAL:** El archivo .txt resultante será procesado automáticamente, por lo que seguir este formato AL PIE DE LA LETRA es ESENCIAL. No incluyas ningún texto adicional, explicación o nota antes o después de las preguntas.";
    

    // Mostrar el prompt generado
    promptOutput.textContent = prompt;
    promptContainer.classList.remove('hidden');
}
// Función para preparar el contenido del examen según la configuración
function prepareExamContent(inputContent, config) {
    // Validar que el archivo contiene preguntas en formato válido
    if (!inputContent.includes('$$$')) {
        alert('Advertencia: No se encontraron respuestas marcadas con "$$$". ' +
            'Asegúrese de que su archivo sigue el formato correcto.');
        return inputContent;
    }

    // Analizar el contenido para detectar cada tipo de pregunta
    let tiposPreguntasEncontrados = detectarTiposPreguntas(inputContent);
    
    // Verificar que todos los tipos de preguntas solicitados estén presentes
    let tiposFaltantes = [];
    if (config.questionTypes.multirespuesta > 0 && tiposPreguntasEncontrados["opción múltiple"] === 0) {
        tiposFaltantes.push("opción múltiple");
    }
    if (config.questionTypes.verdaderoFalso > 0 && tiposPreguntasEncontrados["verdadero/falso"] === 0) {
        tiposFaltantes.push("verdadero/falso");
    }
    if (config.questionTypes.respuestaCorta > 0 && tiposPreguntasEncontrados["respuesta corta"] === 0) {
        tiposFaltantes.push("respuesta corta");
    }
    if (config.questionTypes.rellenarEspacios > 0 && tiposPreguntasEncontrados["rellenar espacios"] === 0) {
        tiposFaltantes.push("rellenar espacios");
    }
    
    if (tiposFaltantes.length > 0) {
        throw new Error(
            `No se encontraron preguntas de los siguientes tipos: ${tiposFaltantes.join(', ')}.\n\n` +
            `Por favor, sube un archivo que contenga preguntas de esos tipos o modifica la configuración del examen.`
        );
    }
    

    // Contar el número total de preguntas detectadas
    const totalPreguntasDetectadas = 
        tiposPreguntasEncontrados["opción múltiple"] +
        tiposPreguntasEncontrados["verdadero/falso"] +
        tiposPreguntasEncontrados["respuesta corta"] +
        tiposPreguntasEncontrados["rellenar espacios"];
    
    const totalPreguntasRequeridas =
        config.questionTypes.multirespuesta +
        config.questionTypes.verdaderoFalso +
        config.questionTypes.respuestaCorta +
        config.questionTypes.rellenarEspacios;

    // Solo mostrar advertencia si faltan preguntas y no hay errores de detección 
    // (para evitar mensajes confusos)
    if (totalPreguntasDetectadas < totalPreguntasRequeridas && tiposFaltantes.length === 0) {
        // Mostrar detalles de las preguntas encontradas vs. solicitadas
        console.log("Preguntas detectadas:", tiposPreguntasEncontrados);
        console.log("Preguntas requeridas:", {
            "opción múltiple": config.questionTypes.multirespuesta,
            "verdadero/falso": config.questionTypes.verdaderoFalso,
            "respuesta corta": config.questionTypes.respuestaCorta, 
            "rellenar espacios": config.questionTypes.rellenarEspacios
        });
        
        // Mensaje más descriptivo
        let mensaje = `Advertencia: Se solicitaron ${totalPreguntasRequeridas} preguntas en total, pero se encontraron ${totalPreguntasDetectadas}.\n\n`;
        mensaje += "Desglose de preguntas encontradas:\n";
        mensaje += `- Opción múltiple: ${tiposPreguntasEncontrados["opción múltiple"]} de ${config.questionTypes.multirespuesta} solicitadas\n`;
        mensaje += `- Verdadero/Falso: ${tiposPreguntasEncontrados["verdadero/falso"]} de ${config.questionTypes.verdaderoFalso} solicitadas\n`;
        mensaje += `- Respuesta corta: ${tiposPreguntasEncontrados["respuesta corta"]} de ${config.questionTypes.respuestaCorta} solicitadas\n`;
        mensaje += `- Rellenar espacios: ${tiposPreguntasEncontrados["rellenar espacios"]} de ${config.questionTypes.rellenarEspacios} solicitadas\n\n`;
        mensaje += "Se utilizarán todas las preguntas disponibles para generar el examen.";
        
        alert(mensaje);
    }

    return inputContent;
}

// Función para detectar tipos de preguntas en el contenido de forma más robusta
function detectarTiposPreguntas(contenido) {
    // Dividir por líneas en blanco y filtrar líneas vacías al inicio/fin
    const bloquesDeTexto = contenido.split(/\n\s*\n/)
        .filter(bloque => bloque.trim().length > 0);
    
    let tiposPreguntasEncontrados = {
        "opción múltiple": 0,
        "verdadero/falso": 0,
        "respuesta corta": 0,
        "rellenar espacios": 0
    };

    for (const bloque of bloquesDeTexto) {
        const lineas = bloque.split('\n')
            .map(l => l.trim())
            .filter(l => l.length > 0);
        
        // Verificar que sea una pregunta válida (debe tener al menos una línea que empiece con $$$)
        const lineasRespuesta = lineas.filter(l => l.startsWith('$$$'));
        if (lineasRespuesta.length === 0) {
            continue; // No es una pregunta válida, continuar con el siguiente bloque
        }
        
        // Obtener la respuesta correcta sin el prefijo $$$
        const respuestaCorrecta = lineasRespuesta[0].substring(3).trim().toLowerCase();
        
        // Contar opciones totales (incluyendo la correcta)
        // Restar 1 por el enunciado que siempre es la primera línea
        const numOpciones = lineas.length - 1;
        
        // Primera línea es el enunciado
        const enunciado = lineas[0];
        
        // Clasificar por características
        if (numOpciones >= 3) {
            // Opción múltiple: tiene 3 o más opciones
            tiposPreguntasEncontrados["opción múltiple"]++;
        } else if (numOpciones === 2 && 
                 (respuestaCorrecta === "verdadero" || respuestaCorrecta === "falso")) {
            // Verdadero/Falso: tiene exactamente 2 opciones y una es "verdadero" o "falso"
            tiposPreguntasEncontrados["verdadero/falso"]++;
        } else if (numOpciones === 1 && (enunciado.includes("_____") || 
                  (enunciado.toLowerCase().includes("complete") && enunciado.toLowerCase().includes("frase")))) {
            // Rellenar espacios: tiene una opción y el enunciado incluye guiones bajos o "complete la frase"
            tiposPreguntasEncontrados["rellenar espacios"]++;
        } else if (numOpciones === 1) {
            // Respuesta corta: tiene solo una opción
            tiposPreguntasEncontrados["respuesta corta"]++;
        }
    }

    console.log("Tipos de preguntas detectados:", tiposPreguntasEncontrados);
    return tiposPreguntasEncontrados;
}

// Función para contar preguntas en el archivo de forma más precisa
function contarPreguntasEnArchivo(contenido) {
    // Dividir por líneas en blanco y filtrar líneas vacías al inicio/fin
    const bloquesDeTexto = contenido.split(/\n\s*\n/)
        .filter(bloque => bloque.trim().length > 0);
    
    // Contar bloques que parecen preguntas (tienen al menos una línea que empieza con $$$)
    let contadorPreguntas = 0;
    
    for (const bloque of bloquesDeTexto) {
        const lineas = bloque.split('\n');
        // Una pregunta válida debe tener al menos una línea que empiece con $$$
        if (lineas.some(linea => linea.trim().startsWith('$$$'))) {
            contadorPreguntas++;
        }
    }
    
    return contadorPreguntas;
}

// Funciones para convertir valores de los select a texto descriptivo
function getDificultadTexto(dificultad) {
    const dificultades = {
        'facil': 'fácil (conceptos básicos y preguntas directas)',
        'medio': 'media (aplicación de conceptos y comprensión moderada)',
        'dificil': 'difícil (análisis profundo y conexión de conceptos)',
        'muy_dificil': 'muy difícil (pensamiento crítico avanzado y aplicación compleja)'
    };
    return dificultades[dificultad] || dificultad;
}

function getExamConfig() {
    // Obtener valores de los inputs
    const multirespuesta = parseInt(multirespuestaInput.value) || 0;
    const verdaderoFalso = parseInt(verdaderoFalsoInput.value) || 0;
    const respuestaCorta = parseInt(respuestaCortaInput.value) || 0;
    const rellenarEspacios = parseInt(rellenarEspaciosInput.value) || 0;

    console.log("Configuración del examen:");
    console.log(`- Multirespuesta: ${multirespuesta}`);
    console.log(`- Verdadero/Falso: ${verdaderoFalso}`);
    console.log(`- Respuesta Corta: ${respuestaCorta}`);
    console.log(`- Rellenar Espacios: ${rellenarEspacios}`);

    // Comprobar si las penalizaciones están activadas
    const penalizacionMulti = document.querySelector('input[name="penalizacion_multi"]:checked')?.value === 'si';
    const penalizacionVF = document.querySelector('input[name="penalizacion_vf"]:checked')?.value === 'si';

    // Obtener valores de penalización (como porcentaje)
    const valorPenalizacionMulti = penalizacionMulti ?
        (parseFloat(document.getElementById('valor_penalizacion_multi').value) || 25) / 100 : 0;
    const valorPenalizacionVF = penalizacionVF ?
        (parseFloat(document.getElementById('valor_penalizacion_vf').value) || 50) / 100 : 0;

    // Resto de configuraciones
    let config = {
        questionTypes: {
            multirespuesta: multirespuesta,
            verdaderoFalso: verdaderoFalso,
            respuestaCorta: respuestaCorta,
            rellenarEspacios: rellenarEspacios
        },
        config: {
            multirespuesta: {
                opciones: parseInt(document.getElementById('opciones_multirespuesta').value) || 4,
                penalizacion: penalizacionMulti,
                valorPenalizacion: valorPenalizacionMulti,
                puntos: parseFloat(document.getElementById('puntos_multi').value) || 1.0
            },
            verdaderoFalso: {
                penalizacion: penalizacionVF,
                valorPenalizacion: valorPenalizacionVF,
                puntos: parseFloat(document.getElementById('puntos_vf').value) || 1.0
            },
            respuestaCorta: {
                puntos: parseFloat(document.getElementById('puntos_corta').value) || 1.0,
                caseSensitive: document.querySelector('input[name="case_sensitive"]:checked')?.value === 'si'
            },
            rellenarEspacios: {
                puntos: parseFloat(document.getElementById('puntos_rellenar').value) || 1.0
            }
        }
    };

    return config;
}

function togglePenalizacionConfig(tipo) {
    const radioPenalizacion = document.querySelector(`input[name="penalizacion_${tipo}"]:checked`);
    const configDiv = document.getElementById(`penalizacion_${tipo}_config`);

    if (radioPenalizacion && configDiv) {
        if (radioPenalizacion.value === 'si') {
            configDiv.style.display = 'block';
        } else {
            configDiv.style.display = 'none';
        }
    }
}

// Función ejecutada al subir el archivo
function processForm(e) {
    e.preventDefault();
    statusEl.hidden = false;

    // Obtener la configuración del examen
    const examConfig = getExamConfig();

    // Obtener los valores del formulario
    const formData = new FormData(e.target);
    let scriptName = formData.get('script');
    const entrada = document.getElementById('entrada');
    const outputFilename = OUTPUT_FILENAMES[scriptName];

    // Usamos los scripts mejorados independientemente del tipo de pregunta
    console.log(`Usando script: ${scriptName}`);

    // Leer el examen subido
    var inputFile = entrada.files[0];
    var reader = new FileReader();
    reader.readAsText(inputFile);
    reader.onload = async (evt) => {

        try {
            
            // Preparar el contenido según la configuración
            var inputContent = evt.target.result;
            var processedContent = prepareExamContent(inputContent, examConfig);

            // Escribir el examen de entrada en el sistema de archivos virtual de Pyodide
            
    // Validaciones antes de ejecutar generación de examen
    if (!pyodide) {
        alert("Error: Pyodide no está completamente cargado. Espere unos segundos y vuelva a intentarlo.");
        return;
    }

    if (!processedContent || processedContent.trim().length === 0) {
        alert("Error: El archivo subido está vacío. Por favor, sube un archivo con contenido válido.");
        return;
    }

    const totalPreguntas = preguntasCargadas.length;
    const preguntasSolicitadas = Object.values(examConfig.questionTypes).reduce((acc, val) => acc + val, 0);


    if (preguntasSolicitadas > totalPreguntas) {
        alert(`Error: Has solicitado ${preguntasSolicitadas} preguntas, pero solo hay ${totalPreguntas} disponibles.`);
        return;
    }

    
    // Validación adicional: comprobar si hay suficientes opciones por pregunta múltiple
 

    const bloques = processedContent.split(/\n\s*\n/).filter(b => b.trim().length > 0);
    const erroresOpciones = [];

    const numOpcionesMulti = examConfig.config.multirespuesta.opciones || 4;

bloques.forEach((bloque, idx) => {
    const lineas = bloque.trim().split('\n').map(l => l.trim()).filter(l => l.length > 0);
    if (lineas.length < 2) return;

    const enunciado = lineas[0].toLowerCase();
    const respuestas = lineas.slice(1);
    const respuestaCorrecta = respuestas.find(r => r.startsWith('$$$'));
    const numOpciones = respuestas.length;

    // Detectar si es de opción múltiple:
    const pareceVF = respuestas.length === 2 &&
        respuestas.some(r => r.toLowerCase().includes("verdadero")) &&
        respuestas.some(r => r.toLowerCase().includes("falso"));

    const pareceRellenar = enunciado.includes("_____") || enunciado.includes("complete la frase");
    const pareceCorta = respuestas.length === 1 && !pareceRellenar;

    const esOpcionMultiple = respuestaCorrecta && !pareceVF && !pareceCorta && !pareceRellenar;

    if (esOpcionMultiple && numOpciones < numOpcionesMulti) {
        erroresOpciones.push(`Pregunta ${idx + 1} tiene solo ${numOpciones} opciones (mínimo requerido: ${numOpcionesMulti})`);
    }
});



    if (erroresOpciones.length > 0) {
        alert("Error: Se encontraron preguntas de opción múltiple con menos opciones de las requeridas:\n\n" + erroresOpciones.join('\n'));
        return;
    }

    pyodide.FS.writeFile("examen.txt", processedContent, { encoding: "utf8" });
            // Guardar imágenes en el FS de Pyodide
for (const [nombre, archivo] of Object.entries(imagenesSubidas)) {
    const arrayBuffer = await archivo.arrayBuffer();
    const bytes = new Uint8Array(arrayBuffer);
    pyodide.FS.writeFile(nombre, bytes);
  }
  

            // Ejecutar el script
            pyodide.globals.clear();
            pyodide.globals.set("ASIGNACION_IMAGENES", asignacionImagenes);

            pyodide.runPython(PYTHON_GOOGLE_MOCK);

            // Modificar el script según la configuración antes de ejecutarlo
            let modifiedScript = injectExamConfig(SCRIPTS[scriptName], examConfig);

            try {
                var debug = pyodide.runPython(modifiedScript);
                console.log("Resultado de ejecución:", debug);

                // Leer el examen de salida del sistema de archivos virtual de Pyodide
                let outputContent = pyodide.FS.readFile(outputFilename, { encoding: "utf8" });

                // Disparar la descarga del archivo en el navegador creando un elemento temporal
                var blob = new Blob([outputContent], { type: "text/plain;charset=utf8" });
                var elem = window.document.createElement('a');
                elem.href = window.URL.createObjectURL(blob);
                elem.download = outputFilename;
                document.body.appendChild(elem);
                elem.click();
                document.body.removeChild(elem);
            } catch (pythonError) {
                console.error("Error al ejecutar el script Python:", pythonError);

                // Intentar identificar el tipo de error
                if (pythonError.message.includes("SyntaxError") ||
                    pythonError.message.includes("IndentationError")) {
                    alert("Error de sintaxis en el script Python. Por favor, contacta al administrador.");
                    console.log("Script con error de sintaxis:", modifiedScript);
                } else {
                    alert("Error al procesar el examen: " + pythonError.message);
                }
            }
        }
        catch (err) {
            alert("Error al producir el examen: " + err.message);
            console.error("Error completo:", err);
        } finally {
            try {
                pyodide.FS.unlink("examen.txt");
            } catch (e) {
                console.warn("No se pudo eliminar el archivo temporal:", e);
            }
            statusEl.hidden = true;
        }
    };
    return false;
}

// Función para inyectar la configuración del examen en el script Python de manera segura
function injectExamConfig(script, config) {
    // Convertir JavaScript a formato de diccionario Python de forma manual y cuidadosa
    function jsToDict(obj, indent = 0) {
        const spaces = ' '.repeat(indent);
        const spacesInner = ' '.repeat(indent + 4);

        if (obj === null) return 'None';
        if (obj === true) return 'True';
        if (obj === false) return 'False';
        if (typeof obj === 'number') return obj.toString();
        if (typeof obj === 'string') return `"${obj}"`;

        if (Array.isArray(obj)) {
            const items = obj.map(item => jsToDict(item, indent + 4)).join(', ');
            return `[${items}]`;
        }

        // Si es un objeto, convertirlo a diccionario Python con indentación apropiada
        if (typeof obj === 'object') {
            const entries = Object.entries(obj).map(([k, v]) => {
                return `${spacesInner}"${k}": ${jsToDict(v, indent + 4)}`;
            }).join(',\n');

            return `{\n${entries}\n${spaces}}`;
        }

        return String(obj);
    }

    // Crear la configuración Python como string con formato adecuado
    const configString = jsToDict(config);
    const pythonConfig = `CONFIG_EXAMEN = ${configString}`;

    // Buscar el patrón de declaración de CONFIG_EXAMEN y reemplazarlo completamente
    const declarationPattern = /CONFIG_EXAMEN\s*=\s*\{[\s\S]*?\n\}/g;

    if (declarationPattern.test(script)) {
        // Usar una expresión regular para capturar toda la declaración hasta el último }
        return script.replace(declarationPattern, pythonConfig);
    } else {
        console.warn("No se encontró la declaración CONFIG_EXAMEN en el formato esperado.");

        // Como alternativa, buscar solo la línea de declaración y reemplazar todo hasta un punto conocido
        const declarationLine = script.indexOf('CONFIG_EXAMEN = {');
        if (declarationLine >= 0) {
            // Encontrar un punto seguro en el script después de la configuración
            const segmentosImport = [
                'from google.colab import files',
                'import random',
                'import re',
                'import math',
                'import json'
            ];

            // Buscar la primera ocurrencia de cualquiera de estos segmentos después de la declaración
            let cutPoint = -1;
            for (const segmento of segmentosImport) {
                const pos = script.indexOf(segmento, declarationLine);
                if (pos > 0 && (cutPoint === -1 || pos < cutPoint)) {
                    cutPoint = pos;
                }
            }

            if (cutPoint > 0) {
                // Reemplazar solo la parte de la configuración
                return script.substring(0, declarationLine) + pythonConfig + '\n\n' + script.substring(cutPoint);
            }
        }

        // Si todo falla, volver a insertar al inicio del script después de los comentarios
        const scriptLines = script.split('\n');
        let insertPoint = 0;

        // Encontrar la última línea de comentarios o importaciones
        for (let i = 0; i < scriptLines.length; i++) {
            if (scriptLines[i].trim().startsWith('#') ||
                scriptLines[i].trim().startsWith('import') ||
                scriptLines[i].trim().startsWith('from')) {
                insertPoint = i + 1;
            } else if (scriptLines[i].trim() === '') {
                continue;
            } else {
                break;
            }
        }

        // Insertar después de los comentarios e importaciones
        scriptLines.splice(insertPoint, 0, pythonConfig + '\n');
        return scriptLines.join('\n');
    }
}