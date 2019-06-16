<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>SD Computer Vision Service</title>
  <style>
    body {
      font-family: 'Open Sans', 'Arial', sans-serif;
      color: #444444;
      font-size: 1.1rem;
      background-color: #fefefe;
    }

    code {
      font-family: 'Fire Mono', monospace;
      font-size: 1rem
    }

    .content {
      display: flex;
      justify-content: center;
    }

    .blue {
      color: rgb(92, 92, 92)
    }

    .green {
      color: rgb(16, 153, 130)
    }

    .purple {
      color: #6a25c4
    }

    .container {
      max-width: 950px
    }

    .margin-left {
      margin-left: 40px
    }

    .margin-bottom {
      margin-bottom: 10px
    }

    .margin-top {
      margin-top: 10px
    }

    .service {
      border: 1px solid rgb(230, 230, 230);
      padding: 25px;
      margin-bottom: 25px;
    }
  </style>
  <link href="https://fonts.googleapis.com/css?family=Fira+Mono|Open+Sans&display=swap" rel="stylesheet">
</head>

<body>
  <div class="content">
    <div class="container">
      <h1>SceneDetection Computer Vision Service</h1>

      <h2>Available Services</h2>

      <div class="service">
        <div class="margin-bottom"><b class="blue">Service Name</b> : Object Detection</div>
        <div class="margin-bottom"><b class="blue">Endpoint</b> : <code>
            <b class="green">/start-object-detection/&lt;video_id&gt;/&lt;progress_endpoint&gt;</b>
        </code>
        </div>
        <div class="margin-bottom"><b class="blue">Arguments</b> :
          <div class="margin-left">
            <div class="margin-top"><code><b class="green"> video_id</b></code> :
              <code><b class="purple">_id</b></code>
              field of the
              document of the video in <code class="purple"> <b> videos </b></code> collection in
              database, that is going to be used in detection.</div>
            <div class="margin-top"><code><b class="green"> progress_endpoint</b></code> : An optional argument, which
              will be used for HTTP GET request to sendprogress information. This request will be sent
              to an endpoint which is a combination of <code><b class="green">progress_endpoint</b></code>,
              progress information (percentage) and <code><b class="green">video_id</b></code> which looks like:
              <code><b class="green">&lt;progress_endpoint&gt;/&lt;video_id&gt;/&lt;progress&gt;</b></code>.
            </div>
          </div>
        </div>
        <div class="margin-bottom"><b class="blue">Response Fields</b> :
          <div class="margin-left">
            <div class="margin-top"><code><b class="green">status</b></code> :
              <code><b class="green">OK</b></code> if no errors occured, otherwise
              <code><b class="green">ERROR</b></code></div>
            <div class="margin-top"><code><b class="green">operation_id</b></code> : An ID which can be later used to
              terminate detection.
            </div>
          </div>
        </div>
        <div><b class="blue">Description</b> : With this service, objects can be detected in videos. With supplied
          arguments, objects will be detected and for every frame, detected objects will be inserted into <code
            class="purple"> <b> detected_objects</b></code> collection in database.
          Inserted documents have a shape which looks like: <code class="purple"> <b>
              {"class": int, "confidence":float, "x":float,
              "y":float, "w":float, "h":float, "frame_no":int, "video_id":ObjectId}
          </b></code>. Also, service will update
          <code class="purple"><b>object_detection_status</b></code> and <code
            class="purple"><b>object_detection_progress</b></code> fields of the video document while detecting
          objects. Before detection, <code class="purple"><b>object_detection_status</b></code> field should be
          either <code class="purple"> <b>NOT_STARTED</b></code> or <code class="purple"> <b>ERROR</b></code>, or
          service won't start detection. When detection starts <code
            class="purple"><b>object_detection_status </b></code> will be updated to <code
            class="purple"><b>STARTED</b></code> and when it is completed it will be updated to <code
            class="purple"><b>COMPLETED</b></code>. While detection occurs, <code
            class="purple"> <b>object_detection_progress</b></code> will be updated with calculated progress percentage.
        </div>
      </div>

      <div class="service">
        <div class="margin-bottom"><b class="blue">Service Name</b> : Termination Object Detection</div>
        <div class="margin-bottom"><b class="blue">Endpoint</b> : <code>
              <b class="green">/terminate-object-detection/&lt;operation_id&gt;</b>
          </code>
        </div>
        <div class="margin-bottom"><b class="blue">Arguments</b> :
          <div class="margin-left">
            <div class="margin-top"><code><b class="green">operation_id</b></code> :
              This ID can be found in the response of Object Detection service.</div>
          </div>
        </div>
        <div class="margin-bottom"><b class="blue">Response Fields</b> :
          <div class="margin-left">
            <div class="margin-top"><code><b class="green">status</b></code> :
              <code><b class="green">OK</b></code> if no errors occured, otherwise
              <code><b class="green">ERROR</b></code></div>
          </div>
        </div>
        <div><b class="blue">Description</b> : Detection operation with ID
          <code><b class="green">operation_id</b></code> will be terminated. <code
            class="purple"><b>object_detection_status </b></code> will be updated to <code
            class="purple"><b>ERROR</b></code>. <code class="purple"> <b>object_detection_progress</b></code> field
          won't be updated. Changes made to <code class="purple"> <b> detected_objects</b></code> collection will be
          reverted.
        </div>
      </div>
    </div>
  </div>
</body>

</html>