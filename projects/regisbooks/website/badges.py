from dataclasses import dataclass
from typing import Callable, TypeVar

User = TypeVar("User")
Listing = TypeVar("Listing")
Book = TypeVar("Book")

@dataclass
class BadgeInfo:
	name: str
	description: str
	achieved: Callable[[User, type[Listing], type[Book]], bool]

	@property
	def as_dict(self):
		return {
			"name": self.name,
			"description": self.description,
			"imageURL": f"/static/images/badges/{self.name.lower().replace(' ', '_')}.png"
		}

badges: list[BadgeInfo] = [
	BadgeInfo(
		"Contributor",
		"Created at least one listing",
		lambda user, Listing, Book: user.stats.listings_made > 0
	),
	BadgeInfo(
		"Book Baron",
		"Posted at least ten listings",
		lambda user, Listing, Book: user.stats.listings_made >= 10
	),
	BadgeInfo(
		"Donor",
		"Gave away at least one book",
		lambda user, Listing, Book: user.stats.books_given > 0
	),
	BadgeInfo(
		"Philanthropist",
		"Gave away at least five books",
		lambda user, Listing, Book: user.stats.books_given >= 5
	),
	BadgeInfo(
		"Book Benefactor",
		"Gave away at least ten books",
		lambda user, Listing, Book: user.stats.books_given >= 10
	),
	BadgeInfo(
		"Collector",
		"Received at least one book",
		lambda user, Listing, Book: user.stats.books_received > 0
	),
	BadgeInfo(
		"It Comes Back Around",
		"Receive and give away at least one book",
		lambda user, Listing, Book: user.stats.books_received > 0 and user.stats.books_given > 0
	),
	BadgeInfo(
		"Loyal Member",
		"Gain at least 10 Aura",
		lambda user, Listing, Book: user.aura >= 10
	),
	BadgeInfo(
		"Aura Farmer",
		"Gain at least 25 Aura",
		lambda user, Listing, Book: user.aura >= 25
	),
	BadgeInfo(
		"Omnipresent",
		"List a book with three or more pickup locations",
		lambda user, Listing, Book: any(
			True for listing in user.listings if len(listing.pickup_locations) >= 3
		)
	),
	BadgeInfo(
		"Stacking",
		"List a book that at least two other listings already posted",
		lambda user, Listing, Book: any(
			True for listing in user.listings if len(listing.book.listings) >= 3
		)
	)
]

def get(name: str) -> BadgeInfo:
	for badge in badges:
		if badge.name.lower() == name.lower():
			return badge

	return None