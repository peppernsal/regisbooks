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

	const statsContainerLabel = document.getElementById('stats-container-label-text');
	
	if (selfProfile) {
		statsContainerLabel.textContent = 'Your Stats';
	} else {
		statsContainerLabel.textContent = `${userInfo.firstName}'s Stats`
	}

	const listingsContainerLabel = document.getElementById('listings-container-label-text');

	if (selfProfile) {
		listingsContainerLabel.textContent = 'Your Listings';
	} else {
		listingsContainerLabel.textContent = `${userInfo.firstName}'s Listings`;
	}

	const badgesContainerLabel = document.getElementById('badges-container-label-text');

	if (selfProfile) {
		badgesContainerLabel.textContent = 'Your Badges';
	} else {
		badgesContainerLabel.textContent = `${userInfo.firstName}'s Badges`;
	}

	document.getElementById('stat-listings-made').textContent = userInfo.stats.listingsMade;
	document.getElementById('stat-books-given').textContent = userInfo.stats.booksGiven;
	document.getElementById('stat-books-received').textContent = userInfo.stats.booksReceived;
	
	// fill badges and notify if needed
	const displayBadges = await getUpdatedAchievedBadges(userInfo.id);

	// display new badges and notify if on own profile page
	if (selfProfile) {
		const newBadges = displayBadges.filter((badge) => !userInfo.badges.some((achievedBadge) => {
			return achievedBadge.name === badge.name
		}));

		if (newBadges.length > 0) {

			displayBadgeAchievementModal(newBadges)

			await updateAchievedBadges(); // ensure the user doesn't get notified again
		}
	}

	const badgesDisplayContainer = document.getElementById("badges-display-container");

	badgesDisplayContainer.innerHTML = '';
	
	let row;

	displayBadges.forEach((badge, i) => {
		if (i % 6 === 0) {
			row = document.createElement('div');
			row.className = 'row mb-3';
			badgesDisplayContainer.appendChild(row);
		}
		const badgeWrapper = document.createElement('div');
		badgeWrapper.className = 'text-center col-md-2';

		const badgeImg = document.createElement('img');
		badgeImg.src = badge.imageURL;
		badgeImg.alt = badge.name;
		badgeImg.className = 'badge-img';
		badgeImg.title = badge.description;
		badgeImg.setAttribute('data-bs-toggle', 'tooltip');
		badgeImg.setAttribute('data-bs-placement', 'top');

		const caption = document.createElement('div');
		caption.className = 'badge-caption mt-1';
		caption.textContent = badge.name;

		badgeWrapper.appendChild(badgeImg);
		badgeWrapper.appendChild(caption);
		row.appendChild(badgeWrapper);
	});
	
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
});

function displayBadgeAchievementModal(newBadges) {
	const existingModal = document.getElementById('badge-achievement-modal');
	if (existingModal) existingModal.remove();

	const modal = document.createElement('div');
	modal.className = 'modal fade';
	modal.id = 'badge-achievement-modal';
	modal.tabIndex = -1;
	modal.setAttribute('aria-labelledby', 'badge-achievement-modal-label');
	modal.setAttribute('aria-hidden', 'true');

	// XSS-safe because badge data is static and unsettable by users on the server side
	modal.innerHTML = `
		<div class="modal-dialog modal-dialog-centered">
		<div class="modal-content">
			<div class="modal-header bg-success text-white">
			<h5 class="modal-title" id="badge-achievement-modal-label">New Badge${newBadges.length > 1 ? 's' : ''} Unlocked!</h5>
			<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
			</div>
			<div class="modal-body text-center">
			<div class="mb-3">${newBadges.map(badge => `
				<div class="d-inline-block m-2 text-center">
				<img src="${badge.imageURL}" alt="${badge.name}" class="badge-img mb-1">
				<div class="fw-bold">${badge.name}</div>
				<div class="small text-muted">${badge.description}</div>
				</div>
			`).join('')}</div>
			<div class="alert alert-success">Congratulations! You have unlocked ${newBadges.length} new badge${newBadges.length > 1 ? 's' : ''}.</div>
			</div>
			<div class="modal-footer">
			<button type="button" class="btn btn-success" data-bs-dismiss="modal">OK</button>
			</div>
		</div>
		</div>
	`;
	document.body.appendChild(modal);

	const modalInstance = new window.bootstrap.Modal(modal);
	modalInstance.show();
}