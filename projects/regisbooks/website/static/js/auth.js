if (Cookies.get("accepted") !== "true") location.href = "/acknowledgement";

const authUrl = "https://228794087.propelauthtest.com";
const authClient = PropelAuth.createClient({ authUrl });

const authInfoPromise = authClient.getAuthenticationInfoOrNull();

// cache user auth data
async function getAuthInfo() {
	return await authInfoPromise;
}

async function getUserInternal() {
	const authInfo = await getAuthInfo();

	if (authInfo) return authInfo.user;
	else {
		location.href = authUrl;
		return null;
	}
}

let userPromise = getUserInternal();

// cache user auth data
async function getUser() {
	return await userPromise;
}

async function useAuth(func) {
	return func(await userPromise);
}