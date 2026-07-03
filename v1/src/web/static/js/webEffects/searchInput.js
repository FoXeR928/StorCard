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