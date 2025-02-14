var add_demo_selectors = function(response){
    var arraylength = response.actual_names.length

    // Delete the existing selectors and remove content
    $("#demo_label_col").empty();
    $("#demo_selector_col").empty();


    // Add the required selectors and add the content to them.
    for (var i = 0; i < arraylength; i++){
        var name = response.actual_names[i]
        var display_name = response.display_names[response.actual_names[i]]
        $("#demo_label_col").append("<div class=\"label_stacked\">{}</div>".replace(/{}/g, display_name))
        $("#demo_selector_col").append("<select id=\"{a}\" class=\"select_demo\" name=\"{b}\"></select>".replace(/{a}/g, name).replace(/{b}/g, display_name))
        $.each(response.options[response.actual_names[i]], function(i, obj){
                $('#'+name).append($('<option>').text(obj));
        });
        $('#'+name).val('All')
    }

    // Bind plotting of load to newly created selectors.
    $('.select_demo').on('change', function() {
        $('#dialog').dialog({modal: true});
        plot_filtered_load();
        // Update menu bat status indicator
        status_not_set(['tech', 'net_load_profiles', 'tech_from_gui',
                        'tech_from_file'])
        $('#calc_net_profiles').prop('disabled', true)
        $('#save_tech_sample').prop('disabled', true)
        $('#toggle_tech').prop('disabled', true)
        $.ajax({url: '/deactivate_tech'});
    });

    plot_filtered_load();

}

var get_down_sample_setting = function(){
    var chosen_down_sample_option
    var options = $('.down_sample_option')
    $.each(options, function(i, option){
        if ($(option).is(":checked")){
            chosen_down_sample_option = parseFloat($(option).attr('value'))
        }
    });
    return chosen_down_sample_option
}

var get_missing_data_limit = function(){
    var chosen_missing_data_limit
    var options = $('.missing_data_limit')
    $.each(options, function(i, option){
        if ($(option).is(":checked")){
            chosen_missing_data_limit = parseFloat($(option).attr('value'))
        }
    });
    return chosen_missing_data_limit
}

var get_network_load_setting = function(){
    // Check which network load type is checked in the drop down menu.
    var chosen_network_load
    var options = $('.network_load_option')
    $.each(options, function(i, option){
        if ($(option).is(":checked")){
            chosen_network_load = $(option).attr('value')
        }
    });

    // If the synthetic option is chosen then replace the return value with the name of the chosen synthetic load.
    if (chosen_network_load == 'synthetic'){
         var synthetic_options = $('.synthetic_network_load_option')
        $.each(synthetic_options, function(i, option){
            if ($(option).is(":checked")){
                chosen_network_load = $(option).attr('value')
            }
        });
    }

    console.log(chosen_network_load)
    return chosen_network_load
}

var get_load_details_from_ui = function(){

    var filter_options = {}

    $.each($(".select_demo"), function(i, selector){
        filter_options[$(selector).attr('name')] = $(selector).val();
    });

    var file_name = $('#select').children("option:selected").val();

    var chart_type = $('#select_graph').children("option:selected").val();

    var down_sample_option = get_down_sample_setting();

    var missing_data_limit = get_missing_data_limit();

    var network_load = get_network_load_setting();

    var load_request = {'file_name': file_name, 'filter_options': filter_options, 'chart_type': chart_type,
                        'sample_fraction': down_sample_option, 'missing_data_limit': missing_data_limit,
                        'network_load': network_load};

    return load_request

}

var plot_filtered_load =  function(){
    // Update menu bat status indicator
    $('#load_status_not_set').show()
    $('#load_status_set').hide()

    load_request = get_load_details_from_ui()

    $.ajax({
    url: '/filtered_load_data',
    data: JSON.stringify(load_request),
    contentType: 'application/json;',
    type : 'POST',
    async: 'false',
    dataType:"json",
    success: function(data){
            alert_user_if_error(data)
            plot_load(data);
        }
    });
}

