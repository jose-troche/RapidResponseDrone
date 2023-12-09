function refreshImage() {
    var img = document.getElementById('video_frame');
    img.src = '/video_frame'
}
  
setInterval(refreshImage, 33);
