
var alert_user_if_error = function(data){
    if ('error' in data){
        $('#error_dialog').dialog({modal: true, width: 400, height: 200})
        $('#error_dialog p').text(data['error'])
    }
}