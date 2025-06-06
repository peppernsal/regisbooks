let listingsPageNumber = 0;

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
	populateListings();
}

populateListings();

function disableFilters() {
	filterSet.disabled = true;
	myListingsCheckbox.disabled = true;
}

function enableFilters() {
	filterSet.disabled = false;
	myListingsCheckbox.disabled = false;
}

function addLocation() {
	const locationInput = document.getElementById("location-input");
	const locationTags = document.getElementById("location-tags");

	const location = locationInput.value.trim();
	if (location === "") {
		alert("Please enter a location before clicking the + icon!");
		return;
	}

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

const nextPageButton = document.getElementById("next-page");
const prevPageButton = document.getElementById("prev-page");
const pageInfo = document.getElementById("page-info");

async function moreListingsExist() {
	const usageLevel = parseInt(document.getElementById("filter-usage").value);
	const statusLevel = parseInt(document.getElementById("filter-status").value);
	const locationTags = document.getElementById("location-tags");
	const locations = Array.from(locationTags.children).map((tag) => tag.textContent.slice(9).trim());
	const myListingsOnly = myListingsCheckbox.checked;

	const posterID = myListingsOnly ? (await getUser()).userId : undefined;

	const options = {
		name: document.getElementById("filter-name").value ?? undefined,
		isbn: document.getElementById("filter-isbn").value ?? undefined,
		locations,
		usage: usageLevel === 0 ? usageLevel : (usageLevel ?? undefined),
		status: statusLevel === 0 ? statusLevel : (statusLevel ?? undefined),
		posterID,
		page: (listingsPageNumber+1) // check if next page exists
	};

	const listings = await getListings(options);

	return listings.length > 0;
}

async function incPage() {
	listingsPageNumber++;
	await populateListings();

	prevPageButton.disabled = false;

	if (!(await moreListingsExist())) {
		nextPageButton.disabled = true;
	}

	pageInfo.textContent = `Page ${listingsPageNumber + 1}`;
}

async function decPage() {
	if (listingsPageNumber > 0) {
		listingsPageNumber--;
		await populateListings();
		
		pageInfo.textContent = `Page ${listingsPageNumber + 1}`;

		nextPageButton.disabled = false;

		if (listingsPageNumber === 0) {
			prevPageButton.disabled = true;
		}

		return;
	}

	prevPageButton.disabled = true;
}

async function populateListings() {
	disableFilters();
	listingsContainer.innerHTML = ""; // Clear previous listings

	let listings;
	
	const usageLevel = parseInt(document.getElementById("filter-usage").value);
	const statusLevel = parseInt(document.getElementById("filter-status").value);
	const locationTags = document.getElementById("location-tags");
	const locations = Array.from(locationTags.children).map((tag) => tag.textContent.slice(9).trim());
	const myListingsOnly = myListingsCheckbox.checked;

	const posterID = myListingsOnly ? (await getUser()).userId : undefined;

	const options = {
		name: document.getElementById("filter-name").value ?? undefined,
		isbn: document.getElementById("filter-isbn").value ?? undefined,
		locations,
		usage: usageLevel === 0 ? usageLevel : (usageLevel ?? undefined),
		status: statusLevel === 0 ? statusLevel : (statusLevel ?? undefined),
		posterID,
		page: listingsPageNumber
	};

	listings = await getListings(options);
	
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
			anchor.className = "btn my-1 d-block text-center listing-preview"
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

	enableFilters();
}

document.getElementById('toggle-filters').addEventListener('click', function() {
	const filters = document.querySelector('.filters');
	if (filters.style.display === 'none' || filters.style.display === '') {
		filters.style.display = 'block';
		this.textContent = 'Hide Filters/Search';
	} else {
		filters.style.display = 'none';
		this.textContent = 'Show Filters/Search';
	}
});


document.addEventListener('DOMContentLoaded', async () => {
	if (await moreListingsExist()) {
		nextPageButton.disabled = false;
	}
});