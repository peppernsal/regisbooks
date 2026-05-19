// authInfo should be defined prior to loading this library

const USAGE_LIKE_NEW = 0;
const USAGE_LIGHT = 1;
const USAGE_USED = 2;


const STATUS_AVAILABLE = 0;
const STATUS_REQUESTED = 1;
const STATUS_GIVEN = 2;

const listingUsageRepr = ["Like New", "Lightly Used", "Used"];
const listingStatusRepr = ["Available", "Requested", "Given Away"];
const classRepr = [
	"Freshman",
	"Sophomore",
	"Junior",
	"Senior"
]
const subjectAreaRepr = [
	"Art",
	"Music",
	"Science",
	"Math",
	"History",
	"English",
	"Computer Science",
	"Theology",
	"French",
	"Spanish",
	"German",
	"Latin",
	"Chinese",
	"Other"
]

async function makeAPICall(endpoint, body, method, extraHeaders) {
	return await fetch(endpoint, {
		headers: {
			Authorization: `Bearer ${(await getAuthInfo()).accessToken}`,
			...extraHeaders
		},
		method,
		body
	})
}

async function getJSONInfoFromAPICall(endpoint, body, method, headers) {
	return await (await makeAPICall(endpoint, body, method, headers)).json()
}

async function getUserInfo(userID) {
	if (!userID) return await getJSONInfoFromAPICall(`/api/internal/get-user?id=${await getUserID()}`);

	return await getJSONInfoFromAPICall(`/api/internal/get-user?id=${userID}`);
}

function getUpdatedAchievedBadges(userID) {
	return getJSONInfoFromAPICall(`/api/internal/get-updated-achieved-badges?id=${userID}`);
}

function updateAchievedBadges() {
	return makeAPICall(`/api/internal/update-achieved-badges`);
}

function getAllUsers() {
	return getJSONInfoFromAPICall(`/api/internal/get-users`);
}

function getLeaderboard() {
	return getJSONInfoFromAPICall(`/api/internal/get-leaderboard`);
}

function getListingInfo(listingID) {
	return getJSONInfoFromAPICall(`/api/internal/get-listing?id=${listingID}`);
}

function getBookInfo(bookID) {
	return getJSONInfoFromAPICall(`/api/internal/get-book?id=${bookID}`);
}


function getBooks(classFilter) {
	if (classFilter !== undefined && classFilter !== "") {
		return getJSONInfoFromAPICall(`/api/internal/get-books?class=${classFilter}`);
	}

	return getJSONInfoFromAPICall(`/api/internal/get-books`);
}

function getListings(options) {
	return getJSONInfoFromAPICall(`/api/internal/get-listings`, JSON.stringify(options), "POST", {
		"Content-Type": "application/json"
	});
}

async function getListingsPaginateFully(options) {
	const listings = [];

	let page = 0;
	while (true) {
		const res = (await getListings({ ...options, page }));

		if (res.listings.length > 0) {
			listings.push(...res.listings);
		} else break;

		page++;
	}

	return listings;
}

function getMyListings() {
	return getJSONInfoFromAPICall(`/api/internal/my-listings`);
}

function getOpenReqs() {
	return getJSONInfoFromAPICall(`/api/internal/get-open-reqs`);
}

function addListing(listingInfo) {
	return makeAPICall(`/api/internal/add-listing`, JSON.stringify(listingInfo), "POST", {
		"Content-Type": "application/json"
	});
}

function updateListing(listingInfo) {
	return makeAPICall(`/api/internal/update-listing`, JSON.stringify(listingInfo), "POST", {
		"Content-Type": "application/json"
	});
}

function updatePhoneNumber(phoneNumber) {
	return makeAPICall(`/api/internal/update-phone-number?number=${phoneNumber}`);
}

function addBook(bookISBN) {
	return getJSONInfoFromAPICall(`/api/internal/add-book?isbn=${bookISBN}`);
}

function addPreReq(preReqInfo) {
	return getJSONInfoFromAPICall(`/api/internal/add-pre-req`, JSON.stringify(preReqInfo), "POST", {
		"Content-Type": "application/json"
	});
}

function remListing(listingID) {
	return makeAPICall(`/api/internal/rem-listing?id=${listingID}`);
}

function remPreReq(preReqID) {
	return makeAPICall(`/api/internal/rem-pre-req?id=${preReqID}`);
}

function remBook(bookID) {
	return makeAPICall(`/api/internal/rem-book?id=${bookID}`);
}

function reqListing(listingID) {
	return makeAPICall(`/api/internal/req-listing?id=${listingID}`);
}

function rejectListingReq(listingID) {
	return makeAPICall(`/api/internal/reject-listing-req?id=${listingID}`);
}

function fulfillRequestFor(listingID) {
	return makeAPICall(`/api/internal/fulfill-req?id=${listingID}`);
}

async function getImpact() {
	const resp = await fetch("/api/external/get-impact");

	return await resp.json();
}


const LISTINGS_PER_PAGE = 10;