const listingID = new URLSearchParams(window.location.search).get('id');

if (!listingID) {
	alert("No listing ID provided!");
	location.href = "/";
}

(async () => {
	try {
		const response = await reqListing(listingID);
		
		if (response.status !== 200) {
			throw new Error();
		}

		const listing = await getListingInfo(listingID);
		const book = await getBookInfo(listing.bookID);
		const poster = await getUserInfo(listing.authorID);

		document.getElementById("book-title").textContent = book.title;
		document.getElementById("book-author").textContent = book.author;
		document.getElementById("book-isbn").textContent = `ISBN: ${book.isbn}`;
		document.getElementById("book-publishing-info").textContent = `${book.publisher}, ${book.publishDate}`;

		document.getElementById("listing-author").textContent = `Listed by: ${poster.firstName} ${poster.lastName}`;
		document.getElementById("listing-usage-level").textContent = `Condition: ${listingUsageRepr[listing.usageLevel]}`;
		document.getElementById("listing-status").textContent = `Status: ${listingStatusRepr[listing.status]}`;
		document.getElementById("listing-notes").textContent = listing.notes || "No notes provided by poster.";

		const pickupContainer = document.getElementById("pickup-locations-container");
		pickupContainer.innerHTML = "";

		listing.pickupLocations.forEach(location => {
			const locElem = document.createElement("h5");
			locElem.textContent = `Pickup At: ${location}`;
			pickupContainer.appendChild(locElem);
		});

		const coverImg = document.getElementById("book-cover-img");
		const coverCaption = document.getElementById("cover-disclaimer");

		if (book.coverImageURL === "<no-url>") {
			coverImg.remove();
			coverCaption.remove();
		} else {
			coverImg.src = book.coverImageURL;
			coverCaption.textContent = "Note: cover image and publisher may not match physical book. Check ISBN to match versions.";
		}


		const emailBtn = document.getElementById("email-info-btn");
		const emailLink = document.getElementById("email-info");

		emailLink.textContent = poster.email;
		emailLink.href = `mailto:${poster.email}?subject=RegisBooks: Request for ${book.title}`;

		emailBtn.addEventListener("click", () => {
			emailLink.classList.toggle("d-none");
			emailBtn.textContent = emailLink.classList.contains("d-none") ? "Show Lister Email" : "Hide Lister Email";
		});
	} catch {
		alert("Could not request the listing!");
		location.href = `/view-listing?listingID=${listingID}`;
	}

})();