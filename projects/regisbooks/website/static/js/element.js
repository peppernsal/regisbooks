function elem(tag, innerHTML) {
	const elem = document.createElement(tag);

	elem.innerHTML = innerHTML;

	return elem;
}

function textElem(tag, text) {
	const elem = document.createElement(tag);

	elem.textContent = text;

	return elem;
}

function createUserLink(user) {
    const link = textElem('a', `${user.firstName} ${user.lastName}`);
    link.href = `/view-profile?id=${user.id}`;
    link.className = 'user-link';
    return link;
}