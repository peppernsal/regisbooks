document.addEventListener("DOMContentLoaded", async () => {
	const userInfo = await getUserInfo((await getUser()).userId);

	const outgoingContainer = document.getElementById("outgoing-requests");
	const incomingContainer = document.getElementById("incoming-requests");

	outgoingContainer.innerHTML = "";
	incomingContainer.innerHTML = "";

	const outgoingRequests = (await getListingsPaginateFully({ status: STATUS_REQUESTED })).filter((listing) => listing.requesterID == userInfo.id);

	if (outgoingRequests.length > 0) {

		for (const listing of outgoingRequests) {
			const bookInfo = await getBookInfo(listing.bookID);

			const card = document.createElement("a");
			card.className = "card mb-3 text-decoration-none";
			card.href = `/view-listing?id=${listing.id}`;

			const cardBody = document.createElement("div");
			cardBody.className = "card-body row";

			const coverImg = document.createElement("img");
			coverImg.className = "detail-cover-img col-md-3";
			coverImg.src = bookInfo.coverImageURL;

			const textContainer = document.createElement("div");
			textContainer.className = "col-md-9"

			const title = document.createElement("h5");
			title.className = "card-title";
			title.textContent = bookInfo.title;

			const listerInfo = await getUserInfo(listing.authorID);

			const listerName = document.createElement("h6");
			listerName.className = "card-subtitle text-muted";
			listerName.textContent = `Listed by: ${listerInfo.firstName} ${listerInfo.lastName}`;

			textContainer.appendChild(title);
			textContainer.appendChild(listerName);

			cardBody.appendChild(coverImg);
			cardBody.appendChild(textContainer);
			card.appendChild(cardBody);
			outgoingContainer.appendChild(card);
		}
	} else {
		const alert = document.createElement('div');
		alert.className = 'col-12';
		const alertInner = textElem('div', "You haven't requested any listings yet!");
		alertInner.className = 'alert alert-secondary';
		alert.appendChild(alertInner);
		outgoingContainer.appendChild(alert);
	}

	const incomingRequests = (await getListingsPaginateFully({ posterID: userInfo.id, status: STATUS_REQUESTED }));

	if (incomingRequests.length > 0) {
		for (const listing of incomingRequests) {
			const bookInfo = await getBookInfo(listing.bookID);

			const card = document.createElement("a");
			card.className = "card mb-3 text-decoration-none";
			card.href = `/view-listing?id=${listing.id}`;

			const cardBody = document.createElement("div");
			cardBody.className = "card-body row";

			const coverImg = document.createElement("img");
			coverImg.className = "detail-cover-img col-md-3";
			coverImg.src = bookInfo.coverImageURL;

			const textContainer = document.createElement("div");
			textContainer.className = "col-md-9"

			const title = document.createElement("h5");
			title.className = "card-title";
			title.textContent = bookInfo.title;

			const requesterInfo = await getUserInfo(listing.requesterID);

			const listerName = document.createElement("h6");
			listerName.className = "card-subtitle text-muted";
			listerName.textContent = `Requested by: ${requesterInfo.firstName} ${requesterInfo.lastName}`;

			textContainer.appendChild(title);
			textContainer.appendChild(listerName);

			cardBody.appendChild(coverImg);
			cardBody.appendChild(textContainer);
			card.appendChild(cardBody);
			incomingContainer.appendChild(card);
		}
	} else {
		const alert = document.createElement('div');
		alert.className = 'col-12';
		const alertInner = textElem('div', "No one has requested your listings yet!");
		alertInner.className = 'alert alert-secondary';
		alert.appendChild(alertInner);
		incomingContainer.appendChild(alert);
	}
});