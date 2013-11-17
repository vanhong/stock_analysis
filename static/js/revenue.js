(function(Revenue) {

	function Tool(){
		var drawTool = new Draw.Tool();
		this.Init = function(){
			$(window).load(function(){
				drawTool.DrawMonth();
				$('#table_result').html('&nbsp;').load('/get_month_revenue_table/', function () {
					$('#symbol').html($('#stock_id').html());
				});
				$( '#month_revenue' ).click( function() {
					if (!$('#month_revenue').hasClass('btn-success')){
						$('#season_revenue').attr('class', 'btn btn-primary');
						$('#season_profit').attr('class', 'btn btn-primary');
						$('#month_revenue').attr('class', 'btn btn-success');
						drawTool = new Draw.Tool();
						$('#table_result').html('&nbsp;').load('/get_month_revenue_table/');
						drawTool.DrawMonth();
					}
				});
				$( '#season_revenue' ).click( function() {
					if (!$('#season_revenue').hasClass('btn-success')) {
						$('#season_revenue').attr('class', 'btn btn-success');
						$('#season_profit').attr('class', 'btn btn-primary');
						$('#month_revenue').attr('class', 'btn btn-primary');
						drawTool = new Draw.Tool();
						$('#table_result').html('&nbsp;').load('/get_season_revenue_table/');
						drawTool.DrawSeason();
					}
				});
				$( '#season_profit').click(function () {
					if (!$('#season_profit').hasClass('btn-success')) {
						$('#season_revenue').attr('class', 'btn btn-primary');
						$('#season_profit').attr('class', 'btn btn-success');
						$('#month_revenue').attr('class', 'btn btn-primary');
						drawTool = new Draw.Tool();
						$('#table_result').html('&nbsp').load('/get_season_profit_table/');
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
				$('#table_result').html('&nbsp;').load('/get_profitability_table/', {'time_type':'season'}, function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_profitability_chart/', 'season');

				$('#season_profitability').click(function () {
					if (!$('#season_profitability').hasClass('btn-success')) {
						$('#season_profitability').attr('class', 'btn btn-success');
						$('#year_profitability').attr('class', 'btn btn-primary');
						$('#table_result').html('&nbsp').load('/get_profitability_table/', {'time_type': 'season'});
						drawTool.Init('/get_profitability_chart', 'season');
					}
				});

				$('#year_profitability').click(function () {
					if (!$('#year_profitability').hasClass('btn-success')) {
						$('#season_profitability').attr('class', 'btn btn-primary');
						$('#year_profitability').attr('class', 'btn btn-success');
						$('#table_result').html('&nbsp').load('/get_profitability_table/', {'time_type':'year'});
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
				$('#table_result').html('&nbsp;').load('/get_performance_per_share_table/', {'time_type':'season'}, function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_performance_per_share_chart/', 'season');

				$('#season_performance_per_share').click(function () {
					if (!$('#season_performance_per_share').hasClass('btn-success')) {
						$('#season_performance_per_share').attr('class', 'btn btn-success');
						$('#year_performance_per_share').attr('class', 'btn btn-primary');
						$('#table_result').html('&nbsp').load('/get_performance_per_share_table/',{'time_type': 'season'});
						drawTool.Init('/get_performance_per_share_chart', 'season');
					}
				});

				$('#year_performance_per_share').click(function () {
					if (!$('#year_performance_per_share').hasClass('btn-success')) {
						$('#season_performance_per_share').attr('class', 'btn btn-primary');
						$('#year_performance_per_share').attr('class', 'btn btn-success');
						$('#table_result').html('&nbsp').load('/get_performance_per_share_table/', {'time_type': 'year'});
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
				$('#table_result').html('&nbsp;').load('/get_roe_roa_table/', {'time_type': 'season'}, function () {
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_roe_roa_chart/', 'season');
				$('#season_roe_roa').click(function () {
					if (!$('#season_roe_roa').hasClass('btn-success')) {
						$('#season_roe_roa').attr('class', 'btn btn-success');
						$('#year_roe_roa').attr('class', 'btn btn-primary');
						$('#table_result').html('&nbsp').load('/get_roe_roa_table/', {'time_type': 'season'});
						drawTool.Init('/get_roe_roa_chart', 'season');
					}
				});
				$('#year_roe_roa').click(function () {
					if (!$('#year_roe_roa').hasClass('btn-success')) {
						$('#season_roe_roa').attr('class', 'btn btn-primary');
						$('#year_roe_roa').attr('class', 'btn btn-success');
						$('#table_result').html('&nbsp').load('/get_roe_roa_table/', {'time_type': 'year'});
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
				$('#table_result').html('&nbsp;').load('/get_turnover_ratio_table/', {'time_type': 'season'}, function(){
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_turnover_ratio_chart/', 'season');
				$('#season_turnover_ratio').click(function () {
					if (!$('#season_turnover_ratio').hasClass('btn-success')) {
						$('#season_turnover_ratio').attr('class', 'btn btn-success');
						$('#year_turnover_ratio').attr('class', 'btn btn-primary');
						$('#table_result').html('&nbsp').load('/get_turnover_ratio_table/', {'time_type': 'season'});
						drawTool.Init('/get_turnover_ratio_chart', 'season');
					}
				});
				$('#year_turnover_ratio').click(function () {
					if (!$('#year_turnover_ratio').hasClass('btn-success')) {
						$('#season_turnover_ratio').attr('class', 'btn btn-primary');
						$('#year_turnover_ratio').attr('class', 'btn btn-success');
						$('#table_result').html('&nbsp').load('/get_turnover_ratio_table/', {'time_type': 'year'});
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
			$('#table_result').html('&nbsp;').load('/get_current_ratio_table/', {'time_type': 'season'}, function(){
				$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_current_ratio_chart/', 'season');
				$('#season_current_ratio').click(function () {
					if (!$('#season_current_ratio').hasClass('btn-success')) {
						$('#season_current_ratio').attr('class', 'btn btn-success');
						$('#year_current_ratio').attr('class', 'btn btn-primary');
						$('#table_result').html('&nbsp').load('/get_current_ratio_table/', {'time_type': 'season'});
						drawTool.Init('/get_current_ratio_chart', 'season');
					}
				});
				$('#year_current_ratio').click(function () {
					if (!$('#year_current_ratio').hasClass('btn-success')) {
						$('#season_current_ratio').attr('class', 'btn btn-primary');
						$('#year_current_ratio').attr('class', 'btn btn-success');
						$('#table_result').html('&nbsp').load('/get_current_ratio_table/', {'time_type': 'year'});
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
				$('#table_result').html('&nbsp;').load('/get_debt_ratio_table/', {'time_type':'season'}, function(){
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_debt_ratio_chart/', 'season');
				$('#season_debt_ratio').click(function () {
					if (!$('#season_debt_ratio').hasClass('btn-success')) {
						$('#season_debt_ratio').attr('class', 'btn btn-success');
						$('#year_debt_ratio').attr('class', 'btn btn-primary');
						$('#table_result').html('&nbsp').load('/get_debt_ratio_table/', {'time_type': 'season'});
						drawTool.Init('/get_debt_ratio_chart', 'season');
					}
				});
				$('#year_debt_ratio').click(function () {
					if (!$('#year_debt_ratio').hasClass('btn-success')) {
						$('#season_debt_ratio').attr('class', 'btn btn-primary');
						$('#year_debt_ratio').attr('class', 'btn btn-success');
						$('#table_result').html('&nbsp').load('/get_debt_ratio_table/', {'time_type': 'year'});
						drawTool.Init('/get_debt_ratio_chart', 'year');
					}
				});
			});
		}
	}
	DebtRatio.Tool = Tool;
}(window.DebtRatio = window.DebtRatio || {}));

(function(InterestCover) {
	function Tool () {
		var drawTool = new DrawBasicLine.Tool();
		this.Init = function(){
			$(window).load(function(){
				$('#table_result').html('&nbsp;').load('/get_interest_cover_table/', {'time_type':'season'}, function(){
					$('#symbol').html($('#stock_id').html());
				});
				drawTool.Init('/get_interest_cover_chart/', 'season');
				$('#season_interest_cover').click(function () {
					if (!$('#season_interest_cover').hasClass('btn-success')) {
						$('#season_interest_cover').attr('class', 'btn btn-success');
						$('#year_interest_cover').attr('class', 'btn btn-primary');
						$('#table_result').html('&nbsp').load('/get_interest_cover_table/', {'time_type': 'season'});
						drawTool.Init('/get_interest_cover_chart', 'season');
					}
				});
				$('#year_interest_cover').click(function () {
					if (!$('#year_interest_cover').hasClass('btn-success')) {
						$('#season_interest_cover').attr('class', 'btn btn-primary');
						$('#year_interest_cover').attr('class', 'btn btn-success');
						$('#table_result').html('&nbsp').load('/get_interest_cover_table/', {'time_type': 'year'});
						drawTool.Init('/get_interest_cover_chart', 'year');
					}
				});
			});
		}
	}
	InterestCover.Tool = Tool;
}(window.InterestCover = window.InterestCover || {}));
