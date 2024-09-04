namespace RegisSuite.Books;

public class Client
{
	readonly HttpClient httpClient;

	public Client(string apiKey, string serverURL = "https://regisbooks.xyz")
	{
		httpClient = new()
		{
			BaseAddress = new Uri(serverURL)
		};

		httpClient.DefaultRequestHeaders.Add("X-API-Key", apiKey);
	}
}
