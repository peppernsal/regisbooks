document.addEventListener("DOMContentLoaded", async () => {
	const impactPara = document.getElementById("impact-paragraph");

	const impact = await getImpact();

	let bookStr = "books"

	if (impact.givenAway == 1) {
		bookStr = "book";
	}


	impactPara.innerHTML = `
		Since its release, RegisBooks has facilitated the redistribution of <span class="text-danger">${impact.givenAway}</span> ${bookStr},
		with <span class="text-success">${impact.requested}</span> more on the way.
	`;
});