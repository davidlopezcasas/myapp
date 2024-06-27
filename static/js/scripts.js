document.addEventListener('DOMContentLoaded', function () {
    const addLineaButton = document.getElementById('add-linea');
    const lineasProductoContainer = document.getElementById('lineas-producto-container');
    let currentEtiquetaInput = null;

    addLineaButton.addEventListener('click', function () {
        const newLinea = document.querySelector('.linea-producto').cloneNode(true);
        const newId = document.querySelectorAll('.linea-producto').length;
        newLinea.querySelector('.etiquetas-container').dataset.lineaId = newId;
        newLinea.querySelector('.etiquetas-container').innerHTML = '';
        newLinea.querySelectorAll('input').forEach(input => input.value = '');
        newLinea.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
        lineasProductoContainer.appendChild(newLinea);
    });

    lineasProductoContainer.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-linea')) {
            e.target.closest('.linea-producto').remove();
        }
        if (e.target.classList.contains('add-etiqueta')) {
            const lineaId = e.target.nextElementSibling.dataset.lineaId;
            const numeroCajasInput = e.target.closest('.linea-producto').querySelector('input[name="numerocajas[]"]');
            const numeroCajas = parseInt(numeroCajasInput.value) || 0;
            const etiquetasContainer = e.target.nextElementSibling;
            etiquetasContainer.innerHTML = '';

            for (let i = 0; i <= numeroCajas; i++) {
                const newEtiqueta = document.createElement('div');
                newEtiqueta.classList.add('etiqueta');

                if (i != numeroCajas) {
                    newEtiqueta.innerHTML = `
                        <label for="kilos">Kilos:</label>
                        <input type="number" name="kilo_${i}" step="0.01"><br>
                    `;
                } else {
                    newEtiqueta.innerHTML = `
                        <label for="qretiqueta">QR Etiqueta:</label>
                        <input type="text" name="qretiqueta_${lineaId}[]" class="qretiqueta-input"><br>
                        <button type="button" class="scan-qr">Escanear QR</button>
                        <hr>
                        <label for="qretiquetacompra">QR Compra:</label>
                        <input type="text" name="qretiquetacompra_${lineaId}[]" class="qretiquetacompra-input"><br>
                        <button type="button" class="scan-qr-compra">Escanear QR Compra</button>
                        <hr>
                        <input type="text" name="etiqueta_kilos_${lineaId}" class="etiqueta-kilos-input" readonly><br>
                        <button type="button" class="concat-kilos" data-linea-id="${lineaId}">Guardar etiqueta</button>
                        <button type="button" class="remove-etiqueta">Eliminar Etiqueta</button>
                    `;
                }
                etiquetasContainer.appendChild(newEtiqueta);
            }
        }
        if (e.target.classList.contains('remove-etiqueta')) {
            e.target.closest('.etiqueta').remove();
        }
        if (e.target.classList.contains('scan-qr')) {
            currentEtiquetaInput = e.target.closest('.etiqueta').querySelector('.qretiqueta-input');
            document.getElementById('qr-scanner-modal').style.display = 'block';
            startQrScanner();
        }
        if (e.target.classList.contains('scan-qr-compra')) {
            currentEtiquetaInput = e.target.closest('.etiqueta').querySelector('.qretiquetacompra-input');
            document.getElementById('qr-scanner-modal').style.display = 'block';
            startQrScanner();
        }
        if (e.target.classList.contains('concat-kilos')) {
            const lineaId = e.target.dataset.lineaId;
            const kilosInputs = e.target.closest('.etiquetas-container').querySelectorAll(`input[name^="kilo_"]`);
            let kilosConcatenados = Array.from(kilosInputs).map(input => input.value).join(' ');
            const etiquetaKilosInput = e.target.closest('.etiquetas-container').querySelector(`input[name="etiqueta_kilos_${lineaId}"]`);
            etiquetaKilosInput.value = kilosConcatenados;
        }
    });

    document.getElementById('close-qr-scanner').addEventListener('click', function () {
        document.getElementById('qr-scanner-modal').style.display = 'none';
        stopQrScanner();
    });

    let qrScanner = null;

    function startQrScanner() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            qrScanner = new Html5Qrcode("qr-reader");
            qrScanner.start(
                { facingMode: "environment" },
                {
                    fps: 10,
                    qrbox: 250
                },
                qrCodeMessage => {
                    currentEtiquetaInput.value = qrCodeMessage;
                    document.getElementById('qr-scanner-modal').style.display = 'none';
                    stopQrScanner();
                },
                errorMessage => {
                    console.error(errorMessage);
                }
            ).catch(err => {
                console.error('Error al iniciar el escáner QR: ', err);
            });
        } else {
            alert('El acceso a la cámara no está soportado en este navegador.');
        }
    }

    function stopQrScanner() {
        if (qrScanner) {
            qrScanner.stop().then(ignore => {
                qrScanner.clear();
            }).catch(err => {
                console.error(err);
            });
        }
    }
});
