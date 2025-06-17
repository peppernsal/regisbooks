// authInfo should be defined prior to loading this library

const USAGE_NEW = 0;
const USAGE_LIGHT = 1;
const USAGE_USED = 2;


const STATUS_AVAILABLE = 0;
const STATUS_REQUESTED = 1;
const STATUS_GIVEN = 2;

const listingUsageRepr = ["New", "Lightly Used", "Used"];
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
	if (!userID) return await getJSONInfoFromAPICall(`/api/internal/get-user?id=${await getAuthInfo().userId}`);

	return await getJSONInfoFromAPICall(`/api/internal/get-user?id=${userID}`);
}

async function getAllUsers() {
	return await getJSONInfoFromAPICall(`/api/internal/get-users`);
}


function getListingInfo(listingID) {
	return getJSONInfoFromAPICall(`/api/internal/get-listing?id=${listingID}`);
}

function getBookInfo(bookID) {
	return getJSONInfoFromAPICall(`/api/internal/get-book?id=${bookID}`);
}

function getBooks() {
	return getJSONInfoFromAPICall(`/api/internal/get-books`);
}

function getListings(options) {
	if (options) {
		return getJSONInfoFromAPICall(`/api/internal/get-listings`, JSON.stringify(options), "POST", {
			"Content-Type": "application/json"
		});
	}

	return getJSONInfoFromAPICall(`/api/internal/get-listings`);
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

const AURA_PER_LISTING = 1;
const AURA_PER_BOOK_GIVEN = 3;
const LISTINGS_PER_PAGE = 10;

function getAura(userInfo) {
	return userInfo.stats.listingsMade*AURA_PER_LISTING + userInfo.stats.booksGiven*AURA_PER_BOOK_GIVEN;
}