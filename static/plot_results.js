
var get_default_case_name = function(){
    // Get a un used case name to put as the default name in the case namer dialog box.
    $.ajax({
        url: '/get_case_default_name',
        contentType: 'application/json;charset=UTF-8',
        async: 'false',
        dataType:"json",
        success: function(data){launch_case_namer(data)}
    });
}


var launch_case_namer = function(default_name){
    $('#case_name').val(default_name)
    $( "#case_namer" ).dialog({
        modal: true,
        buttons: {"Save case": add_case_to_gui}
    });
}

var add_case_to_gui = function(){
    // Get case name
    case_name = $('#case_name').val();
    case_name_no_spaces = case_name.replace(/\s/g, '');

    // Get a copy of the case control template.
    var $new_case_control = $('#case_control_template').clone();
    // Set the id of the copy equal to the case name.
    $new_case_control.attr('id', case_name_no_spaces);
    // Insert the copy into the case panel
    $new_case_control.insertAfter($('#case_list').children().last())
    // Make the case control visible
    $new_case_control.css("display", "block");
    // Set the value of the checkbox in the case_control
    $('#' + case_name_no_spaces + ' ' + '.case_visibility_checkbox').attr('value', case_name);
    $('#' + case_name_no_spaces + ' ' + '.case_delete_button').attr('value', case_name);
    $('#' + case_name_no_spaces + ' ' + '.case_info_button').attr('value', case_name);
    // Set label in case control equal to case name.
    $('#' + case_name_no_spaces + ' ' + '.case_label').html(case_name)
    // Add the case to the python side.
    add_case();
    //Update the select for the single case results.
    update_single_case_selector();
}

var update_single_case_selector = function(){
    var cases = get_cases_to_plot_from_ui();
    $('#single_case_result_chosen_case').empty();
    $.each(cases, function (i, case_name) {
        $('#single_case_result_chosen_case').append($('<option>', {
            value: case_name,
            text : case_name
        }));
    });
}


var get_cases_to_plot_from_ui = function(){
  case_controls = $("#case_list .case_visibility_checkbox");
  cases_to_plot = []
  $.each(case_controls, function(index, checkbox){
    if (checkbox.checked == true){
       cases_to_plot.push(checkbox.value)
    }
  })
  return cases_to_plot
}


var on_checkbox_change = function(){
  update_single_case_selector();
  plot_results();
}

var get_active_network_component = function(){
    var component
    var tablinks = $("#network_tariff_selection_panel .tablinks");
    $.each(tablinks, function(index, link){
        if ($(link).hasClass('active')){
          component = link.value
        }
        return component
    });
    return component
}

var plot_results = function(){
    // Plot results for each results tab.
    plot_single_variable_results();
    plot_dual_variable_results();
    plot_single_case_results();
    $('#dialog').dialog('close');
    // Always show single variable graph by default.
    document.getElementById('results_panel_button').click();
}

var plot_single_variable_results = function(){
    // Get cases to plot
    cases_to_plot = get_cases_to_plot_from_ui();

    // Get the chart type to be drawn from the GUI.
    var chart_type = $('#single_variable_chart_type').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'chart_name': chart_type, 'case_names': cases_to_plot}

    // Define the chart layout
    var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};

    // Get chart data
    $.ajax({
        url: '/get_single_variable_chart',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            // Draw chart.
            Plotly.newPlot('single_variable_result_chart', data, layout, {responsive: true});
        ;}
    });

}


var plot_dual_variable_results = function(){
    // Get cases to plot
    cases_to_plot = get_cases_to_plot_from_ui();

    // Get the x and y axis for the dual variable chart.
    var x_axis = $('#dual_variable_x_axis').children("option:selected").val();
    var y_axis = $('#dual_variable_y_axis').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'x_axis': x_axis, 'y_axis': y_axis, 'case_names': cases_to_plot}

    // Define the chart layout
    var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};

    // Get chart data
    $.ajax({
        url: '/get_dual_variable_chart',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            // Draw chart.
            Plotly.newPlot('dual_variable_result_chart', data, layout, {responsive: true});
        ;}
    });

}


var plot_single_case_results = function(){
    // Get the name of the case to plot.
    var case_name = $('#single_case_result_chosen_case').children("option:selected").val();

    // Get the x and y axis for the dual variable chart.
    var case_to_plot = $('#single_case_result_chosen_case').children("option:selected").val();
    var chart_type = $('#single_case_chart_type').children("option:selected").val();

    // Package request details into a single object.
    var case_details = {'chart_name': chart_type, 'case_name': case_name}

    // Define the chart layout
    var layout = {margin: { l: 40, r: 35, b: 40, t: 20, pad: 0 },
                  paper_bgcolor: '#EEEEEE',
                  plot_bgcolor: '#c7c7c7',
                  showlegend: true};

    // Get chart data
    $.ajax({
        url: '/get_single_case_chart',
        data: JSON.stringify(case_details),
        contentType: 'application/json;charset=UTF-8',
        type : 'POST',
        async: 'false',
        dataType:"json",
        success: function(data){
            // Draw chart.
            Plotly.newPlot('single_case_result_chart', data, layout, {responsive: true});
        ;}
    });
}