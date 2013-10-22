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
					if ($('#revenue_type').html() != '季盈餘明細') {
						$('#revenue_type').html('季盈餘明細');
						$('#table_result').html('&nbsp;').load('/season_revenue/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.DrawSeason();
					}
				});
				$( '#month_revenue' ).click( function() {
					if ($('#revenue_type').html() != '月營收明細'){
						$('#revenue_type').html('月營收明細');
						$('#table_result').html('&nbsp;').load('/month_revenue/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.DrawMonth();
					}
				});
			});
		}
	}
	
	Revenue.Tool = Tool;
}(window.Revenue = window.Revenue || {}));

(function(Dividend) {

	function Tool(){
		var drawTool = new DrawDividend.Tool();
		this.Init = function(){
			$(window).load(function(){
				drawTool.Draw();
				$('#revenue_type').html('股利政策');
				$('#table_result').html('&nbsp;').load('/dividend_table/', function () {
					$('#symbol').html($('#stock_id').html());
				});
			});
		}
	}
	
	Dividend.Tool = Tool;
}(window.Dividend = window.Dividend || {}));
