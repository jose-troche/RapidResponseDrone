function refreshImage() {
    const img = document.getElementById('video_frame');
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


async function refreshRecognizedObjects() {
    const recognizedObjects = await (await fetch('/recognized_objects')).json();
    const element = document.getElementById('recognized_objects');
    element.innerHTML = recognizedObjects.join()
}

setInterval(refreshRecognizedObjects, 750);
