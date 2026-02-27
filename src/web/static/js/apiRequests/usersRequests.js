function get_users(){
    $.ajax({
        url:'/users/get',
        method:'GET',
        headers:{
            "Content-Type":"application/json",
        },
        statusCode:{
            401:function(){
                create_flash("warning","Авторизация не пройдена")
                window.location.href="/"
            }
        },
        success : function(result) {
            if (result["result"]==false){
                create_flash(result["category"],result["message"])
            }else{
                $("#table_block_users").empty()
                $("#update_card_own").empty()
                $("#update_card_own").append('<option value="" selected disabled hidden>Выбрать пользователя</option>')
                $.each(result.users, function(index,user){
                    command="open_form_update('"+user.login+"')"
                    role="Пользователь"
                    if(user.isAdmin==true){
                        role="Администратор"
                    }
                    $("#update_card_own").append('<option value="'+user.login+'">'+user.user_name+'</option>')
                    $("#table_block_users").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element search_element_users -td_user_login">'+user.login+'</td><td class="table_element -table_body_element -td_user_name">'+user.user_name+'</td><td class="table_element -table_body_element">'+role+'</td><td class="table_element_button -table_body_element"><button onclick="'+command+'" class="update_button -button">Изменить</button></td></tr>')
                })
            }
        },
        error: function(error){
            console.log(error);
            create_flash("error","Список пользователей не получен")
        }
    })
}

function create_user(){
    login=$("#registration_login").val()
    user_name=$("#registration_user_name").val()
    password=$("#registration_password").val()
    password_checked=$("#registration_password_check").val()
    data_user={"login":login,"user_name":user_name,"password":password}
    if (login!="" && password!="" && password.length>=8 && password==password_checked){
        $.ajax({
            url:'/users/registration',
            method:'POST',
            headers:{
                "Content-Type":"application/json",
            },
            data:JSON.stringify(data_user),
            statusCode:{
                401:function(){
                    create_flash("warning","Авторизация не пройдена")
                    window.location.href="/"
                }
            },
            success : function(result) {
                create_flash(result["category"],result["message"])
                get_users()
                close_form()
            },
            error: function(error){
                console.log(error);
                create_flash("error","Ошибка создания пользователя")
            }
        })
        $("#registration_login").val("")
        $("#registration_user_name").val("")
        $("#registration_password").val("")
        $("#registration_password_check").val("")
    }
}

function update_user(){
    login=$("#update_login").val()
    user_role=$("#update_user_role").val()
    password=$("#update_password").val()
    password_checked=$("#update_password_check").val()
    if (login!="" && password!="" && password.length>=8 && password==password_checked){
        data_user={"login":login,"password":password}
        $.ajax({
            url:'/users/change/password',
            method:'PATCH',
            headers:{
                "Content-Type":"application/json",
            },
            data:JSON.stringify(data_user),
            statusCode:{
                401:function(){
                    create_flash("warning","Авторизация не пройдена")
                    window.location.href="/"
                }
            },
            success : function(result) {
                create_flash(result["category"],result["message"])
                close_form_update()
            },
            error: function(error){
                console.log(error);
                window.location.href="/"
            }
        })
        $("#update_login").val("")
        $("#update_password").val("")
        $("#update_password_check").val("")
    }
    if (user_role!=null){
        if (user_role==1){
            user_role_add=true
        }else{
            user_role_add=false
        }
        data_user={"login":login,"isAdmin":user_role_add}
        $.ajax({
            url:'/users/change/role',
            method:'PATCH',
            headers:{
                "Content-Type":"application/json",
            },
            data:JSON.stringify(data_user),
            statusCode:{
                401:function(){
                    create_flash("warning","Авторизация не пройдена")
                    window.location.href="/"
                }
            },
            success : function(result) {
                create_flash(result["category"],result["message"])
                close_form_update()
            },
            error: function(error){
                console.log(error);
                window.location.href="/"
            }
        })
    }
}

function remove_user(){
    
}