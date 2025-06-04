const authUrl = "https://228794087.propelauthtest.com";
const authClient = PropelAuth.createClient({ authUrl });

async function getAuthInfo() {
	return await authClient.getAuthenticationInfoOrNull();
}

async function getUser() {
	const authInfo = await getAuthInfo();

	if (authInfo) return authInfo.user;
	else {
		location.href = authUrl;
		return null;
	}
}

let userPromise = getUser();

async function useAuth(func) {
	return func(await userPromise);
}