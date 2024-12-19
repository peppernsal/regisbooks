const bookISBN = new URLSearchParams(location.search).get("book");

if (!bookISBN) location.href = "/enter-isbn";

(async () => {
	try {
		const bookInfo = await addBook(bookISBN);
		document.getElementById("book-title").textContent = bookInfo.title;
		document.getElementById("book-author").textContent = bookInfo.author;
		document.getElementById("book-isbn").textContent = `ISBN: ${bookISBN}`;
		document.getElementById("book-publishing-info").textContent = `Published by ${bookInfo.publisher}, ${bookInfo.publishDate}`;
		document.getElementById("book-cover-img").src = bookInfo.coverImageURL;
	} catch { // book doesn't exist
		alert("Invalid ISBN!");
		location.href = "/enter-isbn";
	}
})()

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
	
	addListing(listingInfo).then(() => location.href = "/my-listings");
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
	inputElem.placeholder = "ex. Some City, XY; Regis High School; etc.";
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