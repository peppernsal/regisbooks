const listingsContainer = document.getElementById("listings-container");

const clearFiltersBtn = document.getElementById("clear-filters");
const locationTags = document.getElementById("location-tags");

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
		newSearch();
	}
});

const isbnFilter = document.getElementById("filter-isbn");
isbnFilter.addEventListener("keydown", (event) => {
	if (event.key === "Enter") {
		event.preventDefault();
		newSearch();
	}
});

const classFilter = document.getElementById("filter-usage");
classFilter.addEventListener("change", (event) => {
	newSearch();
});

const statusFilter = document.getElementById("filter-status");
statusFilter.addEventListener("change", (event) => {
	newSearch();
});

const myListingsCheckbox = document.getElementById("show-my-listings");

const filterSet = document.getElementById("filter-set");

myListingsCheckbox.onchange = () => {
	newSearch();
}

function clearFilters() {
	nameFilter.value = "";
	isbnFilter.value = "";
	classFilter.value = "";
	statusFilter.value = "";
	myListingsCheckbox.checked = false;
	locationTags.innerHTML = "";

	populateListings();
}

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

	const location = locationInput.value.trim();
	if (location === "") {
		alert("Please enter a location before clicking the + icon!");
		return;
	}

	addLocationFromString(location);

	locationInput.value = "";

	newSearch();
}

function addLocationFromString(loc) {
	const badge = document.createElement("span");
	badge.className = "badge bg-success text-light me-2 mb-1";
	badge.textContent = `Location: ${loc}`;

	const removeBtn = document.createElement("button");
	removeBtn.className = "btn-close btn-close-white ms-2";
	removeBtn.style.fontSize = "0.6rem";
	removeBtn.onclick = () => {
		badge.remove();
		populateListings();
	};

	badge.appendChild(removeBtn);
	locationTags.appendChild(badge);
}

const nextPageButton = document.getElementById("next-page");
const prevPageButton = document.getElementById("prev-page");
const pageInfo = document.getElementById("page-info");

async function disablePaginationButtonsForListingPopulation() {
	nextPageButton.disabled = true;
	prevPageButton.disabled = true;

	const pageButtonContainer = document.getElementById("page-buttons-container");

	for (const button of pageButtonContainer.children) {
		button.disabled = true;
	}
}

async function updatePaginationButtonStates(startingNumber, endingNumber, totalCount) {
	if (listingsPageNumber === 0) {
		prevPageButton.disabled = true;
	} else {
		prevPageButton.disabled = false;
	}

	if (endingNumber < totalCount) {
		nextPageButton.disabled = false;
	} else {
		nextPageButton.disabled = true;
	}

	pageInfo.textContent = `Page ${listingsPageNumber + 1} (showing ${startingNumber}-${endingNumber} of ${totalCount} filtered listings)`;
}

async function incPage() {
	listingsPageNumber++;
	await populateListings();
}

async function decPage() {
	if (listingsPageNumber > 0) {
		listingsPageNumber--;
		await populateListings();
	}
}

async function newSearch() {
	listingsPageNumber = 0;

	await populateListings();
}

