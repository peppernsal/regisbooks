const focusText = location.hash.substring(1);

if (focusText !== "view-listings") {
	document.getElementById(focusText).querySelector("button").click();
}

const accordionButtons = document.querySelectorAll(".accordion-button");
accordionButtons.forEach(button => {
	button.addEventListener("click", () => {
		location.hash = button.parentElement.id;
	});
});