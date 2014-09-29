(function(filter_menu){
    function menu() {
        this.Init = function () {
            $(window).load(function(){
                $('.filter_menu').html('&nbsp;').load('/filter_menu/', {'kind':'revenue'}, function(){
                    bind_button_event();
                });

                $('.filter_menu_revenue').click(function(){
                    alert('hello');
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

    ConditionArray = [];
    function bind_button_event(){

        $('button[id^=add-]').click(function(){
            var condition = $(this).attr('id').split('-')[1];
            var title = $(this).attr('title');
            //組條件字串
            var conditions = {};
            var timetype, overunder;
            conditions['class'] = condition;
            $('[id^=' + condition + '-]').each(function(){
                conditions[$(this).attr('id').split('-')[1]] = $(this).val();
            });
            if(conditions['timetype'] =='month'){
                timetype = '個月';
            }else if(conditions['timetype'] == 'season'){
                timetype = '季';
            }

            if(conditions['overunder'] == 'gte'){
                overunder = '大於';
            }else{
                overunder = '小於';
            }
            ConditionArray.push(conditions);
            //條件 字串
            var conditionStr = conditions['cnt'] + timetype + '內有' + conditions['matchcnt'] + timetype + title + overunder + conditions['value'];

            //將選擇的條件區塊放到div#fileter_content
            var cloneObj = $(this).clone();
            var newID = $(this).attr('id') + '-select';
            cloneObj.attr('id', newID).attr('class','btn btn-success').css({'width':'20em', 'margin':'0.5em'}).text(conditionStr).appendTo('#filter_content');

        });
    }

    function start_filter() {
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