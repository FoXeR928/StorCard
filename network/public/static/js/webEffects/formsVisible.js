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

function open_card_form(){
    $("#hide_card_form").show();
}
function close_card_form(){
    $("#hide_card_form").hide();
}