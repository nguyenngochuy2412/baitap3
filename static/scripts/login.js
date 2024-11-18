

function submitLogin() {
    const formData = {
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
        host: document.getElementById("host").value || "localhost", // Giá trị mặc định  localhost
        port: document.getElementById("port").value || 5432 // Giá trị mặc định  5432
    };

    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Đăng nhập thất bại!");
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        if (data.message === "Kết nối thành công!") {
            // Chuyển hướng đến trang chính nếu đăng nhập thành công
            window.location.href = "/";
        }
    })
    .catch(error => console.error("Error:", error));
}

// Đăng xuất
function logout() {
    fetch('/logout', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.redirect_url) {
            window.location.href = data.redirect_url;  // Điều hướng đến trang đăng nhập
        }
    })
    .catch(error => console.error("Error:", error));
}