if (Cookies.get("accepted") === "true") location.href = "/dash";

function acknowledge() {
	Cookies.set("accepted", "true", { expires: 365 });

	location.href = "/dash";
}