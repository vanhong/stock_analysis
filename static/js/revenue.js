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
				$('#table_result').html('&nbsp;').load('/get_profitability_table/', {'time_type':'season'}, function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_profitability_chart/', 'season');

				$('#season_profitability').click(function () {
					if ($('#data_type').html() != '季獲利能力') {
						$('#data_type').html('季獲利能力');
						$('#table_result').html('&nbsp').load('/get_profitability_table/', {'time_type': 'season'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_profitability_chart', 'season');
					}
				});

				$('#year_profitability').click(function () {
					if ($('#data_type').html() != '年獲利能力') {
						$('#data_type').html('年獲利能力');
						$('#table_result').html('&nbsp').load('/get_profitability_table/', {'time_type':'year'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_profitability_chart', 'year');
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
				$('#table_result').html('&nbsp;').load('/get_performance_per_share_table/', {'time_type':'season'}, function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_performance_per_share_chart/', 'season');

				$('#season_performance_per_share').click(function () {
					if ($('#data_type').html() != '季經營績效') {
						$('#data_type').html('季經營績效');
						$('#table_result').html('&nbsp').load('/get_performance_per_share_table/',{'time_type': 'season'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_performance_per_share_chart', 'season');
					}
				});

				$('#year_performance_per_share').click(function () {
					if ($('#data_type').html() != '年經營績效') {
						$('#data_type').html('年經營績效');
						$('#table_result').html('&nbsp').load('/get_performance_per_share_table/', {'time_type': 'year'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_performance_per_share_chart', 'year');
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
				$('#table_result').html('&nbsp;').load('/get_roe_roa_table/', {'time_type': 'season'}, function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_roe_roa_chart/', 'season');
				$('#season_roe_roa').click(function () {
					if ($('#data_type').html() != '季ROE/ROA') {
						$('#data_type').html('季ROE/ROA');
						$('#table_result').html('&nbsp').load('/get_roe_roa_table/', {'time_type': 'season'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_roe_roa_chart', 'season');
					}
				});
				$('#year_roe_roa').click(function () {
					if ($('#data_type').html() != '年ROE/ROA') {
						$('#data_type').html('年ROE/ROA');
						$('#table_result').html('&nbsp').load('/get_roe_roa_table/', {'time_type': 'year'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_roe_roa_chart', 'year');
					}
				});
			});
		}
	}
	ROE.Tool = Tool;
}(window.ROE = window.ROE || {}));

(function(TurnoverRatio) {
	function Tool () {
		var drawTool = new DrawBasicLine.Tool();
		this.Init = function(){
			$(window).load(function(){
				$('#data_type').html('季經營週轉能力');
				$('#table_result').html('&nbsp;').load('/get_turnover_ratio_table/', {'time_type': 'season'}, function(){
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_turnover_ratio_chart/', 'season');
				$('#season_turnover_ratio').click(function () {
					if ($('#data_type').html() != '季經營週轉能力') {
						$('#data_type').html('季經營週轉能力');
						$('#table_result').html('&nbsp').load('/get_turnover_ratio_table/', {'time_type': 'season'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_turnover_ratio_chart', 'season');
					}
				});
				$('#year_turnover_ratio').click(function () {
					if ($('#data_type').html() != '年經營週轉能力') {
						$('#data_type').html('年經營週轉能力');
						$('#table_result').html('&nbsp').load('/get_turnover_ratio_table/', {'time_type': 'year'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_turnover_ratio_chart', 'year');
					}
				});
			});
		}
	}
	TurnoverRatio.Tool = Tool;
}(window.TurnoverRatio = window.TurnoverRatio || {}));

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
			$('#data_type').html('流動比/速動比(季)');
			$('#table_result').html('&nbsp;').load('/get_current_ratio_table/', {'time_type': 'season'}, function(){
				$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_current_ratio_chart/', 'season');
				$('#season_current_ratio').click(function () {
					if ($('#data_type').html() != '流動比/速動比(季)') {
						$('#data_type').html('流動比/速動比(季)');
						$('#table_result').html('&nbsp').load('/get_current_ratio_table/', {'time_type': 'season'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_current_ratio_chart', 'season');
					}
				});
				$('#year_current_ratio').click(function () {
					if ($('#data_type').html() != '流動比/速動比(年)') {
						$('#data_type').html('流動比/速動比(年)');
						$('#table_result').html('&nbsp').load('/get_current_ratio_table/', {'time_type': 'year'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_current_ratio_chart', 'year');
					}
				});
			});
		}
	}
	CurrentRatio.Tool = Tool;
}(window.CurrentRatio = window.currentRatio || {}));

(function(DebtRatio) {
	function Tool () {
		var drawTool = new DrawBasicLine.Tool();
		this.Init = function(){
			$(window).load(function(){
				$('#data_type').html('負債比率(季)');
				$('#table_result').html('&nbsp;').load('/get_debt_ratio_table/', {'time_type':'season'}, function(){
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_debt_ratio_chart/', 'season');
				$('#season_debt_ratio').click(function () {
					if ($('#data_type').html() != '負債比率(季)') {
						$('#data_type').html('負債比率(季)');
						$('#table_result').html('&nbsp').load('/get_debt_ratio_table/', {'time_type': 'season'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_debt_ratio_chart', 'season');
					}
				});
				$('#year_debt_ratio').click(function () {
					if ($('#data_type').html() != '負債比率(年)') {
						$('#data_type').html('負債比率(年)');
						$('#table_result').html('&nbsp').load('/get_debt_ratio_table/', {'time_type': 'year'}, function(){
							$('#symbol').html($('#stock_id').html());
						});
						drawTool.Init('/get_debt_ratio_chart', 'year');
					}
				});
			});
		}
	}
	DebtRatio.Tool = Tool;
}(window.DebtRatio = window.DebtRatio || {}));
