const bookISBN = new URLSearchParams(location.search).get("book");

const waitingMessage = document.getElementById("waiting-message");
waitingMessage.textContent = `Loading book from ISBN ${bookISBN}`;

const loaderAnimation = setInterval(() => {
	if (waitingMessage.textContent.slice(-3) == "...") waitingMessage.textContent = waitingMessage.textContent.slice(0, -3);

	waitingMessage.textContent+=".";
}, 500);

if (!bookISBN) location.href = "/enter-isbn";

(async () => {
	try {
		const bookInfo = await addBook(bookISBN);
		document.getElementById("book-title").textContent = bookInfo.title;
		document.getElementById("book-author").textContent = bookInfo.author;
		document.getElementById("book-isbn").textContent = `ISBN: ${bookISBN}`;
		document.getElementById("book-publishing-info").textContent = `Published by ${bookInfo.publisher}, ${bookInfo.publishDate}`;
		
		if (bookInfo.coverImageURL != "<no-url>") {
			document.getElementById("book-cover-img").src = bookInfo.coverImageURL;
			document.getElementById("cover-disclaimer").textContent = "Note: cover image and publisher may not match physical book. Check ISBN to match versions.";
		} else {
			document.getElementById("book-cover-img").remove();
			document.getElementById("cover-disclaimer").remove();
		}

		clearInterval(loaderAnimation);
		waitingMessage.remove();
	} catch { // book doesn't exist
		alert("Invalid ISBN!");
		location.href = "/enter-isbn";
	}
})();

function createListing() {
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

	const listingInfo = {
		bookID: bookISBN,
		usageLevel: parseInt(usageLevel),
		notes: notes,
		pickupLocations: pickupLocations,
	}

	console.log(listingInfo);
	
	addListing(listingInfo).then(() => location.href = "/view-listings");
}

const locationsContainer = document.getElementById("pickup-locations-container");;

function addPickupLocation() {
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
	};

	removeDiv.appendChild(removeBtn);

	innerDiv.append(inputDiv, removeDiv);

	locationsContainer.append(innerDiv);

	window.scrollTo({
		top: document.body.scrollHeight, 
		behavior: 'smooth'
	});
}