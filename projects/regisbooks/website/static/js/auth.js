// force deprecate regisbooks.onrender.com
if (location.hostname === "regisbooks.onrender.com") {
	location.hostname = "regisbooks.org";
}

if (Cookies.get("accepted") !== "true") location.href = "/acknowledgement";

const DEBUG = true;

let authUrl;

if (DEBUG) {
	authUrl = "https://228794087.propelauthtest.com";
} else {
	authUrl = "https://auth.regisbooks.org";
}

const authClient = PropelAuth.createClient({ authUrl });

const authInfoPromise = authClient.getAuthenticationInfoOrNull();

authInfoPromise.catch((err) => {
	alert("Login failed. Please try using a different browser (e.g. Chrome) or disabling incognito mode/third party cookie protection.")
});

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

async function getUserID() {
	const user = await getUser();

	// prioritize legacyId to support legacy users in DB
	if (user) return user.legacyUserId || user.userId;
	else return null;
}

async function useAuth(func) {
	return func(await userPromise);
}