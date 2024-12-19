function propagateISBN() {
	const isbn = document.getElementById("isbn-entry").value;

	window.location.href = `/add-listing?book=${isbn}`;
}