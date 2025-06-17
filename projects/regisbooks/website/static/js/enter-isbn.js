const isbnEntry = document.getElementById("isbn-entry");

function propagateISBN() {
	const isbn = isbnEntry.value.replace(/\D/g,''); // Remove all non-digit characters

	window.location.href = `/add-listing?book=${isbn}`;
}

isbnEntry.addEventListener("keypress", function(event) {
	if (event.key === "Enter") {
		event.preventDefault();
		propagateISBN();
	}
});

const html5QrCodeScanner = new Html5QrcodeScanner("barcode-reader", { fps: 10, qrbox: 250 });
html5QrCodeScanner.render(onScanSuccess);

function onScanSuccess(decodedText, decodedResult) {
	if (decodedText) {
		const isbn = decodedText.replace(/\D/g,'');
		if (isbn.length == 10 || isbn.length == 13) {
			window.location.href = `/add-listing?book=${isbn}`;
		} else {
			alert("Scanned code is not a valid ISBN.");
		}
	}
}

setInterval(() => {
	const barcodeButtons = document.getElementById("barcode-reader").querySelectorAll("button");

	barcodeButtons.forEach(button => {
		if (button.classList.contains("btn")) return;
		
		button.classList.add("btn", "body-btn-primary", "btn-primary");
	});
}, 1000);