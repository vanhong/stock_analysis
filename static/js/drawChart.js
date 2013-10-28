(function(Draw) {
    function Tool() {
        String.prototype.endsWith = function(pattern) {
            var d = this.length - pattern.length;
            return d >= 0 && this.lastIndexOf(pattern) === d;
        };
        var GetData = function(url) {
            $.get(url, function(jData){
                // alert(JSON.stringify(jData));
                //$('#chart_result').html(jData);
                if (jData.dataNum >= 24) {
                    scroll = true;
                } else {
                    scroll = false;
                }
                $('#chart_result').highcharts({
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
                GetData('/getRevenueChart/');
        }
        this.DrawSeason = function() {
                GetData('/getSeasonRevenueChart/');
        }
    }
    Draw.Tool = Tool;
} (window.Draw = window.Draw || {}));

(function(DrawDividend) {
    function Tool() {
        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#chart_result').html(jData);
                $('#chart_result').highcharts({
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
                GetData('/getDividendChart/');
        }
    }
    DrawDividend.Tool = Tool;
} (window.DrawDividend = window.DrawDividend || {}));

(function(DrawBasicLine) {
    function Tool() {
        var GetData = function(url) {
            $.get(url, function(jData){
                // alert(JSON.stringify(jData));
                //$('#chart_result').html(jData);
                var series = [];
                for(i=0; i<jData.names.length; i++){
                     series.push({
                         name: jData.names[i],
                         data: jData.datas[i],
                     });
                }
                $('#chart_result').highcharts({
                    title: {
                        text: '',
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
                                    format: '{value}' + jData.yUnit
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
                    series: series
                });
            });
        }
        this.Init = function(data_url) {
            GetData(data_url);
        }
    }
    DrawBasicLine.Tool = Tool;
} (window.DrawBasicLine = window.DrawBasicLine || {}));