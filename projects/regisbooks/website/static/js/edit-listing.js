const listingID = new URLSearchParams(location.search).get("id");

const waitingMessage = document.getElementById("waiting-message");
waitingMessage.textContent = `Loading your listing`;

const loaderAnimation = setInterval(() => {
	if (waitingMessage.textContent.slice(-3) == "...") waitingMessage.textContent = waitingMessage.textContent.slice(0, -3);

	waitingMessage.textContent+=".";
}, 500);

if (!listingID) location.href = "/view-listings";

document.addEventListener("DOMContentLoaded", async () => {
	try {
		const user = await getUser();
		const listingInfo = await getListingInfo(listingID);
		const bookInfo = await getBookInfo(listingInfo.bookID);

		if (listingInfo.authorID != user.userId) {
			alert("You do not have permission to edit this listing!");
			location.href = `/view-listing?id=${listingID}`;
		}

		document.getElementById("book-title").textContent = bookInfo.title;
		document.getElementById("book-author").textContent = bookInfo.author;
		document.getElementById("book-isbn").textContent = `ISBN: ${bookInfo.id}`;
		document.getElementById("book-publishing-info").textContent = `Published by ${bookInfo.publisher}, ${bookInfo.publishDate}`;
		
		document.getElementById("book-cover-img").src = bookInfo.coverImageURL;
		document.getElementById("cover-disclaimer").textContent = "Note: cover image and publisher may not match physical book. Check ISBN to match versions.";
	

		document.getElementById("usage-level").value = listingInfo.usageLevel;
		document.getElementById("notes").value = listingInfo.notes;
		
		for (const location of listingInfo.pickupLocations) {
			const inputElem = addPickupLocation();
			inputElem.value = location;
		}

		clearInterval(loaderAnimation);
		waitingMessage.remove();
	} catch (err) {		
		location.href = `/view-listing?id=${listingID}`;
	}
});

function editListing() {
	const usageLevel = document.getElementById("usage-level").value;
	const notes = document.getElementById("notes").value;
	const pickupLocations = Array.from(
		document.querySelectorAll(".pickup-location")
	).map((el) => el.value).filter((el) => el !== "");
	
	if (usageLevel === "") {
		alert("Please fill the usage level field!");
		return;
	}

	if (pickupLocations.length === 0) {
		alert("Please specify at least one pickup location!");
		return;
	}

	if (pickupLocations.length > 5) {
		alert("You cannot specify more than 5 pickup locations!");
		return;
	}

	const updateInfo = {
		listingID,
		usageLevel: parseInt(usageLevel),
		notes,
		pickupLocations,
	}
	
	updateListing(updateInfo)
		.then((response) => {
			if (response.status !== 200) {
				alert("Failed to update listing. Please try again.");
			}

			location.href = `/view-listing?id=${listingID}`;
		});
}

const locationsContainer = document.getElementById("pickup-locations-container");;

function addPickupLocation() {
	const numberOfPickupLocations = document.querySelectorAll(".pickup-location").length;

	if (numberOfPickupLocations >= 4) { document.getElementById("add-pickup-location").disabled = true; }
	

	const innerDiv = document.createElement("div");
	innerDiv.className = "row pt-3 justify-content-center";

	const textDiv = document.createElement("div");
	textDiv.className = "col-3";

	textDiv.appendChild(textElem("h4", "Pickup Location: "))

	const inputDiv = document.createElement("div");
	inputDiv.className = "col-5 offset-1";

	const inputElem = document.createElement("input");
	
	inputElem.type = "text";
	inputElem.placeholder = "ex. Fairfield, CT";

	// animate example text
	setInterval(() => {
		if (inputElem.value != "") return;

		if (inputElem.placeholder == "ex. Fairfield, CT") {
			const nextExample = "ex. Regis High School";

			for (let i = 0; i < nextExample.length; i++) {
				if (i < inputElem.placeholder.length) {
					setTimeout(() => {
						inputElem.placeholder = nextExample.slice(0, i+1)+inputElem.placeholder.slice(i+1);
					}, 50 * i);
				} else {
					setTimeout(() => {
						inputElem.placeholder+=nextExample[i];
					}, 50 * i);
				}
			}

			setTimeout(() => {
				inputElem.placeholder = nextExample; // ensure set
			}, 50 * nextExample.length);
		} else {
			const nextExample = "ex. Fairfield, CT";

			for (let i = 0; i < nextExample.length; i++) {
				if (i < inputElem.placeholder.length) {
					setTimeout(() => {
						inputElem.placeholder = nextExample.slice(0, i+1)+inputElem.placeholder.slice(i+1);
					}, 50 * i);
				} else {
					setTimeout(() => {
						inputElem.placeholder+=nextExample[i];
					}, 50 * i);
				}
			}

			setTimeout(() => {
				inputElem.placeholder = nextExample; // ensure set
			}, 50 * nextExample.length);
		}
	}, 3000);

	inputElem.className = "form-control pickup-location";

	inputDiv.appendChild(inputElem);

	const removeDiv = document.createElement("div");
	removeDiv.className = "col-2";
	
	const removeBtn = document.createElement("button");
	removeBtn.textContent = "Remove";
	removeBtn.className = "btn btn-danger";

	removeBtn.onclick = () => {
		innerDiv.remove();

		const numberOfPickupLocations = document.querySelectorAll(".pickup-location").length;

		if (numberOfPickupLocations <= 4) { document.getElementById("add-pickup-location").disabled = false; }
	};

	removeDiv.appendChild(removeBtn);

	innerDiv.append(inputDiv, removeDiv);

	locationsContainer.append(innerDiv);

	window.scrollTo({
		top: document.body.scrollHeight, 
		behavior: 'smooth'
	});

	return inputElem;
}