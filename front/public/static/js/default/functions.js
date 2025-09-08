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