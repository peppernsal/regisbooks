ID = str
UserID = ID
BookID = ID
ListingID = ID

class User:
	id: UserID
	listings: list[ListingID]
	name: str

class Book:
	id: BookID
	listings: list[ListingID]
	isbn: str
	title: str
	author: str


class Listing:
	id: ListingID
	creator: UserID
	requester: UserID | None
	book: BookID