window.addEventListener("DOMContentLoaded", function (e) {
  this.document
    .getElementById("search_button")
    .addEventListener("click", function () {
      text = document.getElementById("search_input").value;

      if (
        text.trim() === "" ||
        text.trim() == "https://geethle.onrender.com/"
      ) {
        alert("NoNo!")
        return;
      }
    });

  this.document
    .getElementById("search_input")
    .addEventListener("focus", function () {
      document.getElementById("search_input").value =
        "https://geethle.onrender.com/"
    });
});
