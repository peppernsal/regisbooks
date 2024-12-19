const authUrl = "https://228794087.propelauthtest.com";
const authClient = PropelAuth.createClient({ authUrl });

async function getAuthInfo() {
	return await authClient.getAuthenticationInfoOrNull();
}

async function getUser() {
	const authInfo = await getAuthInfo();

	if (authInfo) return authInfo.user;
	else location.href = authUrl;
}

let userPromise = getUser();

// while (!user); // wait for user data to be fetched before returning

async function useAuth(func) {
	return func(await userPromise);
}