async function populateListings() {
	disableFilters();
	disablePaginationButtonsForListingPopulation();

	listingsContainer.innerHTML = ""; // Clear previous listings

	const usageLevel = parseInt(document.getElementById("filter-usage").value);
	const statusLevel = parseInt(document.getElementById("filter-status").value);
	const locationTags = document.getElementById("location-tags");
	const locations = Array.from(locationTags.children).map((tag) => tag.textContent.slice(9).trim());
	const myListingsOnly = myListingsCheckbox.checked;

	const posterID = myListingsOnly ? await getUserID() : undefined;

	const options = {
		name: document.getElementById("filter-name").value ?? undefined,
		isbn: document.getElementById("filter-isbn").value ?? undefined,
		locations,
		usage: usageLevel === 0 ? usageLevel : (usageLevel ?? undefined),
		status: statusLevel === 0 ? statusLevel : (statusLevel ?? undefined),
		posterID,
		page: listingsPageNumber
	};

	const {
		listings, bookRef, totalCount
	} = await getListings(options);

	const start = listingsPageNumber*LISTINGS_PER_PAGE;
	const end = start+listings.length;

	for (let i = 0; i < listings.length; i+=2) {
		const group = listings.slice(i, i+2);

		const row = document.createElement("div");
		row.className = "row";

		for (const listingInfo of group) {
			const summaryDiv = document.createElement("div");
			summaryDiv.className = "col-md-6 listing-preview-parent";

			const bookInfo = bookRef[listingInfo.bookID];

			const titleContainer = document.createElement("h4");
			titleContainer.append(
				textElem('i', bookInfo.title),
				textElem("span", ` by ${bookInfo.author}`),
			);

			const anchor = document.createElement("a");
			anchor.className = "btn my-1 d-block text-center listing-preview"
			anchor.href = `/view-listing?id=${listingInfo.id}`;

			const coverImg = document.createElement("img");
			coverImg.className = "img-fluid scaled-cover-image";
			coverImg.src = bookInfo.coverImageURL;

			anchor.append(coverImg);

			anchor.appendChild(titleContainer);

			summaryDiv.appendChild(anchor);

			const usageString = listingUsageRepr[listingInfo.usageLevel];
			const statusString = listingStatusRepr[listingInfo.status];

			let statusLabel;

			if (listingInfo.status == STATUS_REQUESTED) {
				statusLabel = document.createElement("h6");
				statusLabel.innerHTML = `Status: <span class="text-warning">${statusString}</span>`;
			} else { // STATUS_AVAILABLE, the API route cannot return STATUS_GIVEN
				statusLabel = document.createElement("h6");
				statusLabel.innerHTML = `Status: <span class="text-success">${statusString}</span>`;
			}

			anchor.append(
				statusLabel,
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

	await updatePaginationButtonStates(end == 0 ? 0 : start+1, end, totalCount);

	const numberOfPages = Math.ceil(totalCount/10);
	const pageButtonContainer = document.getElementById("page-buttons-container");
	pageButtonContainer.innerHTML = "";

	if (numberOfPages <= 10) {
		for (let i = 0; i < numberOfPages; i++) {
			pageButtonContainer.appendChild(
				createPageJumpButton(i)
			);
		}
	} else { /* numberOfPages > 10 */
		let start, end;

		if (listingsPageNumber == 0) {
			start = 0;
			end = 9;
		} else if (listingsPageNumber >= (numberOfPages-1-9)) {
			start = numberOfPages-10;
			end = numberOfPages-1;
		} else {
			start = listingsPageNumber;
			end = Math.min(listingsPageNumber+9, numberOfPages-1);
		}

		for (let i = start; i <= end; i++) {
			pageButtonContainer.appendChild(
				createPageJumpButton(i)
			);
		}
	}

	searchParams.set("page", listingsPageNumber);
	searchParams.set("name", nameFilter.value);
	searchParams.set("isbn", isbnFilter.value);
	searchParams.set("usage", classFilter.value);
	searchParams.set("status", statusFilter.value);
	searchParams.set("myListings", myListingsCheckbox.checked);
	searchParams.set("locations", Array.from(locationTags.children).map(tag => tag.textContent.slice(9).trim()).join(","));

	window.history.replaceState({}, '', `${location.pathname}?${searchParams.toString()}`);

	enableFilters();
}

function createPageJumpButton(pageNum) {
	const btn = document.createElement("button");
	btn.className = "btn body-btn-primary btn-primary mx-2 px-3"
	btn.textContent = (pageNum+1).toString();
	btn.onclick = async () => {
		listingsPageNumber = pageNum;
		await populateListings();
	}

	if (pageNum == listingsPageNumber) { // current page button
		btn.disabled = true;
	}

	return btn;
}

document.getElementById('toggle-filters').addEventListener('click', function() {
	const filters = document.querySelector('.filters');
	if (filters.classList.contains('d-none')) {
		filters.classList.replace('d-none', 'd-block');
		clearFiltersBtn.classList.remove('d-none');
		this.textContent = 'Hide Filters/Search';
	} else {
		filters.classList.replace('d-block', 'd-none');
		clearFiltersBtn.classList.add('d-none');
		this.textContent = 'Show Filters/Search';
	}
});

const searchParams = new URLSearchParams(window.location.search);

let listingsPageNumber = searchParams.get("page") ? parseInt(searchParams.get("page")) : 0;

if (isNaN(listingsPageNumber) || listingsPageNumber < 0) {
	listingsPageNumber = 0;
}

nameFilter.value = searchParams.get("name") || "";
isbnFilter.value = searchParams.get("isbn") || "";
classFilter.value = searchParams.get("usage") || "";
statusFilter.value = searchParams.get("status") || "0";
myListingsCheckbox.checked = searchParams.get("myListings") === "true";
const locationFilterString = searchParams.get("locations") || "";
const locationFilterArray = locationFilterString.split(",").map(loc => loc.trim()).filter(loc => loc !== "");

for (const loc of locationFilterArray) {
	addLocationFromString(loc);
}

document.getElementById("clear-filters").addEventListener("click", clearFilters);
document.getElementById("search-btn").addEventListener("click", newSearch);
document.getElementById("add-location").addEventListener("click", addLocation);
document.getElementById("prev-page").addEventListener("click", decPage);
document.getElementById("next-page").addEventListener("click", incPage);

populateListings();