const listingsContainer = document.getElementById("listings-container");

(async () => {
	const listings = await getMyListings();
	
	for (const listingInfo of listings) {
		const summaryDiv = document.createElement("div");
		summaryDiv.className = "col-md-6";

		const bookInfo = await getBookInfo(listingInfo.bookID);

		const titleContainer = document.createElement("h4");
		titleContainer.append(
			textElem('i', bookInfo.title),
			textElem("span", ` by ${bookInfo.author}`),
		);

		const anchor = document.createElement("a");
		anchor.className = "btn btn-success my-1  d-block text-center"
		anchor.href = `/view-listing?id=${listingInfo.id}`;

		anchor.appendChild(titleContainer);

		summaryDiv.appendChild(anchor);

		const usageString = listingUsageRepr[listingInfo.usageLevel];
		const statusString = listingStatusRepr[listingInfo.status];

		anchor.append(
			textElem('h6', `Status: ${statusString}`),
			textElem('h6', `Condition: ${usageString}`),
		);

		if (listingInfo.pickupLocations.length > 2) {
			if (listingInfo.pickupLocations.length === 3) {
				anchor.append(
					textElem('h6', `Pickup at ${listingInfo.pickupLocations.slice(0, 2).join(", ")}, and 1 other location`)
				);
			}
			else
			{
				const numMore = listingInfo.pickupLocations.length - 2;

				anchor.append(
					textElem('h6', `Pickup at ${listingInfo.pickupLocations.slice(0, 2).join(", ")}, and ${numMore} other locations`)
				);
			}
		}
		else
		{
			anchor.append(
				textElem('h6', `Pickup at ${listingInfo.pickupLocations.join(", ")}`)
			);
		}

		listingsContainer.appendChild(summaryDiv);
	}
})();