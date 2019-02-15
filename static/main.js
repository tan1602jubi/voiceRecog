window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
const recognition = new SpeechRecognition();
function listen(){
    recognition.start();
    recognition.onresult = (event) => {
        const speechToText = event.results[0][0].transcript;
        console.log(speechToText)
        // $("#text").append("<p> "+ speechToText + "</p>")
        $('#inputText').val(speechToText)
    }
}

function sendMessage(){

  let speech = document.getElementById("inputText").value
  $('#inputText').val("")
  let d = new Date()
      $('#chatArea').append('<div class="d-flex justify-content-end mb-4">\
           <div class="msg_cotainer_send"> '+ speech +' <span class="msg_time_send">'+d.toLocaleTimeString()+', Today</span></div>\
        <div class="img_cont_msg">\
      <img src="./static/user.gif" class="rounded-circle user_img_msg">\
        </div>\
      </div>')
      let d1 = new Date()

        $.ajax({
          type: "POST",
          headers: "application/json",
          url: "/usrSays",
          data: {"usrSays": speech},
          success: function(data) {
          console.log(JSON.stringify(data))
          let d1 = new Date()
            $('#chatArea').append('<div class="d-flex justify-content-start mb-4">\
            <div class="img_cont_msg"><img src="./static/mybot.jpg" class="rounded-circle user_img_msg">\
            </div> <div class="msg_cotainer">'+data["res"]+'<span class="msg_time">'+d1.toLocaleTimeString()+', Today</span>\
            </div> </div>')       
          },
          error: function() {
          }
      });
}