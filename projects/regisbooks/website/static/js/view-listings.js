const listingsContainer = document.getElementById("listings-container");

(async () => {
	const listings = await getListings();
	
	for (const listingInfo of listings) {
		const summaryDiv = document.createElement("div");

		const bookInfo = await getBookInfo(listingInfo.bookID);

		const anchor = textElem('a', bookInfo.title);
		anchor.className = "btn btn-success my-1  d-block text-center"
		anchor.href = `/view-listing?id=${listingInfo.id}`;

		summaryDiv.appendChild(anchor);

		const usageString = listingUsageRepr[listingInfo.usageLevel];
		const statusString = listingStatusRepr[listingInfo.status];

		summaryDiv.append(
			textElem('h4', `Status: ${statusString}`),
			textElem('h5', `Condition: ${usageString}`),
		);

		if (listingInfo.pickupLocations.length > 2) {
			const numMore = listingInfo.pickupLocations.length - 2;

			summaryDiv.append(
				textElem('h5', `Pickup locations: ${listingInfo.pickupLocations.slice(0, 2).join(", ")}, and ${numMore} others`)
			);
		}
		else
		{
			summaryDiv.append(
				textElem('h5', `Pickup locations: ${listingInfo.pickupLocations.join(", ")}`)
			);
		}

		listingsContainer.appendChild(summaryDiv);
	}
})();