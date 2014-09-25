(function(UpdateData) {
	function Update (){
		this.Init = function() {
			$(window).load(function() {
				$("#update_stockid").click(function(){
					//var data = GetData('/update_stockid/');
					$.get('/update_stockid/', function(jData){
						$('#stockid_lastUpdateDate').html(jData.list_of_json.lastUpdateDate);
						$('#stockid_lastDataDate').html(jData.list_of_json.lastDataDate);
						$('#stockid_notes').html(jData.list_of_json.notes);
					});
				});
			});
		}
	}
	UpdateData.Update = Update;
}(window.UpdateData = window.UpdateData||{}));

