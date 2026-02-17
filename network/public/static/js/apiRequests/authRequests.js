function auth(){
    login=$("#login").val();
    password=$("#password").val();
    expires_use=$("expires").prop('checked');
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
                    localStorage.setItem('token', result.access_token);
                    create_flash(flash_status="success",message="Авторизация пройдена")
                    window.location.href="/admin"
                }
            },
            error: function(error){
                console.log(error);
                create_flash(flash_status="warning",message="Авторизация пройдена")
            }
        })
    }else{
        create_flash(flash_status="warning",message="Не все поля заполнены")
    }
}

function get_token() {
    const token = localStorage.getItem('token');
    if (!token){
        window.location.href = "/";
        return null;
    }
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        if (payload.exp < (currentTime - 10)) {
            localStorage.removeItem('token');
            window.location.href = "/";
            create_flash(flash_status="error",message="Срок авторизации истек")
            return null;
        }
        return token;
    } catch (e) {
        localStorage.removeItem('token');
        window.location.href = "/";
        create_flash(flash_status="error",message="Не удалось проверить авторизацию")
        return null;
    }
}

function auth_exit(){
    localStorage.removeItem('token'); 
    window.location.href = "/";
}