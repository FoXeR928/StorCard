const DRIVER_DEFAULTS = {
    postgresql: { host: 'localhost', port: 5432 },
    mysql: { host: 'localhost', port: 3306 }
};

function select_driver(){
    const driver = $("#sql_driver").val();
    const config = DRIVER_DEFAULTS[driver];
     $('.-hide').hide();
    if (driver === 'sqlite') {
        $('.-local').show();
    } else if (config) {
        $('#sql_host').val(config.host);
        $('#sql_port').val(config.port);
        $('.-server').show();
    }
}