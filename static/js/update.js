(function(UpdateData) {
	function Update (){
		this.Init = function() {
			$(window).load(function() {
				$("#update_stockid").click(function(){
					//var data = GetData('/update_stockid/');
					$.get('/update_stockid/', function(jData){
						$('#stockid_lastUpdateDate').html(jData.lastUpdateDate);
						$('#stockid_lastDataDate').html(jData.lastDataDate);
						$('#stockid_notes').html(jData.notes);
					});
				});

				$("#month_revenue").click(function() {
					$.get('/update_month_revenue/', function(jData) {
						$('#monthrevenue_lastUpdateDate').html(jData.lastUpdateDate);
						$('#monthrevenue_lastDataDate').html(jData.lastDataDate);
						$('#monthrevenue_notes').html(jData.notes);
					})
				});
			});
		}
	}
	UpdateData.Update = Update;
}(window.UpdateData = window.UpdateData||{}));

