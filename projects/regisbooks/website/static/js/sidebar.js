function toggleSidebar() {
	const sidebar = document.querySelector('.sidebar');

	if (sidebar.classList.contains('collapsed')) {
		sidebar.classList.remove('collapsed');
		localStorage.setItem('sidebarState', 'expanded');
		
		
	} else {
		sidebar.classList.add('collapsed');
		localStorage.setItem('sidebarState', 'collapsed');
	}
}

document.addEventListener('DOMContentLoaded', () => {
	const sidebar = document.querySelector('.sidebar');
	const savedState = localStorage.getItem('sidebarState');

	if (savedState === 'collapsed') {
		sidebar.classList.add('collapsed');
	} else {
		sidebar.classList.remove('collapsed');
	}
});