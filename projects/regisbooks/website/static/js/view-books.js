const booksContainer = document.getElementById('books-container');

const classFilter = document.getElementById("class-filter");
classFilter.addEventListener("change", populateBooks);

async function populateBooks() {
	classFilter.disabled = true;

	booksContainer.innerHTML = '';

	const books = await getBooks(classFilter.value);

	for (const book of books) {
		const listingCount = (await getListings({ isbn: book.isbn})).totalCount;

		if (listingCount === 0) continue;

		const bookCard = document.createElement('a');
		bookCard.className = 'card mb-3 text-decoration-none';
		bookCard.href = `/view-listings?isbn=${book.isbn}`;

		const cardBody = document.createElement('div');
		cardBody.className = 'row g-0 align-items-center';

		const coverImgContainer = document.createElement('div');
		coverImgContainer.className = 'col-md-1';
		const coverImg = document.createElement('img');
		coverImg.className = 'img-fluid detail-cover-img';
		coverImg.src = book.coverImageURL;
		coverImgContainer.appendChild(coverImg);

		const textContainer = document.createElement('div');
		textContainer.className = 'col-md-7';
		const textContent = document.createElement('div');
		textContent.className = 'card-body';

		const title = document.createElement('h5');
		title.className = 'card-title';
		title.textContent = book.title;

		const pubInfo = document.createElement('h6');
		pubInfo.className = 'card-subtitle mb-2 text-muted';
		pubInfo.textContent = `by ${book.author} (${book.publisher})`;

		const isbn = document.createElement('h6');
		isbn.className = 'card-subtitle mb-2 text-muted';
		isbn.textContent = `ISBN: ${book.isbn}`;

		textContent.appendChild(title);
		textContent.appendChild(pubInfo);
		textContent.appendChild(isbn);
		textContainer.appendChild(textContent);

		const rightContainer = document.createElement('div');
		rightContainer.className = 'col-md-4 text-end';
		const rightContent = document.createElement('div');
		rightContent.className = 'card-body';

		const listings = await getListingsPaginateFully({ isbn: book.isbn, status: STATUS_AVAILABLE });

		const listingsCountDisplay = document.createElement('h6');
		listingsCountDisplay.className = 'text-muted';
		if (listings.length == 1) {
			listingsCountDisplay.textContent = `1 listing available`;
		} else {
			listingsCountDisplay.textContent = `${listings.length} listings available`;
		}
		
		rightContent.appendChild(listingsCountDisplay);

		if (listings.length !== 0) {
			const aggrPickupLocations = listings.reduce((acc, listing) => {
				for (const location of listing.pickupLocations) {
					if (!acc.includes(location)) {
						acc.push(location);
					}
				}
				return acc;
			}, []);

			const pickupLocations = document.createElement('h6');
			pickupLocations.className = 'text-muted';

			if (aggrPickupLocations.length > 2) {
				if (aggrPickupLocations.length === 3) {
					pickupLocations.textContent = `Pickup at ${aggrPickupLocations.slice(0, 2).join(", ")}, and 1 other location`;
				} else {
					const numMore = aggrPickupLocations.length - 2;
					pickupLocations.textContent = `Pickup at ${aggrPickupLocations.slice(0, 2).join(", ")}, and ${numMore} other locations`;
				}
			} else {
				pickupLocations.textContent = `Pickup at ${aggrPickupLocations.join(", ")}`;
			}

			rightContent.appendChild(pickupLocations);
		}

		rightContainer.appendChild(rightContent);

		cardBody.appendChild(coverImgContainer);
		cardBody.appendChild(textContainer);
		cardBody.appendChild(rightContainer);
		bookCard.appendChild(cardBody);

		booksContainer.appendChild(bookCard);
	}

	classFilter.disabled = false;
}

document.addEventListener("DOMContentLoaded", populateBooks);