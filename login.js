document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const usuario = document.getElementById('usuario').value;
    const pass = document.getElementById('pass').value;
    
    try {
        const response = await fetch('https://gfxjef.pythonanywhere.com/login_app/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ usuario, pass })
        });

        const data = await response.json();
        
        if (data.success) {
            sessionStorage.setItem('userData', JSON.stringify(data.user));
            window.location.href = 'index.html';
        } else {
            document.getElementById('errorMsg').textContent = 'Credenciales incorrectas';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('errorMsg').textContent = 'Error de conexión';
    }
});
