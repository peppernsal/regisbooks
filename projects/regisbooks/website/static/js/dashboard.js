useAuth(async (user) => {
	const userInfo = await getUserInfo(user.userId);

	console.log(userInfo);
})