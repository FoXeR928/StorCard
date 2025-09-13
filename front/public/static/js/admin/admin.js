  window.addEventListener('load', function() {
    
    get_users()
    get_configs()
})

function get_cards(){
    $.ajax({
        url:'/carts/get',
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
                $.each(result.users, function(index,user){
                    $("#table_block_cards").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element search_element_users">'+user.login+'</td><td class="table_element -table_body_element">'+user.user_name+'</td><td class="table_element -table_body_element">'+role+'</td><td class="table_element_button -table_body_element"><button onclick="'+command+'" class="update_button -button">Изменить</button></td></tr>')
                })
            }
        },
        error: function(error){
            console.log(error);
            window.location.href="/"
        }
    })
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
            window.location.href="/"
        }
    })
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
                $.each(result.users, function(index,user){
                    command="open_form_update('"+user.login+"')"
                    role="Пользователь"
                    if(user.isAdmin==true){
                        role="Администратор"
                    }
                    $("#table_block_users").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element search_element_users">'+user.login+'</td><td class="table_element -table_body_element">'+user.user_name+'</td><td class="table_element -table_body_element">'+role+'</td><td class="table_element_button -table_body_element"><button onclick="'+command+'" class="update_button -button">Изменить</button></td></tr>')
                })
            }
        },
        error: function(error){
            console.log(error);
            window.location.href="/"
        }
    })
}