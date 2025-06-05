const listingID = new URLSearchParams(location.search).get("id");

document.addEventListener("DOMContentLoaded", async () => {
	try {
		const listing = await getListingInfo(listingID);
		const book = await getBookInfo(listing.bookID);
		const author = await getUserInfo(listing.authorID);
		const currUserId = (await getUser()).userId;

		document.getElementById("book-title").textContent = book.title;
		document.getElementById("book-author").textContent = book.author;
		document.getElementById("book-isbn").textContent = `ISBN: ${book.isbn}`;
		document.getElementById("book-publishing-info").textContent = `${book.publisher}, ${book.publishDate}`;

		const authorElement = document.getElementById("listing-author");
		
		if (author.id != currUserId) {
			authorElement.innerHTML = 'Listed by: ';
			authorElement.appendChild(createUserLink(author));
		} else {
			authorElement.textContent = 'Listed by you';
		}

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
		if (author.id != currUserId) {
			if (listing.status == 1) {
				const reqBtn = document.getElementById("request-listing");
				reqBtn.classList.add("disabled");

				if (listing.requesterID == currUserId) {
					reqBtn.remove();
					displayRequestInfo(book, listing);
				} else {
					reqBtn.innerHTML = "<em>This Listing Has Already Been Requested By Someone!</em>";
				}
			} else if (listing.status == 2) {
				const reqBtn = document.getElementById("request-listing");
				reqBtn.classList.add("disabled");

				if (listing.requesterID == currUserId) { // display request info
					reqBtn.innerHTML = "<em>You Have Already Claimed This Book!</em>";
				} else {
					reqBtn.innerHTML = "<em>This Listing Is No Longer Available!</em>";
				}
			}
		} else {
			if (listing.status == 0) {
				const reqBtn = document.getElementById("request-listing");
				reqBtn.classList.add("disabled");
				reqBtn.innerHTML = "<em>You Cannot Request Your Own Listing</em>";
			} else if (listing.status == 1) {
				const listingRequester = await getUserInfo(listing.requesterID);
				const reqBtn = document.getElementById("request-listing");

				const replacementDiv = document.createElement("div");
				replacementDiv.classList.add("row", "align-items-center", "text-center")
				
				const reqInfoDiv = document.createElement("div");
				reqInfoDiv.classList.add("col-md-6");

				const reqInfo = document.createElement("h3");
				reqInfo.appendChild(document.createTextNode(`This listing was requested by ${listingRequester.firstName} ${listingRequester.lastName} (`));

				const emailLink = document.createElement("a");
				emailLink.href = `mailto:${listingRequester.email}?subject=RegisBooks: Regarding Your Request for ${book.title}`;
				emailLink.textContent = listingRequester.email;
				reqInfo.appendChild(emailLink);
				reqInfo.appendChild(document.createTextNode(")"));

				reqInfoDiv.appendChild(reqInfo);

				const fulfillDiv = document.createElement("div");
				fulfillDiv.classList.add("col-md-4");

				const fulfillBtn = document.createElement("button");
				fulfillBtn.appendChild(textElem("h4", `I sent ${listingRequester.firstName} the book`));

				fulfillBtn.classList.add("btn", "body-btn-primary", "btn-primary");
				fulfillBtn.onclick = () => {
					if (window.confirm("Are you sure you want to mark this request as fulfilled?\nOnly select this if you have sent the book to the requester. This action cannot be undone.")) {
						fulfillRequestFor(listingID).then((resp) => {
							if (resp.status != 200) {
								alert("Could not fulfill the request!");
								return;
							}
							location.reload();
						});
					}
				}

				fulfillDiv.appendChild(fulfillBtn);
				
				const rejectDiv = document.createElement("div");
				rejectDiv.classList.add("col-md-2");

				const rejectBtn = document.createElement("button");
				rejectBtn.appendChild(textElem("h4", `Reject Request`));
				rejectBtn.classList.add("btn", "btn-danger", "ms-2");
				rejectBtn.onclick = () => {
					if (window.confirm("Are you sure you want to reject this request? This will make the listing available again.")) {
						rejectListingReq(listingID).then((resp) => {
							if (resp.status != 200) {
								alert("Could not reject the request!");
								return;
							}
							location.reload();
						});
					}
				};

				rejectDiv.appendChild(rejectBtn);

				replacementDiv.appendChild(reqInfoDiv);
				replacementDiv.appendChild(fulfillDiv);
				replacementDiv.appendChild(rejectDiv);

				reqBtn.replaceWith(replacementDiv);
			} else { // listing.status == 2
				const listingRequester = await getUserInfo(listing.requesterID);

				const reqBtn = document.getElementById("request-listing");
				reqBtn.replaceWith(
					textElem("h3", `This listing was taken by ${listingRequester.firstName} ${listingRequester.lastName}`)
				);
			}
		}

	} catch (error) {
		console.error(error);
		alert("Invalid listing!");
		location.href = "/view-listings";
	}
});

function requestThisListing() {
	reqListing(listingID).then((resp) => {
		if (resp.status != 200) {
			alert("Uh Oh! Something went wrong while trying to request this listing. Please try again later.");
			return;
		}
		location.reload();
	});
}

async function displayRequestInfo(book, listing) {
	const poster = await getUserInfo(listing.authorID);

	const emailBtn = document.getElementById("email-info-btn");
	const emailLink = document.getElementById("email-info");

	emailLink.textContent = poster.email;
	emailLink.href = `mailto:${poster.email}?subject=RegisBooks: Request for ${book.title}`;

	emailBtn.onclick = () => {
		emailLink.classList.toggle("d-none");
		emailBtn.textContent = emailLink.classList.contains("d-none") ? "Show Lister Email" : "Hide Lister Email";
	};

	document.getElementById("success-message").textContent = "You have successfully requested this listing!";

	document.getElementById("rem-listing-btn").onclick = () => {
		rejectListingReq(listingID).then((resp) => {
			if (resp.status != 200) {
				alert("Uh Oh! Something went wrong while trying to remove your request. Please try again later.");
				location.reload();
				return;
			}
			
			alert("You have successfully removed your request!");
			location.reload();
		});
	};

	document.getElementById("req-info").classList.remove("d-none");
}