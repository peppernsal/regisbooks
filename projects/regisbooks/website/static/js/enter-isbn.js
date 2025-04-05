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