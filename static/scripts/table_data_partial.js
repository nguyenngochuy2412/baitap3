
function highlight(e) {
    if (selected[0]) selected[0].className = '';
    e.target.parentNode.className = 'selected';
    
}

var table = document.getElementById('dataTable'),
    selected = table.getElementsByClassName('selected');
table.onclick = highlight;

function fnselect(){
var $row=$(this).parent().find('td');
    var clickeedID=$row.eq(0).text();
    // alert(clickeedID);
}

$("#tst").click(function(){
    var value =$(".selected td:first").html();
    value = value || "No row Selected";
    alert(value);
});

function deleteRow() {
    var columnData = [];

    // Lấy tên của cột đầu tiên của bảng
    var firstColumnName = $("#dataTable thead th:first").text(); 

    // Lấy dữ liệu của cột đầu tiên của dòng được chọn
    var firstRowValue = $(".selected td:first").text(); 

    // Thêm tên cột và giá trị vào mảng columnData dưới dạng đối tượng
    columnData.push({
        columnName: firstColumnName,
        value: firstRowValue
    });
    // Gửi dữ liệu qua AJAX
    $.ajax({
        type: "POST",
        url: '/database/'+databaseName+'/table/'+tableName+'/delete',  // Địa chỉ route  Flask
        contentType: "application/json",  // Thiết lập Content-Type là JSON
        data: JSON.stringify(columnData),  // Chuyển đổi formData thành JSON
        success: function(response) {
            // Xử lý khi Flask trả về phản hồi
            console.log(response);
        },
        error: function(xhr, status, error) {
            // Xử lý khi có lỗi
            console.error("Có lỗi xảy ra: " + error);
        }
    });
}

function updateRow() {
    // Tạo một đối tượng để lưu trữ dữ liệu của tất cả các input
    var formData = {};

    // Lặp qua tất cả các trường input trong form và lấy giá trị
    $("#input_form input").each(function() {
        var columnName = $(this).attr('name');  // Lấy tên của input (name)
        var columnValue = $(this).val();  // Lấy giá trị của input
        formData[columnName] = columnValue;  // Thêm vào đối tượng formData
    });

    var columnData = [];
    var firstColumnName = $("#dataTable thead th:first").text(); 
    var firstRowValue = $(".selected td:first").text(); 
    columnData.push({
        columnName: firstColumnName,
        value: firstRowValue
    });

    // Tạo đối tượng dữ liệu tổng hợp
    var dataToSend = {
        formData: formData,
        columnData: columnData
    };
    // Gửi dữ liệu qua AJAX
    $.ajax({
        type: "POST",
        url: '/database/'+databaseName+'/table/'+tableName+'/update',  // Địa chỉ route của Flask
        contentType: "application/json",  // Thiết lập Content-Type là JSON
        data: JSON.stringify(dataToSend),  // Chuyển đổi dataToSend thành JSON
        success: function(response) {
            // Xử lý khi Flask trả về phản hồi
            console.log(response);
        },
        error: function(xhr, status, error) {
            // Xử lý khi có lỗi
            console.error("Có lỗi xảy ra: " + error);
        }
    });
}

function addRow() {
    // Tạo một đối tượng để lưu trữ dữ liệu của tất cả các input
    var formData = {};

    // Lặp qua tất cả các trường input trong form và lấy giá trị
    $("#input_form input").each(function() {
        var columnName = $(this).attr('name');  // Lấy tên của input (name)
        var columnValue = $(this).val();  // Lấy giá trị của input
        formData[columnName] = columnValue;  // Thêm vào đối tượng formData
    });

    // Gửi dữ liệu qua AJAX
    $.ajax({
        type: "POST",
        url: '/database/'+databaseName+'/table/'+tableName+'/submit',  // Địa chỉ route của Flask
        contentType: "application/json",  // Thiết lập Content-Type là JSON
        data: JSON.stringify(formData),  // Chuyển đổi formData thành JSON
        success: function(response) {
            // Xử lý khi Flask trả về phản hồi
            console.log(response);
        },
        error: function(xhr, status, error) {
            // Xử lý khi có lỗi
            console.error("Có lỗi xảy ra: " + error);
        }
    });
}

function reLoadTable() {
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

function executeQuery() {
    const sqlQuery = document.getElementById("sql-query").value;

    $.ajax({
        url: '/database/' + databaseName + '/execute_query',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({query: sqlQuery}),
        success: function(response) {
            if (response.success) {
                if (response.result) {
                    document.getElementById("query-result").innerHTML = response.result;
                } else {
                    alert(response.message);  // Hiển thị thông báo thành công nếu không có dòng trả về
                }
            } else {
                alert("Error: " + response.error);
            }
        },
        error: function(error) {
            console.error("Error:", error);
        }
    });
}