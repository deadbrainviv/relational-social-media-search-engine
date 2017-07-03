$(document).ready(function(){
	// JQuery code to be added here.

	
	//Selects the input checkboxes that are checked and gets the ID values.
	$("#submit_selections").click(function(){
		
		var selected = [];
		$('.check_class').each(function(index){
			if($(this).prop("checked")){
				selected.push($(this).attr('name'));	
			}
		});
		console.log(selected);
		//console.log(windows.entries);

		var select_params = JSON.stringify(selected);
		// Call view of django with the list.
		//$.get('/testApp/merge_update/', { selectedIDs: selected}, function(data){

		
		$.get('/testApp/merge_update/',
			{'selectedIDs[]': select_params}, function(data){
				//var entries = JSON.parse(data)
				$('#selections_list').html(data);	
			});
			});
});




