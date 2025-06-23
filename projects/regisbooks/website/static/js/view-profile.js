const userID = new URLSearchParams(location.search).get('id');

document.addEventListener("DOMContentLoaded", async () => {
	const selfUserID = await getUserID();
	const selfProfile = userID === null || userID === selfUserID;

	let userInfo;
	
	try {
		userInfo = await getUserInfo(userID);
	} catch (err) {
		if (selfProfile) {
			alert("Please try logging in again. Make sure you are using a Regis account.");
			location.href = authUrl;
		} else {
			location.href = `/view-profile?id=${selfUserID}`;
		}
	}

	// Update page title with user's name
	const h1 = document.querySelector('h1');
	h1.textContent = '';
	const icon = elem('i', '');
	icon.className = 'bi bi-person-circle me-2';
	h1.appendChild(icon);
	h1.appendChild(selfProfile ? textElem('span', 'Dashboard') : textElem('span', `${userInfo.firstName}'s Profile`));

	// Fill in profile items using userInfo
	document.getElementById('full-name').textContent = `${userInfo.firstName} ${userInfo.lastName}`;
	document.getElementById('username').textContent = userInfo.username;
	document.getElementById('email').textContent = userInfo.email;
	document.getElementById('aura').textContent = userInfo.aura;

	const statsContainerLabel = document.getElementById('stats-container-label');
	
	if (selfProfile) {
		statsContainerLabel.textContent = 'Your Stats';
	} else {
		statsContainerLabel.textContent = `${userInfo.firstName}'s Stats`
	}

	const listingsContainerLabel = document.getElementById('listings-container-label');

	if (selfProfile) {
		listingsContainerLabel.textContent = 'Your Listings';
	} else {
		listingsContainerLabel.textContent = `${userInfo.firstName}'s Listings`;
	}

	document.getElementById('stat-listings-made').textContent = userInfo.stats.listingsMade;
	document.getElementById('stat-books-given').textContent = userInfo.stats.booksGiven;
	document.getElementById('stat-books-received').textContent = userInfo.stats.booksReceived;
	
	const listingsContainer = document.getElementById('user-listings');
	listingsContainer.textContent = '';

	const listings = await getListingsPaginateFully({ posterID: userInfo.id });
	// sort listings with status 1 (requested) to the front
	const userListings = listings.sort((a, b) => (b.status === STATUS_REQUESTED ? 1 : 0) - (a.status === STATUS_REQUESTED ? 1 : 0));

	if (userListings.length > 0) {
		for (const listing of userListings) {
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
			
			const status = listingStatusRepr[listing.status];
			const badge = textElem('span', status);
			badge.className = `badge bg-${listing.status === STATUS_AVAILABLE ? 'success' : 'warning'} ms-2`;
			
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