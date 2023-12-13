// -------------------------------  Video Frames update ------------------------------------
function refreshImage() {
    const img = document.getElementById('video_frame');
    img.src = '/video_frame'
}
  
setInterval(refreshImage, 33);

// -------------------------------  Recognized Objects update ------------------------------------
async function refreshRecognizedObjects() {
    const recognizedObjects = await (await fetch('/recognized_objects')).json();
    if (recognizedObjects.length > 0) {
        const element = document.getElementById('recognized_objects');
        element.innerHTML = '<li>' + recognizedObjects.join('<li>');
    }
}
setInterval(refreshRecognizedObjects, 750);

// --------------------------------  Fire Laser flag update ------------------------------------
async function refreshFireLaser() {
    const fireLaser = await (await fetch('/fire_laser')).json();
    const fire = document.getElementById('fire');
    fire.style.display = fireLaser ? 'inline' : 'none';
}
setInterval(refreshFireLaser, 400);


// -------------------------------- Set/get Searched Objects ------------------------------------
function setSearchObjects(){
    const searched_objects_input = document.getElementById('searched_objects_input').value;
    if (searched_objects_input) {
        fetch(`/set_search_objects?search_objects=${searched_objects_input}`);
    }
};

async function refreshSearchObjects() {
    const searched_objects = await (await fetch('/get_search_objects')).json();
    if (searched_objects) {
        document.getElementById('searched_objects').innerHTML = '<li>' + searched_objects.join('<li>')
    }
}
setInterval(refreshSearchObjects, 800);

// --------------------------------  Drone telemetry ------------------------------------
async function refreshDroneTelemetry() {
    const drone_telemetry = await (await fetch('/info')).json();
    const telemetry_element = document.getElementById('drone_telemetry');
    telemetry_element.innerText = `Battery: ${drone_telemetry.bat}%, Height: ${drone_telemetry.h || '0'} cm`;
}
setInterval(refreshDroneTelemetry, 1000);


// ---------------------------- Window event handlers ------------------------------
window.onload = () => {
    setSearchObjects();
};
window.onkeydown = (event) => {
    if (event.key === "Enter") {
        event.preventDefault(); // Cancel the default action, if needed
        setSearchObjects()
    }
}

// ------------------------  Send Drone commands mapped from GamePad ------------------------------
//   Drone commands conform to:
//   https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf
function sendDroneCommandFromGamepadState() {
  const controller = navigator.getGamepads ? navigator.getGamepads()[0] : false;

  if (controller) {
    let command = "";

    if (controller.buttons[3].pressed) command = "takeoff"; // X
    else if (controller.buttons[0].pressed) command = "land"; // B
    else if (controller.buttons[1].pressed) command = "streamon"; // A
    else if (controller.buttons[2].pressed) command = "streamoff"; // Y
    else if (controller.buttons[6].pressed) command = "flip l"; // ZL
    else if (controller.buttons[7].pressed) command = "flip r"; // ZR
    else if (controller.buttons[12].pressed) command = "up 40"; // ^
    else if (controller.buttons[13].pressed) command = "down 40"; // v
    else if (controller.buttons[14].pressed) command = "left 30"; // <-
    else if (controller.buttons[15].pressed) command = "right 30"; // ->
    else { // Just send an rc command wth the axes data
      const MAX = 60, DECIMALS = 4;
      const a = (controller.axes[0]*MAX).toFixed(DECIMALS);
      const b = (-controller.axes[1]*MAX).toFixed(DECIMALS);
      const d = (controller.axes[2]*MAX).toFixed(DECIMALS);
      const c = (-controller.axes[3]*MAX).toFixed(DECIMALS);
      command = `rc ${a} ${b} ${c} ${d}`;
    }

    sendDroneCommand(command);
  }
}
setInterval(sendDroneCommandFromGamepadState, 200);


function sendDroneCommand(command) {
  // Send drone command to webserver
  fetch(`/drone?command=${command}`);
}
