
document.addEventListener("DOMContentLoaded", async () => {
	const waitingMessage = document.getElementById("waiting-message");
	waitingMessage.textContent = "Loading the leaderboard";

	const loaderAnimation = setInterval(() => {
		if (waitingMessage.textContent.slice(-3) == "...") waitingMessage.textContent = waitingMessage.textContent.slice(0, -3);

		waitingMessage.textContent+=".";
	}, 500);

	const leaderboardContent = document.getElementById("leaderboard-content");
	try {
		const userIDs = await getAllUsers();

		const users = [];

		for (const userID of userIDs) {
			const user = await getUserInfo(userID);

			users.push(user);
		}

		users.sort((a, b) => {
			const aScore = a.aura;
			const bScore = b.aura;

			// reversed terms for descending order
			return bScore - aScore;
		});

		const topUsers = users.slice(0, 10);
		
		topUsers.forEach((user, index) => {
			const userRow = document.createElement("div");
			userRow.className = "d-flex justify-content-between align-items-center border-bottom py-2";

			const rankSpan = document.createElement("span");
			rankSpan.className = "fw-bold";
			rankSpan.textContent = `#${index + 1}`;

			const nameSpan = document.createElement("span");
			nameSpan.appendChild(document.createTextNode(`${user.firstName} ${user.lastName} `));

			const usernameLink = document.createElement("a");
			usernameLink.href = `/view-profile?id=${user.id}`;
			usernameLink.textContent = `@${user.username}`;
			nameSpan.appendChild(usernameLink);
			
			const pointsSpan = document.createElement("span");
			pointsSpan.className = "text-warning";
			pointsSpan.textContent = `${user.aura} Aura`;

			userRow.appendChild(rankSpan);
			userRow.appendChild(nameSpan);
			userRow.appendChild(pointsSpan);

			leaderboardContent.appendChild(userRow);
		});

	} catch (error) {
		console.error("Error loading leaderboard:", error);
		leaderboardContent.innerHTML = `<p class="text-danger">Failed to load leaderboard. Please try again later.</p>`;
	}

	clearInterval(loaderAnimation);
	waitingMessage.remove();
});
