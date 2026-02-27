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