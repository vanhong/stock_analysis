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
				$( '#month_revenue' ).click( function() {
					if ($('#revenue_type').html() != '月營收明細'){
						drawTool = new Draw.Tool();
						$('#revenue_type').html('月營收明細');
						$('#table_result').html('&nbsp;').load('/month_revenue/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.DrawMonth();
					}
				});
				$( '#season_revenue' ).click( function() {
					if ($('#revenue_type').html() != '季營收明細') {
						drawTool = new Draw.Tool();
						$('#revenue_type').html('季營收明細');
						$('#table_result').html('&nbsp;').load('/season_revenue/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.DrawSeason();
					}
				});
				$( '#season_profit').click(function () {
					if ($('#revenue_type').html() != '季盈餘明細') {
						drawTool = new Draw.Tool();
						$('#revenue_type').html('季盈餘明細');
						$('#table_result').html('&nbsp').load('/season_profit/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.DrawSeasonProfit();
					}
				});
			});
		}
	}
	
	Revenue.Tool = Tool;
}(window.Revenue = window.Revenue || {}));

(function(Profitability) {
	function Tool(){
		var drawTool = new DrawBasicLine.Tool();
		this.Init = function(){
			$(window).load(function(){
				$('#profitability_type').html('季獲利能力');
				$('#table_result').html('&nbsp;').load('/season_profitability/', function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/getProfitabilityChart/');
			});
		}	
	}
	Profitability.Tool = Tool;
}(window.Profitability = window.Profitability || {}));

(function(PerformancePerShare) {
	function Tool () {
		var drawTool = new DrawBasicLine.Tool();
		this.Init = function(){
			$(window).load(function(){
				$('#data_type').html('經營績效');
				$('#table_result').html('&nbsp;').load('/performance_per_share_table/', function(){
					$('#symbol').html($('#stock_id').html());
				})
			});
			drawTool.Init('/get_performance_per_share/');
		}
	}
	PerformancePerShare.Tool = Tool;
}(window.PerformancePerShare = window.PerformancePerShare || {}));

(function(Dividend) {
	function Tool(){
		var drawTool = new DrawDividend.Tool();
		this.Init = function(){
			$(window).load(function(){
				drawTool.Draw();
				$('#data_type').html('股利政策');
				$('#table_result').html('&nbsp;').load('/dividend_table/', function () {
					$('#symbol').html($('#stock_id').html());
				});
			});
		}
	}
	Dividend.Tool = Tool;
}(window.Dividend = window.Dividend || {}));
