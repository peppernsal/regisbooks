useAuth(async (user) => {
	const userInfo = await getUserInfo(user.userId);

	// Fill in dashboard items using userInfo
	document.getElementById('full-name').textContent = userInfo.name || '';
	document.getElementById('username').textContent = userInfo.username || '';
	document.getElementById('email').textContent = userInfo.email || '';

	// Fill in stats
	document.getElementById('stat-listings-made').textContent = userInfo.stats?.listingsMade ?? 0;
	document.getElementById('stat-books-given').textContent = userInfo.stats?.booksGiven ?? 0;
	document.getElementById('stat-books-received').textContent = userInfo.stats?.booksReceived ?? 0;

	// Fill in user listings using utils
	const listingsContainer = document.getElementById('user-listings');
	listingsContainer.innerHTML = '';
	if (Array.isArray(userInfo.listings) && userInfo.listings.length > 0) {
		userInfo.listings.forEach(listing => {
			const col = document.createElement('div');
			col.className = 'col';

			const card = document.createElement('div');
			card.className = 'card border-success';

			const cardBody = document.createElement('div');
			cardBody.className = 'card-body';

			const title = textElem('h5', listing.title);
			title.className = 'card-title';

			const desc = textElem('p', listing.description || '');
			desc.className = 'card-text';

			const badge = textElem('span', listing.status || '');
			badge.className = 'badge bg-success';

			cardBody.appendChild(title);
			cardBody.appendChild(desc);
			cardBody.appendChild(badge);
			card.appendChild(cardBody);
			col.appendChild(card);
			listingsContainer.appendChild(col);
		});
	} else {
		listingsContainer.appendChild(
			elem('div', `<div class="alert alert-secondary">No listings found.</div>`)
		).className = 'col';
	}
})