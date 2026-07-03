function auth(){
    login=$("#login").val();
    password=$("#password").val();
    expires_use=$("#expires").prop('checked');
    send_data={
        "username":login,
        "password":password,
        "expires_use":expires_use
    }
    if (login!="" && password!=""){
        $.ajax({
            url:'/auth/login',
            method:'POST',
            headers:{
                "Content-Type":"application/x-www-form-urlencoded"
            },
            data:send_data,
            success : function(result) {
                if (result["result"]==false){
                    create_flash(flash_status=result["categoty"],message=result["message"])
                }else{
                    create_flash(flash_status="success",message="Авторизация пройдена")
                    window.location.href="/admin"
                }
            },
            error: function(error){
                console.log(error);
                create_flash(flash_status="warning",message="Авторизация не пройдена из-за ошибки")
            }
        })
    }else{
        create_flash(flash_status="warning",message="Не все поля заполнены")
    }
}
function auth_exit(){ 
    $.ajax({
        url:'/auth/logout',
        method:'POST',
        headers:{
            "Content-Type":"application/x-www-form-urlencoded"
        },
        success : function(result) {
            create_flash(flash_status="success",message="Деавторизация пройдена")
            window.location.href="/"
        },
        error: function(error){
            console.log(error);
            create_flash(flash_status="warning",message="Деавторизация не удалась")
        }
    })
}