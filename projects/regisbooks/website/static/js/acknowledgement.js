if (Cookies.get("accepted") === "true") location.href = "/view-profile";

function acknowledge() {
	Cookies.set("accepted", "true", { expires: 365 });

	location.href = "/view-profile";
}