function confirmLogout() {
	authClient.logout().then(() => {
		location.href = authUrl;
	});
}

function cancelLogout() {
	window.location.href = '/view-profile';
}

document.getElementById("confirm-logout").addEventListener("click", confirmLogout);
document.getElementById("cancel-logout").addEventListener("click", cancelLogout);