function isInt(value)
{
    var er = /^-?[0-9]+$/;
    return er.test(value);
}

String.prototype.format = function() {
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
};

(function(filter_menu){
    function menu() {
        this.Init = function () {
            $(window).load(function(){
                $('.filter_option').html('&nbsp;').load('/filter_option/', {'kind':'revenue'}, function(){
                    bind_button_event();
                });

                $('.filter_menu_revenue').click(function(){
                    $('#filter_menu').html('&nbsp;').load('/filter_menu/', {'kind':'revenue'});
                    $('button[id^="filter_menu"]').attr('class', 'btn btn-primary');
                    
                });

                $('.start_filter').click(function(){
                    start_filter();
                });
            });
        }
    }


    function show_filter_menu(kind) {
        $(document).ready(function() {
            $('#filter_menu').html('&nbsp;').load('/filter_menu/', {'kind':kind}, function(){
                bind_button_event();
            });

        });
         var myObj = document.getElementsByClassName('btn btn-success');
         if (myObj.length >= 0) {
             myObj[0].className = 'btn btn-primary';
         }
    }

    ConditionDic = {};
    function bind_button_event(){
        $('.filter_choice').html('&nbsp;').load('/filter_choice/', function(){
        });
        $('.m_revenue_yoy_button').click(function() {
            var className = 'RevenueYoY'
            if (isInt($('.m_revenue_yoy_cnt').val()) && isInt($('.m_revenue_yoy_match_cnt').val()) &&isInt($('.m_revenue_yoy_percent').val())){
                var conditionText = '最近' + $('.m_revenue_yoy_cnt').val() + '個月內有' + $('.m_revenue_yoy_match_cnt').val() + '個月營收年增率大於' + $('.m_revenue_yoy_percent').val() + '%';
                var conditionID = "{0}_{1}_{2}_{3}".format(className,$('.m_revenue_yoy_cnt').val(),$('.m_revenue_yoy_match_cnt').val(),$('.m_revenue_yoy_percent').val());
                var str = '<tr class="danger"><td>' + conditionText;
                str = str + '<button type="submit" class="btn btn-primary btn-xs add_button"><span class="glyphicon glyphicon-minus"></span></button></td></tr>';
                var $obj = $(str);
                $obj.attr('id', conditionID)
                var params = {};
                params['class'] = className;
                params['timetype'] = 'month'
                params['overunder'] = 'gte'
                params['cnt'] = $('.m_revenue_yoy_cnt').val();
                params['matchcnt'] = $('.m_revenue_yoy_match_cnt').val();
                params['value'] = $('.m_revenue_yoy_percent').val();
                ConditionDic[conditionID] = params;
                $('.filter_choice_table').append($obj);
                $obj.click(function(){
                    var id = $(this).attr('id');
                    delete ConditionDic[id];
                    $(this).remove();
                });
            } else {
                console.log("error input");
            }
        });

    }

    

    function start_filter() {
        var ConditionArray = Object.keys(ConditionDic).map(function(key){
            return ConditionDic[key];
        });
        if (ConditionArray.length > 0){
            var jsonStr = JSON.stringify(ConditionArray);
            $.ajax({
                url: '/filter/start/',
                type: 'POST',
                data: jsonStr,
                contentType: 'application/json; charset=utf-8',
                success: function(res){
                    //alert(res);
                    $('#filter_result').html(res);
                }
            });

        }
    }

    filter_menu.menu = menu;
}(window.filter_menu = window.filter_menu ||{}));