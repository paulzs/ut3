$(document).ready(function(){

	var socket=io.connect('http://'+document.domain+':'+location.port+'/test')
	socket.on('my response', function(msg) {
		$('#log').append('<p>Received: '+msg.data+'</p>');
	});
	$('form#broadcast').submit(function(event){
		socket.emit('my broadcast event', {data $('#broadcast_data').val()			});
		return false;
	});
});
