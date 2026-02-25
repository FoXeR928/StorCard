function get_configs(){
    $.ajax({
        url:'/configs/app/get',
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
                    }else if (config.input_format=="generate"){
                        input_element="<input type='text' readonly class='input_value  -separete_main -input_separete' id='"+config.name+"' value="+config.value+"></input>"
                    }else{
                        input_element="<input type="+config.input_format+" class='input_value  -separete_main -input_separete' id='"+config.name+"' value="+config.value+"></input>"
                    }
                    $("#table_block").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element_configs">'+config.name+'</td><td class="table_element -table_body_element -hide-th">'+config.about+'</td><td class="table_element -table_body_element -separete_block">'+input_element+'</td><td><button class="button_save -separete_second -button_separete" onclick="'+command+'">Изменить</button></td></tr>')
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
            },
            data:JSON.stringify({"name":config,"value":get_config}),
            statusCode:{
                401:function(){
                    create_flash("warning","Авторизация не пройдена")
                    window.location.href="/"
                }
            },
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