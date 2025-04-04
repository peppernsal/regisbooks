const listingID = new URLSearchParams(location.search).get("id");

(async() => {
	try {
		const listing = await getListingInfo(listingID);
		const book = await getBookInfo(listing.bookID);
		const author = await getUserInfo(listing.authorID);

		document.getElementById("book-title").textContent = book.title;
		document.getElementById("book-author").textContent = book.author;
		document.getElementById("book-isbn").textContent = `ISBN: ${book.isbn}`;
		document.getElementById("book-publishing-info").textContent = `${book.publisher}, ${book.publishDate}`;

		document.getElementById("listing-author").textContent = `Listed by: ${author.firstName} ${author.lastName}`;
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

		if (listing.status == 1) {
			const reqBtn = document.getElementById("request-listing");
			reqBtn.classList.add("disabled");
			reqBtn.innerHTML = "<em>This Listing Has Already Been Requested By Someone</em>";
		} else if (listing.status == 2) {
			const reqBtn = document.getElementById("request-listing");
			reqBtn.classList.add("disabled");
			reqBtn.innerHTML = "<em>This Listing Is No Longer Available</em>";
		} else {
			const reqBtn = document.getElementById("request-listing");
			
			reqBtn.href = `/request-listing?id=${listingID}`;
		}

	} catch (error) {
		console.error(error);
		alert("Invalid listing!");
		location.href = "/view-listings";
	}
})();