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
                    $("#table_block").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element_configs">'+config.name+'</td><td class="table_element -table_body_element -hide-th">'+config.about+'</td><td class="table_element -table_body_element -separete_block">'+input_element+'<button class="button_save -separete_second -button_separete" onclick="'+command+'"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><title>Send SVG Icon</title><path fill="none" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.912 12H4L2.023 4.135A.662.662 0 0 1 2 3.995c-.022-.721.772-1.221 1.46-.891L22 12L3.46 20.896c-.68.327-1.464-.159-1.46-.867a.66.66 0 0 1 .033-.186L3.5 15"/></svg></button></td></tr>')
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