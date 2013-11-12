(function(Revenue) {

	function Tool(){
		var drawTool = new Draw.Tool();
		this.Init = function(){
			$(window).load(function(){
				drawTool.DrawMonth();
				$('#data_type').html('月營收明細');
				$('#table_result').html('&nbsp;').load('/get_month_revenue_table/', function () {
					$('#symbol').html($('#stock_id').html());
				});
				$( '#month_revenue' ).click( function() {
					if ($('#data_type').html() != '月營收明細'){
						drawTool = new Draw.Tool();
						$('#data_type').html('月營收明細');
						$('#table_result').html('&nbsp;').load('/get_month_revenue_table/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.DrawMonth();
					}
				});
				$( '#season_revenue' ).click( function() {
					if ($('#data_type').html() != '季營收明細') {
						drawTool = new Draw.Tool();
						$('#data_type').html('季營收明細');
						$('#table_result').html('&nbsp;').load('/get_season_revenue_table/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.DrawSeason();
					}
				});
				$( '#season_profit').click(function () {
					if ($('#data_type').html() != '季盈餘明細') {
						drawTool = new Draw.Tool();
						$('#data_type').html('季盈餘明細');
						$('#table_result').html('&nbsp').load('/get_season_profit_table/', function(){
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
				$('#data_type').html('季獲利能力');
				$('#table_result').html('&nbsp;').load('/get_season_profitability_table/', function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_season_profitability_chart/');

				$('#season_profitability').click(function () {
					if ($('#data_type').html() != '季獲利能力') {
						$('#data_type').html('季獲利能力');
						$('#table_result').html('&nbsp').load('/get_season_profitability_table/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_season_profitability_chart');
					}
				});

				$('#year_profitability').click(function () {
					if ($('#data_type').html() != '年獲利能力') {
						$('#data_type').html('年獲利能力');
						$('#table_result').html('&nbsp').load('/get_year_profitability_table/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_year_profitability_chart');
					}
				});
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
				$('#data_type').html('季經營績效');
				$('#table_result').html('&nbsp;').load('/get_season_performance_per_share_table/', function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_season_performance_per_share_chart/');

				$('#season_performance_per_share').click(function () {
					if ($('#data_type').html() != '季經營績效') {
						$('#data_type').html('季經營績效');
						$('#table_result').html('&nbsp').load('/get_season_performance_per_share_table/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_season_performance_per_share_chart');
					}
				});

				$('#year_performance_per_share').click(function () {
					if ($('#data_type').html() != '年經營績效') {
						$('#data_type').html('年經營績效');
						$('#table_result').html('&nbsp').load('/get_year_performance_per_share_table/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_year_performance_per_share_chart');
					}
				});
			});
		}
	}
	PerformancePerShare.Tool = Tool;
}(window.PerformancePerShare = window.PerformancePerShare || {}));

(function(ROE) {
	function Tool () {
		var drawTool = new DrawBasicLine.Tool();
		this.Init = function(){
			$(window).load(function(){
				$('#data_type').html('季ROE/ROA');
				$('#table_result').html('&nbsp;').load('/get_season_roe_roa_table/', function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_season_roe_roa_chart/');

				$('#season_roe_roa').click(function () {
					if ($('#data_type').html() != '季ROE/ROA') {
						$('#data_type').html('季ROE/ROA');
						$('#table_result').html('&nbsp').load('/get_season_roe_roa_table/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_season_roe_roa_chart');
					}
				});

				$('#year_roe_roa').click(function () {
					if ($('#data_type').html() != '年ROE/ROA') {
						$('#data_type').html('年ROE/ROA');
						$('#table_result').html('&nbsp').load('/get_year_roe_roa_table/', function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_year_roe_roa_chart');
					}
				});
			});
		}

	}
	ROE.Tool = Tool;
}(window.ROE = window.ROE || {}));

(function(Dividend) {
	function Tool(){
		var drawTool = new DrawDividend.Tool();
		this.Init = function(){
			$(window).load(function(){
				drawTool.Draw();
				$('#data_type').html('股利政策');
				$('#table_result').html('&nbsp;').load('/get_dividend_table/', function () {
					$('#symbol').html($('#stock_id').html());
				});
			});
		}
	}
	Dividend.Tool = Tool;
}(window.Dividend = window.Dividend || {}));

(function(CurrentRatio) {
	function Tool () {
		var drawTool = new DrawBasicLine.Tool();
		this.Init = function(){
			$(window).load(function(){
				$('#data_type').html('流動比/速動比');
				$('#table_result').html('&nbsp;').load('/get_season_current_ratio_table/', function(){
					$('#symbol').html($('#stock_id').html());
				})
			});
			drawTool.Init('/get_season_current_ratio_chart/');
		}
	}
	CurrentRatio.Tool = Tool;
}(window.CurrentRatio = window.CurrentRatio || {}));

(function(DebtRatio) {
	function Tool () {
		var drawTool = new DrawBasicLine.Tool();
		this.Init = function(){
			$(window).load(function(){
				$('#data_type').html('負債比率');
				$('#table_result').html('&nbsp;').load('/get_season_debt_ratio_table/', function(){
					$('#symbol').html($('#stock_id').html());
				})
			});
			drawTool.Init('/get_season_debt_ratio_chart/');
		}
	}
	DebtRatio.Tool = Tool;
}(window.DebtRatio = window.DebtRatio || {}));
