  window.addEventListener('load', function() {
    get_cards()
    get_users()
    get_configs()
})

function get_cards(){
    $.ajax({
        url:'/cards/get',
        method:'GET',
        headers:{
            "Content-Type":"application/json",
            "Authorization": "Bearer "+get_token()
        },
        success : function(result) {
            if (result["result"]==false){
                create_flash(result["category"],result["message"])
            }else{
                $("#table_block_cards").empty()
                $.each(result.cards, function(index,card){
                    command="open_form_update_card('"+card.id+"')"
                    $("#table_block_cards").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element">'+card.name+'</td><td class="table_element -table_body_element search_element_cards">'+card.own_login+'</td><td class="table_element_button -table_body_element"><button onclick="'+command+'" class="update_button -button">Изменить</button></td></tr>')
                })
            }
        },
        error: function(error){
            console.log(error);
            create_flash("error","Список карт не получен")
        }
    })
}

function update_card(){
    card_id=$("#update_card").val()
    login=$("#update_card_own").val()
    if (login!=""){

    }
}

function get_configs(){
    $.ajax({
        url:'/configs/app/get',
        method:'GET',
        headers:{
            "Content-Type":"application/json",
            "Authorization": "Bearer "+get_token()
        },
        success : function(result) {
            if (result["result"]==false){
                create_flash(result["category"],result["message"])
            }else{
                $("#table_block").empty()
                $.each(result.configs_ai, function(index,config){
                    command="update_config('"+config.name+"','"+config.input_format+"')"
                    if (config.input_format=="textarea"){
                        input_element="<textarea class='textarea_value  -separete_main -input_separete' id='"+config.name+"'>"+config.value+"</textarea>"
                    }else if (config.input_format=="boolen"){
                        var checked_element=""
                        if (config.value==1){
                            checked_element="checked"
                        }
                        input_element="<input type='checkbox' class='input_value  -separete_main -input_separete' id='"+config.name+"' "+checked_element+"></input>"
                    }else{
                        input_element="<input type="+config.input_format+" class='input_value  -separete_main -input_separete' id='"+config.name+"' value="+config.value+"></input>"
                    }
                    $("#table_block").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element_configs">'+config.name+'</td><td class="table_element -table_body_element">'+config.about+'</td><td class="table_element -table_body_element -separete_block">'+input_element+'<button class="button_save -separete_second -button_separete" onclick="'+command+'">\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c</button></td></tr>')
                })
            }
        },
        error: function(error){
            console.log(error);
            create_flash("error","Список конфигов не получен")
        }
    })
}

function update_config(config,format){
    get_config=$("#"+config).val()
    if (format=="boolen"){
        get_config=$("#"+config).prop("checked")
    }
    if (get_config!=""){
        $.ajax({
            url:'/configs/update',
            method:'PATCH',
            headers:{
                "Content-Type":"application/json",
                "Authorization": "Bearer "+get_token()
            },
            data:JSON.stringify({"name":config,"value":get_config}),
            success : function(result) {
                create_flash(result["category"],result["message"])
                get_configs()
            },
            error: function(error){
                alert('Ошибка '+error)
                console.log(error);
            }
        })
    }
}

function get_users(){
    $.ajax({
        url:'/users/get',
        method:'GET',
        headers:{
            "Content-Type":"application/json",
            "Authorization": "Bearer "+get_token()
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
                    $("#table_block_users").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element search_element_users">'+user.login+'</td><td class="table_element -table_body_element">'+user.user_name+'</td><td class="table_element -table_body_element">'+role+'</td><td class="table_element_button -table_body_element"><button onclick="'+command+'" class="update_button -button">Изменить</button></td></tr>')
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
                "Authorization": "Bearer "+get_token()
            },
            data:JSON.stringify(data_user),
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

function password_check(form){
    password=$('#'+form+'password').val();
    password_checked=$('#'+form+'password_check').val();
    if ((password=='') || (password.length>=8)){
        $('#'+form+'password').removeAttr('style')
    }else{
        $('#'+form+'password').css('border','1px solid red');
    }
    if ((password==password_checked)){
        $('#'+form+'password_check').removeAttr('style')
    }else{
        $('#'+form+'password_check').css('border','1px solid red');
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
                "Authorization": "Bearer "+get_token()
            },
            data:JSON.stringify(data_user),
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
                "Authorization": "Bearer "+get_token()
            },
            data:JSON.stringify(data_user),
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

function open_form_update_card(card){
    $("#update_card").val(card)
    $("#hide_form_update_card").show();
}
function close_form_update_card(){
    $("#update_card").val("")
    $("#hide_form_update_card").hide();
}

function open_form_update(user){
    $("#update_login").val(user)
    $("#hide_form_update").show();
}
function close_form_update(){
    $("#update_login").val("")
    $("#update_user_role").val("")
    $("#update_password").val("")
    $("#update_password_check").val("")
    $("#hide_form_update").hide();
}

function open_form(){
    $("#hide_form").show();
}
function close_form(){
    $("#hide_form").hide();
}