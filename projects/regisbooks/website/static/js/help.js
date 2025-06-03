const focusText = location.hash.substring(1);

if (focusText !== "view-listings") {
	document.getElementById(focusText).querySelector("button").click();
}