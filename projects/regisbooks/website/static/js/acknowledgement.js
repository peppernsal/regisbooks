if (Cookies.get("accepted") === "true") location.href = "https://auth.regisbooks.org";
function acknowledge() {
	Cookies.set("accepted", "true", { expires: 365 });

	location.href = "https://auth.regisbooks.org";
}