$(document).ready(function() {
    if (!"WebSocket" in window) {
        throw {
            name: "WebSocketError",
            message: "WebSockets are not supported by this browser"
        };  
    } 

    socket = new WebSocket("ws://" + window.location.host + "/talk");

    socket.onopen = function(){
        console.log("open");
    };

    socket.onmessage = function(msg) {
        console.log("Received message: ");
        console.log(msg);
        $("#messages").append("<p>"+msg.data+"</p>");
    };

    socket.onclose = function() {
        console.log("close");
    };

    $("#submit").click(function() {
        socket.send($("#input").val());
    });
});
