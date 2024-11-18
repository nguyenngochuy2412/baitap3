
function loadTables(databaseName) {
    // Lấy danh sách bảng cho database
    $.ajax({
        url: '/get_tables/' + databaseName,
        method: 'GET',
        success: function(tables) {
            let tablesList = $('#tables-' + databaseName);
            tablesList.empty();
            tablesList.show();
            tables.forEach(function(table) {
                tablesList.append('<li><a href="javascript:void(0);" onclick="loadTableData(\'' + databaseName + '\', \'' + table + '\')">' + table + '</a></li>');
                tablesList.append('<button class="toggle-btn" type="button"><i class="fa-solid fa-ellipsis small-icon" style="font-size: 20px;"></i></button>');
            });
        },
        error: function(error) {
            console.log("Lỗi khi lấy danh sách bảng:", error);
        }
    });
}

function loadTableData(databaseName, tableName) {
    // Lấy dữ liệu bảng cho database và table
    $.ajax({
        url: '/database/' + databaseName + '/table/' + tableName,
        method: 'GET',
        success: function(response) {
            $('#database-content').html(response);  // Hiển thị dữ liệu bảng trong <div id="database-content">
        },
        error: function(error) {
            console.log("Lỗi khi lấy dữ liệu bảng:", error);
        }
    });
}

function toggleMenu(databaseName) {
    var menu = document.getElementById('dropdown-menu-' + databaseName);
    
    // Kiểm tra xem menu có đang hiển thị không
    if (menu.style.display === 'none' || menu.style.display === '') {
        menu.style.display = 'block';  // Hiển thị menu
    } else {
        menu.style.display = 'none';  // Ẩn menu
    }
}








