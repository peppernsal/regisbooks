function elem(tag, innerHTML) {
	const elem = document.createElement(tag);

	elem.innerHTML = innerHTML;

	return elem;
}

function textElem(tag, text) {
	const elem = document.createElement(tag);

	elem.textContent = text;

	return elem;
}

function createUserLink(user) {
    const link = textElem('a', `${user.firstName} ${user.lastName}`);
    link.href = `/view-profile?id=${user.id}`;
    link.className = 'user-link';
    return link;
}

function createStatsCard(label, value) {
	const card = document.createElement('div');
	card.className = 'stats-card card-hover';

	const number = textElem('div', value);
	number.className = 'stats-number';

	const labelElem = textElem('div', label);
	labelElem.className = 'stats-label';

	card.append(number, labelElem);
	return card;
}

function createListingCard(listing, book) {
	const container = document.createElement('div');
	container.className = 'col-12 mb-2 fade-in';
	
	const link = document.createElement('a');
	link.href = `/view-listing?id=${listing.id}`;
	link.className = 'card-link';
	
	const card = document.createElement('div');
	card.className = 'listing-card card-hover d-flex justify-content-between align-items-center';
	
	const leftSide = document.createElement('div');
	const title = textElem('h5', book.title);
	title.className = 'mb-1 text-success';
	const author = textElem('div', `by ${book.author}`);
	author.className = 'text-muted';
	leftSide.append(title, author);
	
	const rightSide = document.createElement('div');
	const status = listing.status === 0 ? 'Available' : 'Requested';
	const badge = textElem('span', status);
	badge.className = `badge bg-${listing.status === 0 ? 'success' : 'warning'} ms-2`;
	rightSide.appendChild(badge);
	
	card.append(leftSide, rightSide);
	link.appendChild(card);
	container.appendChild(link);
	
	return container;
}

function createBookCover(book) {
	const container = document.createElement('div');
	container.className = 'text-center mb-3';

	if (book.coverImageURL !== "<no-url>") {
		const img = document.createElement('img');
		img.src = book.coverImageURL;
		img.alt = `${book.title} cover`;
		img.className = 'img-fluid rounded shadow-sm';
		img.style.maxHeight = '300px';
		container.appendChild(img);
	}

	return container;
}