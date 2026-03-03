function install_request(){
    const sql_driver = $('#sql_driver').val();
    const db_data = {
        app_port: $('#app_port').val(),
        sql_driver: sql_driver,
        sql_db: $('#sql_db').val(),
        front_enable: $('#front_enable').prop('checked'),
        sql_host: $('#sql_host').val() || null,
        sql_port: $('#sql_port').val() || null,
        sql_user: $('#sql_user').val() || null,
        sql_password: $('#sql_password').val() || null,
        db_path: $('#db_path').val() || null
    };
    const commonFields = db_data.app_port && db_data.sql_db && db_data.sql_driver;
    const isSqlite = sql_driver === "sqlite";
    const isValid = isSqlite 
        ? commonFields && db_data.db_path 
        : commonFields && db_data.sql_host && db_data.sql_port && db_data.sql_user;

    if (!isValid) {
        return create_flash("warning", "Не все поля заполнены");
    }
    $.ajax({
        url:'/install',
        method:'POST',
        contentType: "application/json",
        data:JSON.stringify(db_data),
        success : function(res) {
            create_flash(res.category, res.message);
            setTimeout(() => location.reload(), 5000);
        },
        error: (err) => {
            console.error(err);
            create_flash("warning", "Ошибка: " + err.statusText);
        }
    })
}