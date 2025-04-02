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

const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const step1Nav = document.getElementById('step1-nav');
const step2Nav = document.getElementById('step2-nav');
const step3Nav = document.getElementById('step3-nav');

const btnToStep2 = document.getElementById('btn-to-step2');
const btnToStep1 = document.getElementById('btn-to-step1');
const btnToStep3 = document.getElementById('btn-to-step3');
const btnToStep2FromStep3 = document.getElementById('btn-to-step2-from-3');

const multirespuestaInput = document.getElementById('multirespuesta');
const verdaderoFalsoInput = document.getElementById('verdadero_falso');

const multirespuestaConfig = document.getElementById('multirespuesta-config');
const verdaderoFalsoConfig = document.getElementById('verdadero_falso-config');
const loadingTimeout = setTimeout(function () {
    const statusEl = document.getElementById('status');
    const errorMessageEl = document.getElementById('error-message');

    if (statusEl && !statusEl.hidden) {
        if (errorMessageEl) errorMessageEl.classList.remove('hidden');
        console.error("Timeout durante la carga de scripts o Pyodide");
    }
}, 10000);


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
        throw err;
    }),
]).then(([papel, moodle, papelEnhanced, moodleEnhanced, _pyodide]) => {
    clearTimeout(loadingTimeout);

    if (!papel || !moodle) {
        throw new Error("No se pudieron cargar los scripts principales");
    }

    SCRIPTS['papel.py'] = papel;
    SCRIPTS['moodle.py'] = moodle;

    if (papelEnhanced) SCRIPTS['papel.py'] = papelEnhanced;
    if (moodleEnhanced) SCRIPTS['moodle.py'] = moodleEnhanced;

    step1.classList.remove('hidden');
    statusEl.hidden = true;

    pyodide = _pyodide;
    console.log("Pyodide ready");

}).catch(error => {
    clearTimeout(loadingTimeout);

    const statusEl = document.getElementById('status');
    const errorMessageEl = document.getElementById('error-message');

    if (statusEl) statusEl.innerHTML = "Error al cargar. Por favor, recargue la página.";
    if (errorMessageEl) errorMessageEl.classList.remove('hidden');

    console.error("Error durante la inicialización:", error);
});

function updateConfigVisibility() {
    multirespuestaConfig.classList.toggle('hidden', parseInt(multirespuestaInput.value) <= 0);
    verdaderoFalsoConfig.classList.toggle('hidden', parseInt(verdaderoFalsoInput.value) <= 0);
}

[multirespuestaInput, verdaderoFalsoInput].forEach(input => {
    input.addEventListener('change', updateConfigVisibility);
});

btnToStep2.addEventListener('click', () => {
    const totalQuestions = parseInt(multirespuestaInput.value) +
        parseInt(verdaderoFalsoInput.value);

    if (totalQuestions <= 0) {
        alert('Debe seleccionar al menos un tipo de pregunta');
        return;
    }

    updateConfigVisibility();

    step1.classList.add('hidden');
    step2.classList.remove('hidden');
    step1Nav.classList.remove('active');
    step2Nav.classList.add('active');
});

btnToStep1.addEventListener('click', () => {
    step2.classList.add('hidden');
    step1.classList.remove('hidden');
    step2Nav.classList.remove('active');
    step1Nav.classList.add('active');
});

btnToStep3.addEventListener('click', () => {
    step2.classList.add('hidden');
    step3.classList.remove('hidden');
    step2Nav.classList.remove('active');
    step3Nav.classList.add('active');
});

btnToStep2FromStep3.addEventListener('click', (e) => {
    e.preventDefault();

    step3.classList.add('hidden');
    step2.classList.remove('hidden');
    step3Nav.classList.remove('active');
    step2Nav.classList.add('active');
});

function getExamConfig() {
    const multirespuesta = parseInt(multirespuestaInput.value) || 0;
    const verdaderoFalso = parseInt(verdaderoFalsoInput.value) || 0;

    console.log("Configuración del examen:");
    console.log(`- Multirespuesta: ${multirespuesta}`);
    console.log(`- Verdadero/Falso: ${verdaderoFalso}`);

    const penalizacionMulti = document.querySelector('input[name="penalizacion_multi"]:checked')?.value === 'si';
    const penalizacionVF = document.querySelector('input[name="penalizacion_vf"]:checked')?.value === 'si';

    const valorPenalizacionMulti = penalizacionMulti ?
        (parseFloat(document.getElementById('valor_penalizacion_multi').value) || 25) / 100 : 0;
    const valorPenalizacionVF = penalizacionVF ?
        (parseFloat(document.getElementById('valor_penalizacion_vf').value) || 50) / 100 : 0;

    let config = {
        questionTypes: {
            multirespuesta: multirespuesta,
            verdaderoFalso: verdaderoFalso
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
            }
        }
    };

    return config;
}

