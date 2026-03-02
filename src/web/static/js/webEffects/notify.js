function create_flash(status,message){
    const $flash = $(`<div class='flash ${status}'>${message}</div>`);
   $("#main").prepend($flash);
    setTimeout(() => $flash.fadeOut(() => $flash.remove()), 4000);
}