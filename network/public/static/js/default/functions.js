function create_flash(flash_status,message){
    $("#main").prepend("<div class='flash "+flash_status+"'>"+message+"</div>")
    setTimeout(function(){
        $('.flash').remove();
    }, 4000);
}

function get_token(){
    var token_get = document.cookie.match(/token=(.+?)(;|$)/);
    if (token_get==null){
        token=null
    }else{
        token=token_get[1]
    }
    return token
}

function search_on_page(table){
    search=$("#search"+table).val();
    $('.search_element'+table).each(function(){
        if (($(this).text()).includes(search)!=true){
            $(this).parent().hide();
        }
    })
    if(search==''){
        $('.search_element'+table).parent().show()
    }
}

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
                    document.cookie="token="+result["access_token"]
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