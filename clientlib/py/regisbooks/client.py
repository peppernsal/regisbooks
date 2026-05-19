from typing import TypeVar
from .structures import (
	User, UserID,
	Listing, ListingID,
	Book, BookID
)

import httpx

T = TypeVar('T')

class Client:
	def __init__(self, api_key: str, server_url: str="https://regisbooks.xyz"):
		self.api_key = api_key
		self.client = httpx.Client(
			base_url=server_url,
			headers={ "X-API-Key": api_key }
		)

	def _get(self, endpoint: str):
		return self.client.get(endpoint)

	def _get_json(self, endpoint: str) -> dict:
		return self._get(endpoint).json()

	def _post(self, endpoint: str, data: dict):
		return self.client.post(endpoint, json=data)

	@staticmethod
	def _conform(urldata: dict, dtype: type[T]) -> T:
		obj = dtype()

		obj.__dict__ = urldata

		return obj

	def get_user(self, id: UserID) -> User:
		return self._conform(
			self._get_json(f"/api/get-user?id={id}"), User
		)

	def get_book(self, id: BookID) -> Book:
		return self._conform(
			self._get_json(f"/api/get-book?id={id}"), Book
		)

	def get_listing(self, id: ListingID) -> Listing:
		return self._conform(
			self._get_json(f"/api/get-listing?id={id}"), Listing
		)