(function(Draw) {

    function Tool() {

        String.prototype.endsWith = function(pattern) {
            var d = this.length - pattern.length;
            return d >= 0 && this.lastIndexOf(pattern) === d;
        };

        var GetData = function(url) {
            $.get(url, function(jData){
                // alert(JSON.stringify(jData));
                //$('#Result').html(jData);
                if (jData.dataNum >= 24) {
                    scroll = true;
                } else {
                    scroll = false;
                }
                $('#Result').highcharts({
                    chart: {
                        zoomType: 'xy',
                        plotBorderWidth: 1
                    },
                    title: jData.title,
                    subtitle: jData.subtitle,
                    xAxis: [{
                            categories: jData.categories, 
                            labels: {
                                //step: 6,
                                formatter: function() {
                                    if (this.value.endsWith('01') || this.value.endsWith('07')){
                                        return this.value;
                                    }
                                }
                            },
                            max: jData.dataNum - 1,
                            //minRange: 12,
                    }],
                    yAxis: [{ // Primary yAxis
                        labels: {
                            format: '{value}%',
                            style: {
                                color: '#89A54E'
                            }
                        },
                        title: {
                            text: '',
                            style: {
                                color: '#89A54E'
                            }
                        }
                    }, { // Secondary yAxis
                        title: {
                            text: '',
                            style: {
                                color: '#4572A7'
                            }
                        },
                        labels: {
                            format: '{value} 仟元',
                            style: {
                                color: '#4572A7'
                            }
                        },
                        opposite: true
                    }],
                    tooltip: {
                        shared: true
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'left',
                        x: 120,
                        verticalAlign: 'top',
                        y: 100,
                        floating: true,
                        backgroundColor: '#FFFFFF'
                    },
                    series: [{
                        name: '營收',
                        color: '#4572A7',
                        type: 'column',
                        yAxis: 1,
                        data: jData.revenue,
                        tooltip: {
                            valueSuffix: '(仟元)'
                        }
                    }, {
                        name: '成長率',
                        color: '#89A54E',
                        type: 'line',
                        data: jData.growth_rate,
                        tooltip: {
                            valueSuffix: '%'
                        }
                    }],
                    scrollbar: {
                        enabled: scroll
                    }
                });    
            });
        }

        this.DrawMonth = function() {
            //alert("Init");
            // $(window).load(function() {
                //Default figure
                GetData('/getRevenueChart/');
            // });
        }
        this.DrawSeason = function() {
            // $(window).load(function() {
                //Default figure
                GetData('/getSeasonRevenueChart/');
            // });
        }
    }
    Draw.Tool = Tool;
} (window.Draw = window.Draw || {}));

(function(DrawDividend) {

    function Tool() {

        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#Result').html(jData);
                $('#Result').highcharts({
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: ''
                    },
                    xAxis: {
                        categories: jData.categories,
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        },
                        stackLabels: {
                            enabled: true,
                            style: {
                                fontWeight: 'bold',
                                color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                            }
                        }
                    },
                    legend: {
                        align: 'right',
                        x: -70,
                        verticalAlign: 'top',
                        y: 20,
                        floating: true,
                        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColorSolid) || 'white',
                        borderColor: '#CCC',
                        borderWidth: 1,
                        shadow: false
                    },
                    tooltip: {
                        formatter: function() {
                            return '<b>'+ this.x +'</b><br/>'+
                                this.series.name +': '+ this.y +'<br/>'+
                                'Total: '+ this.point.stackTotal;
                        }
                    },
                    plotOptions: {
                        column: {
                            stacking: 'normal',
                            dataLabels: {
                                enabled: true,
                                color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                            }
                        }
                    },
                    series: [{
                        name: '現金股利',
                        data: jData.cash_dividends
                    }, {
                        name: '股票股利',
                        data: jData.stock_dividends
                    }],
                });
            });
        }

        this.Draw = function() {
            //alert("Init");
                //Default figure
                GetData('/getDividendChart/');
        }
    }
    DrawDividend.Tool = Tool;
} (window.DrawDividend = window.DrawDividend || {}));

(function(DrawProfitbility) {

    function Tool() {

        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#Result').html(jData);
                $('#Result').highcharts({
                    title: {
                        text: '獲利能力',
                        x: -20 //center
                    },
                    xAxis: {
                        categories: jData.categories
                    },
                    yAxis: {
                        title: {
                            text: ''
                        },
                        labels: {
                                    format: '{value}%'
                                },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    tooltip: {
                        valueSuffix: ''
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        borderWidth: 0
                    },
                    series: [{
                        name: '毛利率',
                        data: jData.gross_profit_margins
                    }, {
                        name: '營益率',
                        data: jData.operating_profit_margins
                    }, {
                        name: '稅前淨利率',
                        data: jData.net_before_tax_profit_margins
                    }, {
                        name: '稅後淨利率',
                        data: jData.net_after_tax_profit_margins
                    }]
                });
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                //Default figure
                GetData('/getProfitabilityChart/');

                
            });
        }
    }
    DrawProfitbility.Tool = Tool;
} (window.DrawProfitbility = window.DrawProfitbility || {}));

(function(DrawPerformancePerShare) {
    function Tool () {
        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#Result').html(jData);
                $('#Result').highcharts({
                    title: {
                        text: '經營績效',
                        x: -20 //center
                    },
                    xAxis: {
                        categories: jData.categories
                    },
                    yAxis: {
                        title: {
                            text: ''
                        },
                        labels: {
                                    format: '{value}'
                                },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    tooltip: {
                        valueSuffix: ''
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        borderWidth: 0
                    },
                    series: [{
                        name: '稅前每股盈餘',
                        data: jData.net_before_tax_profit_per_shares
                    }, {
                        name: '稅後每股盈餘',
                        data: jData.net_after_tax_profit_per_shares
                    }]
                });
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                //Default figure
                GetData('/get_performance_per_share/');

                
            });
        }
    }
    DrawPerformancePerShare.Tool = Tool;
} (window.DrawPerformancePerShare = window.DrawPerformancePerShare || {}));
