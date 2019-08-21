var add_case_to_python = function(){
    // Get the name of the selected tariff.
    var case_name = $('#case_name').val();

    // Get the name of the selected tariff.
    var retail_tariff_name = $('#retail_tariff_selection_panel .select_tariff').val();
    var network_tariff_name = $('#network_tariff_selection_panel .select_tariff').val();

    // Get load name
    var load_request = get_load_details_from_ui();

    // Get wholesale price details
    var year = $('#select_wholesale_year').val();
    var state = $('#select_wholesale_state').val();
    wholesale_price_details = {'year': year, 'state': state}

    // Bundle case details into a single object
    var case_details = {'case_name': case_name,
                        'retail_tariff_name': retail_tariff_name,
                        'network_tariff_name': network_tariff_name,
                        'load_details': load_request,
                        'wholesale_price_details': wholesale_price_details};

    $('#case_namer').dialog('close');
    $('#dialog').dialog({modal: true});
    // Get the python app to create the case and calculate results, after this is done create the result plots.
    $.ajax({
        url: '/add_case',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            plot_results();
            reset_case_info(case_name);
            }
    });
}

var delete_case = function(delete_button){
    var case_name = $(delete_button).attr('value')
    var case_name_no_spaces = case_name.replace(/\s/g, '');

    // Delete case controller
    $('#' + case_name_no_spaces).remove();

    // Delete case on python side.
    $.ajax({
        url: '/delete_case',
        data: JSON.stringify(case_name),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json"
    });

    // Re plot charts
    plot_results();

    //update case info tabs
    update_info_tabs_on_case_delete(case_name);

}