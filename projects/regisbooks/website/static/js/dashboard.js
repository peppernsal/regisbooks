useAuth(async (user) => {
	if (!user) return;

	let userInfo;
	
	try {
		userInfo = await getUserInfo(user.userId);
	} catch (err) {
		alert(err);
		location.href = authUrl;
	}

	// Fill in dashboard items using userInfo
	document.getElementById('full-name').textContent =  `${userInfo.firstName} ${userInfo.lastName}`;
	document.getElementById('username').textContent = userInfo.username;
	document.getElementById('email').textContent = userInfo.email;

	// Fill in stats
	document.getElementById('stat-listings-made').textContent = userInfo.stats.listingsMade;
	document.getElementById('stat-books-given').textContent = userInfo.stats.booksGiven;
	document.getElementById('stat-books-received').textContent = userInfo.stats.booksReceived;

	const listingsContainer = document.getElementById('user-listings');
	listingsContainer.textContent = '';

	const listings = await getListings({ posterID: userInfo.id});
	const userListings = listings.filter(listing => listing.status !== 2);

	if (userListings.length > 0) {
		for (const listing of userListings	) {
			const book = await getBookInfo(listing.bookID);
			const container = document.createElement('div');
			container.className = 'col-12 mb-2';
			
			const link = document.createElement('a');
			link.href = `/view-listing?id=${listing.id}`;
			link.className = 'text-decoration-none';
			
			const summary = document.createElement('div');
			summary.className = 'p-3 rounded border border-success bg-light d-flex justify-content-between align-items-center';
			
			const title = textElem('span', book.title);
			title.className = 'text-success';
			
			const status = listing.status === 0 ? 'Available' : 'Requested';
			const badge = textElem('span', status);
			badge.className = `badge bg-${listing.status === 0 ? 'success' : 'warning'} ms-2`;
			
			summary.appendChild(title);
			summary.appendChild(badge);
			link.appendChild(summary);
			container.appendChild(link);
			listingsContainer.appendChild(container);
		}
	} else {
		const alert = document.createElement('div');
		alert.className = 'col-12';
		const alertInner = textElem('div', 'No active listings found.');
		alertInner.className = 'alert alert-secondary';
		alert.appendChild(alertInner);
		listingsContainer.appendChild(alert);
	}
})