function togglePenalizacionConfig(tipo) {
    const radioPenalizacion = document.querySelector(`input[name="penalizacion_${tipo}"]:checked`);
    const configDiv = document.getElementById(`penalizacion_${tipo}_config`);

    if (radioPenalizacion.value === 'si') {
        configDiv.style.display = 'block';
    } else {
        configDiv.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    togglePenalizacionConfig('multi');
    togglePenalizacionConfig('vf');

    document.querySelectorAll('input[name="penalizacion_multi"], input[name="penalizacion_vf"]').forEach(radio => {
        radio.addEventListener('change', function () {
            togglePenalizacionConfig(this.name.split('_')[1]);
        });
    });
});

function prepareExamContent(inputContent, config) {
    if (!inputContent.includes('$$$')) {
        alert('Advertencia: No se encontraron respuestas marcadas con "$$$". ' +
            'Asegúrese de que su archivo sigue el formato correcto.');
    }

    // Modificación para mejorar la detección de preguntas
    // Primero normalizar los saltos de línea
    let normalizedContent = inputContent.replace(/\r\n/g, '\n');
    
    // Contar preguntas basándose en varios patrones de separación
    const numPreguntasBasico = (normalizedContent.match(/\n\n/g) || []).length + 1;
    const numPreguntasMultiple = (normalizedContent.match(/\$\$\$/g) || []).length;
    
    // Usar el mayor valor como estimación de preguntas
    const numPreguntas = Math.max(numPreguntasBasico, numPreguntasMultiple);
    
    const totalPreguntasRequeridas =
        config.questionTypes.multirespuesta +
        config.questionTypes.verdaderoFalso;

    if (numPreguntas < totalPreguntasRequeridas) {
        alert(`Advertencia: El archivo parece contener solo ${numPreguntas} preguntas, ` +
            `pero se han solicitado ${totalPreguntasRequeridas}. ` +
            `Se utilizarán todas las preguntas disponibles.`);
    }

    return normalizedContent;
}

function processForm(e) {
    e.preventDefault();
    statusEl.hidden = false;

    const examConfig = getExamConfig();

    const formData = new FormData(e.target);
    let scriptName = formData.get('script');
    const entrada = document.getElementById('entrada');
    const outputFilename = OUTPUT_FILENAMES[scriptName];

    console.log(`Usando script: ${scriptName}`);

    var inputFile = entrada.files[0];
    var reader = new FileReader();
    reader.readAsText(inputFile);
    reader.onload = evt => {
        try {
            var inputContent = evt.target.result;
            var processedContent = prepareExamContent(inputContent, examConfig);

            pyodide.FS.writeFile("examen.txt", processedContent, { encoding: "utf8" });

            pyodide.globals.clear();
            pyodide.runPython(PYTHON_GOOGLE_MOCK);

            let modifiedScript = injectExamConfig(SCRIPTS[scriptName], examConfig);

            try {
                var debug = pyodide.runPython(modifiedScript);
                console.log("Resultado de ejecución:", debug);

                let outputContent = pyodide.FS.readFile(outputFilename, { encoding: "utf8" });

                var blob = new Blob([outputContent], { type: "text/plain;charset=utf8" });
                var elem = window.document.createElement('a');
                elem.href = window.URL.createObjectURL(blob);
                elem.download = outputFilename;
                document.body.appendChild(elem);
                elem.click();
                document.body.removeChild(elem);
            } catch (pythonError) {
                console.error("Error al ejecutar el script Python:", pythonError);

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


function injectExamConfig(script, config) {
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

        if (typeof obj === 'object') {
            const entries = Object.entries(obj).map(([k, v]) => {
                return `${spacesInner}"${k}": ${jsToDict(v, indent + 4)}`;
            }).join(',\n');

            return `{\n${entries}\n${spaces}}`;
        }

        return String(obj);
    }

    const configString = jsToDict(config);
    const pythonConfig = `CONFIG_EXAMEN = ${configString}`;

    const declarationPattern = /CONFIG_EXAMEN\s*=\s*\{[\s\S]*?\n\}/g;

    if (declarationPattern.test(script)) {
        return script.replace(declarationPattern, pythonConfig);
    } else {
        console.warn("No se encontró la declaración CONFIG_EXAMEN en el formato esperado.");

        const declarationLine = script.indexOf('CONFIG_EXAMEN = {');
        if (declarationLine >= 0) {
            const segmentosImport = [
                'from google.colab import files',
                'import random',
                'import re',
                'import math',
                'import json'
            ];

            let cutPoint = -1;
            for (const segmento of segmentosImport) {
                const pos = script.indexOf(segmento, declarationLine);
                if (pos > 0 && (cutPoint === -1 || pos < cutPoint)) {
                    cutPoint = pos;
                }
            }

            if (cutPoint > 0) {
                return script.substring(0, declarationLine) + pythonConfig + '\n\n' + script.substring(cutPoint);
            }
        }

        const scriptLines = script.split('\n');
        let insertPoint = 0;

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

        scriptLines.splice(insertPoint, 0, pythonConfig + '\n');
        return scriptLines.join('\n');
    }

}

var form = document.getElementById('exam-form');
form.addEventListener("submit", processForm);