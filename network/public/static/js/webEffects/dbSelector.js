function select_driver(){
    select=$("#sql_driver").val()
    if (select=='sqlite'){
        $('.-hide').hide()
        $('.-local').show()
    }else if (select=='postgresql'){
        $('.-hide').hide()
        $('#sql_host').val('localhost')
        $('#sql_port').val(5432)
        $('.-server').show()
    }else if (select=='mysql'){
        $('.-hide').hide()
        $('#sql_host').val('localhost')
        $('#sql_port').val(3306)
        $('.-server').show()
    }
}