if (Cookies.get("accepted") === "true") location.href = "/goto-auth";

function acknowledge() {
	Cookies.set("accepted", "true", { expires: 365 });

	location.href = "/goto-auth";
}