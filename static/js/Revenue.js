(function(Revenue) {

	function Tool(){
		var drawTool = new Draw.Tool();
		this.Init = function(){
			$(window).load(function(){
				drawTool.DrawMonth();
				$('#revenue_type').html('月營收明細');
				$('#table_result').html('&nbsp;').load('/month_revenue/', function () {
					$('#symbol').html($('#stock_id').html());
				});
				$( '#season_revenue' ).click( function() {
					$('#revenue_type').html('季盈餘明細');
					$('#table_result').html('&nbsp;').load('/season_revenue/', function(){
						$('#symbol').html($('#stock_id').html());
					});
					drawTool.DrawSeason();
				});
				$( '#month_revenue' ).click( function() {
					$('#revenue_type').html('月營收明細');
					$('#table_result').html('&nbsp;').load('/month_revenue/', function(){
						$('#symbol').html($('#stock_id').html());
					});
					drawTool.DrawMonth();
				});
			});
		}
	}
	
	Revenue.Tool = Tool;
}(window.Revenue = window.Revenue || {}));