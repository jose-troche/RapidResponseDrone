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
    if (recognizedObjects.length > 0) {
        const element = document.getElementById('recognized_objects');
        element.innerHTML = '<li>' + recognizedObjects.join('<li>');
    }
}

setInterval(refreshRecognizedObjects, 750);

// -------------------------------- Set searched objects ------------------------------------


function setSearchObjects(){
    const searched_objects = document.getElementById('searched_objects').value;
    if (searched_objects) {
        fetch(`/set_search_objects?search_objects=${searched_objects}`);
    }
};
