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
    })
    .catch((error) => {
      console.log(error);
    });
}
