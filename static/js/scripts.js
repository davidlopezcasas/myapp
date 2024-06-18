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
            const newEtiqueta = document.createElement('div');
            const lineaId = e.target.nextElementSibling.dataset.lineaId;
            newEtiqueta.classList.add('etiqueta');
            newEtiqueta.innerHTML = `
                <label for="kilos">Kilos:</label>
                <input type="text" name="etiqueta_kilos_${lineaId}[]"><br>
                <label for="qretiqueta">QR Etiqueta:</label>
                <input type="text" name="qretiqueta_${lineaId}[]" class="qretiqueta-input"><br>
                <button type="button" class="scan-qr">Escanear QR</button>
                <button type="button" class="remove-etiqueta">Eliminar Etiqueta</button>
                <hr>
                <label for="qretiquetacompra">QR Compra:</label>
                <input type="text" name="qretiquetacompra_${lineaId}[]" class="qretiquetacompra-input"><br>
                <button type="button" class="scan-qr-compra">Escanear QR Compra</button>
                <hr>
            `;
            e.target.nextElementSibling.appendChild(newEtiqueta);
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
