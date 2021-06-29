const date = new Date()

$(function(){
  namespace = '';
  var socket = io(namespace);

  socket.on('my response', function(msg) {
    if(msg.fromOthers === true){
      $('#log').prepend('<div class="row justify-content-start" style="width: 100%">' +
     '<div class="border-primary mb-3" style="max-width: 18rem; ">' + 
      
     '<div class="partner">' + msg.ip +' '+ now(date) + '</div>' + 
     '<div> ' + 
     '<p class="msg him">' + msg.content + '</p>' + 
     '</div>' + '</div>' + '</div>')
    }
    else{
      $('#log').prepend('<div class="row justify-content-end" style="width: 100%">' +
     '<div class="border-primary mb-3" style="max-width: 18rem; ">' + 
     '<div class="card-body text-success">' +
     '<div class="partner">'+ now(date) + '</div>' +
     
     '<p class="msg you">' + msg.content +  '</p>' + 
     
     '</div>' + '</div>' + '</div>')
    }
  });

  $('form#emit').submit(function(event) {
      if (!$('#emitData').val()) {
        alert('message value is null')
        $(document).scrollTop($(document).height());
        $('#emit')[0].reset();
        return false;

      } else {
        socket.emit('my_event', {data: $('#emitData').val()});
        $(document).scrollTop($(document).height());
        $('#emit')[0].reset();
        return false;
      }
      
  });

  function now(time) {
    return time.toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'});
  }

});