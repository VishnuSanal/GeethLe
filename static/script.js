window.addEventListener("DOMContentLoaded", function (e) {
  var spotify_url = "";
  var input_link = "";

  this.document
    .getElementById("search_button")
    .addEventListener("click", function () {
      input_link = document.getElementById("search_input").value.trim();

      text = input_link.replace("https://geethle.onrender.com/", "").trim();

      if (text === "") {
        alert("NoNo!");
        return;
      }

      $("#search_button").hide();
      $(".loader").show();

      $.ajax({
        type: "GET",
        url: "/get_thumb_from_query/" + text,
        dataType: "json",
        contentType: "application/json;charset=UTF-8",
        success: function (data) {
          console.log(data.frame_url);

          spotify_url = data.redirect_url;

          var image = new Image();
          image.onload = function () {
            document.getElementById("album_art").setAttribute("src", this.src);

            $("#album_art").show();

            $(".container").hide();
            $(".subtitle").hide();
            $(".description").hide();
            $(".loader").hide();

            $("#button_copy").show();
            $("#button_go").show();
          };

          image.src = data.frame_url;
        },
      });
    });

  this.document
    .getElementById("search_input")
    .addEventListener("focus", function () {
      document.getElementById("search_input").value =
        "https://geethle.onrender.com/";
    });

  this.document
    .getElementById("button_copy")
    .addEventListener("click", function () {
      console.log(input_link);

      if (input_link != "") {
        navigator.clipboard.writeText(input_link);
        this.value = "Done";
      }
    });

  this.document
    .getElementById("button_go")
    .addEventListener("click", function () {
      console.log(spotify_url);

      if (spotify_url != "") {
        window.open(spotify_url, "_blank").focus();
        this.value = "Done"
      }
    });
});
