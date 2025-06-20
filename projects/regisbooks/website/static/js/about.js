document.addEventListener("DOMContentLoaded", async () => {
	const impactPara = document.getElementById("impact-paragraph");

	const impact = await getImpact();

	let bookStr = "books"

	if (impact.givenAway == 1) {
		bookStr = "book";
	}

	let requestedInfo = "";

	if (impact.requested > 0) {
		let gawStr = "giveaways";
		let verb = "have"

		if (impact.requested == 1) {
			gawStr = "giveaway";
			verb = "has";
		}

		requestedInfo = `<a href="/view-listings?status=1" class="text-decoration-none text-success">${impact.requested} more ${gawStr}</a> ${verb} already begun.`;
	}

	let availableInfo = "";

	if (impact.available > 0) {
		let distStr = "distributions";
		let verb = "are";

		if (impact.available == 1) {
			distStr = "distribution";
			verb = "is";
		}

		availableInfo = `<a href="/view-listings?status=0" class="text-decoration-none text-primary">${impact.available} ${distStr}</a> ${verb} waiting to happen.`;
	}

	impactPara.innerHTML = `
		<div>Since its release, RegisBooks has facilitated the re-use of <span class="text-danger">${impact.givenAway} ${bookStr}</span>.</div>
		<div>${requestedInfo}</div>
		<div>${availableInfo}</div>
	`;
});