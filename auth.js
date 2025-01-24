document.addEventListener('DOMContentLoaded', () => {
    const userData = sessionStorage.getItem('userData');
    if (!userData) {
        window.location.href = 'login.html';
    } else {
        const user = JSON.parse(userData);
        const userDisplay = document.getElementById('user-display');
        const logoutBtn = document.getElementById('logoutBtn');
        
        if (userDisplay) {
            userDisplay.textContent = `${user.nombre}`;
        }
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                sessionStorage.clear();
                window.location.href = 'login.html';
            });
        }
    }
});
