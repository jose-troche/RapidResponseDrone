function refreshImage() {
    var img = document.getElementById('video_frame');
    img.src = '/video_frame'
}
  
setInterval(refreshImage, 33);


/**
 * Sends a drone command to the webserver
 */
function sendDroneCommand(command) {
    // console.log("Sending drone command: ", command);
    fetch(`/drone?command=${command}`);
  }
  
