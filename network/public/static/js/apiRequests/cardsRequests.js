function get_cards(){
    $.ajax({
        url:'/cards/get',
        method:'GET',
        headers:{
            "Content-Type":"application/json",
        },
        success : function(result) {
            if (result["result"]==false){
                create_flash(result["category"],result["message"])
            }else{
                $("#table_block_cards").empty()
                $.each(result.cards, function(index,card){
                    command="open_form_update_card('"+card.id+"')"
                    $("#table_block_cards").append('<tr class="table_body_element_block"><td class="table_element -table_body_element search_element -td_card">'+card.name+'</td><td class="table_element -table_body_element search_element_cards -td_card_own">'+card.own_login+'</td><td class="table_element_button -table_body_element"><button onclick="'+command+'" class="update_button -button">Изменить</button></td></tr>')
                })
            }
        },
        error: function(error){
            console.log(error);
            create_flash("error","Список карт не получен")
        }
    })
}

function create_card(){
    card_name=$("#card_name").val()
    card_about=$("#card_about").val()
    card_coder=$("#code_format").val()
    card_code=$("#code").val()
    if (card_name!=="" && card_coder!=="" && card_code!==""){
        data_card={"name":card_name,"about":card_about,"code":card_code,"code_type":card_coder}
        $.ajax({
        url:'/cards/add',
        method:'POST',
        headers:{
            "Content-Type":"application/json",
        },
        data:JSON.stringify(data_card),
        success : function(result) {
            create_flash(result["category"],result["message"])
        },
        error: function(error){
            console.log(error);
            create_flash("error","Не удалось отправить запрс на создание карты")
        }
    })
    }else{
        create_flash("warning","Информация о карте не указана")
    }
}

function update_card(){
    card_id=$("#update_card").val()
    login=$("#update_card_own").val()
    if (login!=""){

    }
}