function toggleSidebar() {
	const sidebar = document.querySelector('.sidebar');
	const content = document.querySelector('.content');

	if (sidebar.classList.contains('collapsed')) {
		sidebar.classList.remove('collapsed');
		content.classList.remove('centered');
		localStorage.setItem('sidebarState', 'expanded');


	} else {
		sidebar.classList.add('collapsed');
		content.classList.add('centered');
		localStorage.setItem('sidebarState', 'collapsed');
	}
}

const sidebar = document.querySelector('.sidebar');
const content = document.querySelector('.content');
const savedState = localStorage.getItem('sidebarState');

if (savedState === 'collapsed') {
	sidebar.classList.add('collapsed');
	content.classList.add('centered');
} else {
	sidebar.classList.remove('collapsed');
	content.classList.remove('centered');
}

document.getElementsByClassName("sidebar-toggle")[0].addEventListener("click", toggleSidebar);