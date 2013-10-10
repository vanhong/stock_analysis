(function(Draw) {

    function Tool() {

        var doFilter = function() {
            $.post('{% url "dofilter" %}' , 
                function(data, status) { 
                    alert("after load, get data=" + data + ", status=" + status); 
                    $('#FilterResult').css('display','block');
                }).fail(function(xhr){alert('error=' + xhr.statusText);});
        }

        String.prototype.endsWith = function(pattern) {
            var d = this.length - pattern.length;
            return d >= 0 && this.lastIndexOf(pattern) === d;
        };

        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#Result').html(jData);
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
                                    if (this.value.endsWith('01')){
                                        return this.value;
                                    }
                                }
                            }
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
                        type: 'spline',
                        data: jData.growth_rate,
                        tooltip: {
                            valueSuffix: '%'
                        }
                    }]//,
                    //scrollbar: {
                    //    enabled: true
                    //}
                });    
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                //Default figure
                GetData('/getRevenueChart/');

                //$('#Data').click(function(){
                //    GetData('url2');
                //    alert('revenue data');
                //});
    			//$('#Data2').click(function(){
                //    //FilterResult
                //    GetData('url2');
                //});

                //$('#Data3').click(function(){
                //    //FilterResult
                //    GetData('url3');
                //});
            });
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

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                //Default figure
                GetData('/getDividendChart/');

                //$('#Data').click(function(){
                //    GetData('url2');
                //    alert('revenue data');
                //});
                //$('#Data2').click(function(){
                //    //FilterResult
                //    GetData('url2');
                //});

                //$('#Data3').click(function(){
                //    //FilterResult
                //    GetData('url3');
                //});
            });
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
                text: 'Monthly Average Temperature',
                x: -20 //center
            },
            subtitle: {
                text: 'Source: WorldClimate.com',
                x: -20
            },
            xAxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            },
            yAxis: {
                title: {
                    text: 'Temperature (°C)'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                valueSuffix: '°C'
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [{
                name: 'Tokyo',
                data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
            }, {
                name: 'New York',
                data: [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
            }, {
                name: 'Berlin',
                data: [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
            }, {
                name: 'London',
                data: [3.9, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
            }]
        });
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                //Default figure
                GetData('/getDividendChart/');

                //$('#Data').click(function(){
                //    GetData('url2');
                //    alert('revenue data');
                //});
                //$('#Data2').click(function(){
                //    //FilterResult
                //    GetData('url2');
                //});

                //$('#Data3').click(function(){
                //    //FilterResult
                //    GetData('url3');
                //});
            });
        }
    }
    DrawProfitbility.Tool = Tool;
} (window.DrawProfitbility = window.DrawProfitbility || {}));