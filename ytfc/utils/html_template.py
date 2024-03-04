html_begin = """<!DOCTYPE html>
<html>
  <head>
    <title>Feeds</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Nunito+Sans|Pontano+Sans|Work+Sans|Quattrocento+Sans">
    <style type="text/css">
      h1, h2 {
        margin: 10px;
        padding: 5px;
        background-color: #ccc;
      }
      h1 {
        font-family: "Nunito Sans", sans-serif;
      }
      /* id title */
      h2 {
        font-family: "Nunito Sans", sans-serif;
        background-color: #ccc;
      }
      
      /* main text */
      p, div {
        font-family: "Work Sans", sans-serif;
      }
      
      /* urls */
      a {
        font-family: "Quattrocento Sans", sans-serif;
        text-decoration: none;
      }
      
      /* channel or playlist feed */
      div.feed-info {
        display: block;
        margin: 10px;
        padding: 5px;
      }
      
      /* videos */
      div.video-block {
        display: inline-block;
        width: 320px; /* height depends on the title length */
        margin: 10px;
        padding: 5px;
        vertical-align: top;
      }
      div.video-title {
        font-family: "Pontano Sans", sans-serif;
        font-weight: bold;
        font-size: 1.1em;
      }
      span.video-description {
        font-family: "Nunito Sans", sans-serif;
      }
      
      /* popup over video */
      .description-popup {
        position: relative;
        display: inline-block;
        cursor: pointer;
        width: 100%;
      }
      .description-popup .popup-text {
        visibility: hidden;
        background-color: #555;
        color: #fff;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: -5px;
        width: 100%;
        max-height: 200px;
        overflow: auto;
        cursor: auto;
      }
      .description-popup .show {
        visibility: visible;
      }
      
      /* open in new window, open in new tab */
      div.video-url {
        text-align: center; /* center buttons */
        margin: 10px auto;
      }
      /* open in new window */
      button.video-popup {
        margin-right: 5px;
      }

      /* video thumbnail and frames */
      .slider-container {
        width: 320px;
      }
      .slider {
        width: 320px;
        height: 240px;
        position: relative;
      }
      .slider img {
        position: absolute;
        top: 0;
        left: 0;
      }
      .slider img:first-child {
        z-index: 1;
      }
      .slider img:nth-child(2) {
        z-index: 0;
      }
      .navigation-buttons {
        width: 320px;
        margin: 5px auto;
        text-align: center;
        position: relative;
      }
      .dot {
        cursor: pointer;
        height: 15px;
        width: 15px;
        margin: 0 2px;
        background-color: #ccc;
        border-radius: 50%;
        display: inline-block;
      }
      .active,
      .dot:hover {
        background-color: #717171;
      }

      /* table of contents */
      /* There are no uploads in the feed */
      /* Failed to get response, UC id, feed (errors) */
      div.yt-ids, div.no-uploads, div.no-data {
        margin: 10px;
        padding: 5px;
      }
    </style>
<script type="text/javascript">
  function showPopup(event) {
    event.target.children[0].classList.toggle("show");
  }
  function openWindow(videoId) {
    let url = "https://www.youtube.com/embed/" + videoId;
    let width = screen.width / 1.5;
    let height = screen.height / 1.5;
    var left = (screen.width - width) / 2;
    var top = (screen.height - height) / 4;
    var newWindow = window.open(url, "center window",
      "resizable = yes, width=" + width + ", height=" + height + ", top=" + top + ", left=" + left);
  }
</script>
<script type="text/javascript">
  var currentImg = 0;

  function changeSlide(videoId, n) {
    const elem = document.getElementById(videoId);
    var imgs = elem.getElementsByClassName('slider-img');
    var dots = elem.getElementsByClassName('dot');
    //var imgs = elem.querySelectorAll('.slider-img');
    //var dots = elem.querySelectorAll('.dot');

    for (var i = 0; i < imgs.length; i++) {
      imgs[i].style.opacity = 0;
      dots[i].className = dots[i].className.replace(' active', '');
    }

    currentImg = (currentImg + 1) % imgs.length;

    if (n != undefined) {
      currentImg = n;
    }
    imgs[currentImg].style.opacity = 1;
    dots[currentImg].className += ' active';
  }
</script>
  </head>
  <body>
"""

html_end = """
  </body>
</html>
"""

# hqdefault.jpg original: 480x360, 4:3
# hq[number].jpg original: 480x360, 4:3
slider_block = """
<div class="slider-container" id="{video_id}">
  <div class="slider">
    <img class="slider-img" src="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" width="320" height="240" />
    <img class="slider-img" src="https://i.ytimg.com/vi/{video_id}/hq1.jpg" width="320" height="240" />
    <img class="slider-img" src="https://i.ytimg.com/vi/{video_id}/hq2.jpg" width="320" height="240" />
    <img class="slider-img" src="https://i.ytimg.com/vi/{video_id}/hq3.jpg" width="320" height="240" />
  </div>
  <div class="navigation-buttons">
    <span class="dot active" onclick="changeSlide('{video_id}', 0)"></span>
    <span class="dot" onclick="changeSlide('{video_id}', 1)"></span>
    <span class="dot" onclick="changeSlide('{video_id}', 2)"></span>
    <span class="dot" onclick="changeSlide('{video_id}', 3)"></span>
  </div>
</div>
"""
