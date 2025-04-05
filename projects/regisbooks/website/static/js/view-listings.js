const listingsContainer = document.getElementById("listings-container");

const locationInput = document.getElementById("location-input");

locationInput.addEventListener("keydown", (event) => {
	if (event.key === "Enter") {
		event.preventDefault();
		addLocation();
	}
});

const nameFilter = document.getElementById("filter-name");
nameFilter.addEventListener("keydown", (event) => {
	if (event.key === "Enter") {
		event.preventDefault();
		populateListings();
	}
});

const isbnFilter = document.getElementById("filter-isbn");
isbnFilter.addEventListener("keydown", (event) => {
	if (event.key === "Enter") {
		event.preventDefault();
		populateListings();
	}
});

const usageFilter = document.getElementById("filter-usage");
usageFilter.addEventListener("change", (event) => {
	populateListings();
});

const statusFilter = document.getElementById("filter-status");
statusFilter.addEventListener("change", (event) => {
	populateListings();
});

const myListingsCheckbox = document.getElementById("show-my-listings");

const filterSet = document.getElementById("filter-set");

myListingsCheckbox.onchange = () => {
	if (myListingsCheckbox.checked) {
		filterSet.setAttribute("disabled", "");
		const locationTags = document.getElementById("location-tags");
		if (locationTags) locationTags.innerHTML = "";
	} else {
		filterSet.removeAttribute("disabled");
	}

	populateListings();
}

populateListings();

function addLocation() {
	const locationInput = document.getElementById("location-input");
	const locationTags = document.getElementById("location-tags");

	const location = locationInput.value.trim();
	if (location === "") return;

	const badge = document.createElement("span");
	badge.className = "badge bg-success text-light me-2 mb-1";
	badge.textContent = `Location: ${location}`;

	const removeBtn = document.createElement("button");
	removeBtn.className = "btn-close btn-close-white ms-2";
	removeBtn.style.fontSize = "0.6rem";
	removeBtn.onclick = () => {
		badge.remove();
		populateListings();
	};

	badge.appendChild(removeBtn);
	locationTags.appendChild(badge);

	locationInput.value = "";

	populateListings();
}

async function populateListings() {
	listingsContainer.innerHTML = ""; // Clear previous listings

	let listings;
	
	if (!myListingsCheckbox.checked) {
		const usageLevel = parseInt(document.getElementById("filter-usage").value);
		const statusLevel = parseInt(document.getElementById("filter-status").value);
		const locationTags = document.getElementById("location-tags");
		const locations = Array.from(locationTags.children).map((tag) => tag.textContent.slice(9).trim());

		const options = {
			name: document.getElementById("filter-name").value ?? undefined,
			isbn: document.getElementById("filter-isbn").value ?? undefined,
			locations,
			usage: usageLevel === 0 ? usageLevel : (usageLevel ?? undefined),
			status: statusLevel === 0 ? statusLevel : (statusLevel ?? undefined),
		};

		listings = await getListings(options);
	} else {
		listings = await getMyListings();
	}
	
	for (let i = 0; i < listings.length; i+=2) {
		const group = listings.slice(i, i+2);

		const row = document.createElement("div");
		row.className = "row";

		for (const listingInfo of group) {
			const summaryDiv = document.createElement("div");
			summaryDiv.className = "col-md-6 listing-preview-parent";

			const bookInfo = await getBookInfo(listingInfo.bookID);

			const titleContainer = document.createElement("h4");
			titleContainer.append(
				textElem('i', bookInfo.title),
				textElem("span", ` by ${bookInfo.author}`),
			);

			const anchor = document.createElement("a");
			anchor.className = "btn btn-success my-1 d-block text-center listing-preview"
			anchor.href = `/view-listing?id=${listingInfo.id}`;

			if (bookInfo.coverImageURL !== "<no-url>") {
				const coverImg = document.createElement("img");
				coverImg.className = "img-fluid scaled-cover-image";
				coverImg.src = bookInfo.coverImageURL;

				anchor.append(coverImg);
			}

			anchor.appendChild(titleContainer);

			summaryDiv.appendChild(anchor);

			const usageString = listingUsageRepr[listingInfo.usageLevel];
			const statusString = listingStatusRepr[listingInfo.status];

			anchor.append(
				textElem('h6', `Status: ${statusString}`),
				textElem('h6', `Condition: ${usageString}`),
			);

			if (listingInfo.pickupLocations.length > 2) {
				if (listingInfo.pickupLocations.length === 3) {
					anchor.append(
						textElem('h6', `Pickup at ${listingInfo.pickupLocations.slice(0, 2).join(", ")}, and 1 other location`)
					);
				}
				else
				{
					const numMore = listingInfo.pickupLocations.length - 2;

					anchor.append(
						textElem('h6', `Pickup at ${listingInfo.pickupLocations.slice(0, 2).join(", ")}, and ${numMore} other locations`)
					);
				}
			}
			else
			{
				anchor.append(
					textElem('h6', `Pickup at ${listingInfo.pickupLocations.join(", ")}`)
				);
			}

			row.appendChild(summaryDiv);
		}

		listingsContainer.appendChild(row);
	}
}