var plot_load = function(response){

    console.log("response:",response);
    console.log("response[layout]:",response['chart_data']['layout']);
    var layout = {autosize: true,
                  margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: response['chart_data']['layout'].showlegend,
                  xaxis: response['chart_data']['layout'].xaxis,
                  yaxis: response['chart_data']['layout'].yaxis};

    Plotly.newPlot('load_chart', response['chart_data']['data'], layout);
    var file_name = $('#select').children("option:selected").val();
    print_n_users(response['n_users'])
    $('#dialog').dialog('close');
    // Update menu bat status indicator
    $('#load_status_not_set').hide()
    $('#load_status_set').show()
}

var print_n_users = function(n_users){
    console.log(n_users)
    var label = document.getElementById('sample_size_info');
    label.innerHTML = 'No. of users: ' + n_users ;
}


var perform_plot_load_actions = function(){
    var file_name = $('#select').children("option:selected").val();
    $.ajax({
        url: '/put_load_profiles_in_memory',
        data: JSON.stringify({'file_name': file_name}),
        contentType: 'application/json',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            alert_user_if_error(data)
            if (file_name != 'Select one'){
                $.getJSON('/get_demo_options/' + file_name, add_demo_selectors);
            } else {
                $("#demo_label_col").empty();
                $("#demo_selector_col").empty();
                $("#load_chart").empty();
                $('#load_status_not_set').show();
                $('#load_status_set').hide();
                $('#dialog').dialog('close');
            }
        }
    });
}

$('#select').on('change', function() {
    $('#dialog').dialog({modal: true});
    perform_plot_load_actions();
    // Update menu bat status indicator
        status_not_set(['tech', 'net_load_profiles', 'tech_from_gui',
                        'tech_from_file'])
    $('#calc_net_profiles').prop('disabled', true)
    $('#save_tech_sample').prop('disabled', true)
    $('#toggle_tech').prop('disabled', true)
    $.ajax({url: '/deactivate_tech'});
});

$('.down_sample_option').on('change', function() {
    $('#dialog').dialog({modal: true});
    perform_plot_load_actions();
    // Update menu bat status indicator
    status_not_set(['tech', 'net_load_profiles', 'tech_from_gui',
                    'tech_from_file'])
    $('#calc_net_profiles').prop('disabled', true)
    $('#save_tech_sample').prop('disabled', true)
    $('#toggle_tech').prop('disabled', true)
    $.ajax({url: '/deactivate_tech'});
});

$('.missing_data_limit').on('change', function() {
    $('#dialog').dialog({modal: true});
    perform_plot_load_actions();
    // Update menu bat status indicator
    status_not_set(['tech', 'net_load_profiles', 'tech_from_gui',
                    'tech_from_file'])
    $('#calc_net_profiles').prop('disabled', true)
    $('#save_tech_sample').prop('disabled', true)
    $('#toggle_tech').prop('disabled', true)
    $.ajax({url: '/deactivate_tech'});
});

$('.network_load_option').on('change', function() {
    $('#dialog').dialog({modal: true});
    perform_plot_load_actions();
    // Update menu bat status indicator
    status_not_set(['tech', 'net_load_profiles', 'tech_from_gui',
                    'tech_from_file'])
    $('#calc_net_profiles').prop('disabled', true)
    $('#save_tech_sample').prop('disabled', true)
    $('#toggle_tech').prop('disabled', true)
    $.ajax({url: '/deactivate_tech'});
});

$('.synthetic_network_load_option').on('change', function() {
    $('#dialog').dialog({modal: true});
    perform_plot_load_actions();
    // Update menu bat status indicator
    status_not_set(['tech', 'net_load_profiles', 'tech_from_gui',
                    'tech_from_file'])
    $('#calc_net_profiles').prop('disabled', true)
    $('#save_tech_sample').prop('disabled', true)
    $('#toggle_tech').prop('disabled', true)
    $.ajax({url: '/deactivate_tech'});
});


$('#select_graph').on('change', function() {
    $('#dialog').dialog({modal: true});
    plot_filtered_load();
});

window.onresize = function() {
    Plotly.Plots.resize('load_chart');
};

