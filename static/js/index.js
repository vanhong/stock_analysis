$( document ).ready( function() {
	$( '#searchSubmit' ).click( function() {
		q = $( '#q' ).val();
		$( '#stockid' ).html( '&nbsp;' ).load( '{% url "demo_user_search" %}?q=' + q );
	});
});

$( document ).ajaxStart( function() {
	$( '#spinner' ).show();
}).ajaxStop( function() {
	$( '#spinner' ).hide();
});