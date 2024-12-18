useAuth((user) => {
	const greeting = document.getElementById("greeting");

	greeting.textContent = `Hello, ${user.firstName} (${user.username})`
})