function sendMoney(action) {
  console.log("Send Money");
  fetch("transact", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ action }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      document.getElementById("balance").innerText = data["new_balance"];
      // Handle the response data
    })
    .catch((error) => {
      console.log(error);
      // Handle any errors that occur
    });
}
