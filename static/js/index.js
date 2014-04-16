$(document).ready(function() {
    if (!"WebSocket" in window) {
        throw {
            name: "WebSocketError",
            message: "WebSockets are not supported by this browser"
        };  
    } 

    socket = new WebSocket("ws://localhost:8000/talk");

    socket.onopen = function(){
        console.log("open");
    };

    socket.onmessage = function(msg) {
        console.log("Received message: ");
        console.log(msg);
        if (msg.data == "ping") {
            socket.send("pong");
        }
        $("#messages").append("<p>"+msg.data+"</p>");
    };

    socket.onclose = function() {
        console.log("close");
    };

    $("#submit").click(function() {
        socket.send($("#input").val());
    });
});
