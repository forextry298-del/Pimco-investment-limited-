(function () {
  const teams = {
    Christmas: {
      title: "🎄 Christmas Offers",
      decor: "🎄 🎁 ❄️",
      offers: [
        {price:1000000,income:750000,days:2,hours:8},
        {price:1000,income:400,days:4,hours:4},
        {price:50000,income:25000,days:4,hours:0.5},
        {price:5000,income:3000,days:3,hours:24},
        {price:20000,income:7500,days:4,hours:72}
      ]
    },
    BlackNovember: {
      title: "🖤 Black November Offers",
      decor: "🍌 🐔 🖤",
      offers: [
        {price:4000,income:3000,days:2,hours:7},
        {price:500,income:300,days:4,hours:4},
        {price:100000,income:70000,days:10,hours:24},
        {price:49000,income:26000,days:25,hours:216}
      ]
    }
  };

  const storageKey = "pimcoSeasonalOfferEnds_v1";
  const teamKey = "pimcoSeasonalOfferTeam_v1";

  const popup = document.getElementById("seasonalOffersPopup");
  const title = document.getElementById("seasonalTitle");
  const decor = document.getElementById("seasonalDecor");
  const list = document.getElementById("seasonalOffersList");
  const close = document.getElementById("seasonalClose");

  if (!popup || !title || !decor || !list || !close) return;

  let endTimes = {};
  try {
    endTimes = JSON.parse(localStorage.getItem(storageKey) || "{}");
  } catch (e) {
    endTimes = {};
  }

  let team = localStorage.getItem(teamKey) || "Christmas";
  if (!teams[team]) team = "Christmas";

  function initializeTeam(name) {
    const now = Date.now();

    teams[name].offers.forEach((offer, index) => {
      const key = name + "_" + index;

      if (!endTimes[key]) {
        endTimes[key] = now + offer.hours * 3600000;
      }
    });

    localStorage.setItem(storageKey, JSON.stringify(endTimes));
  }

  function allExpired(name) {
    return teams[name].offers.every((offer, index) =>
      Date.now() >= endTimes[name + "_" + index]
    );
  }

  function formatTime(ms) {
    if (ms <= 0) return "Expired. Please try again later.";

    const total = Math.floor(ms / 1000);
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const seconds = total % 60;

    return hours + "h " + minutes + "m " + seconds + "s";
  }

  function render() {
    const data = teams[team];

    title.textContent = data.title;
    decor.textContent = data.decor;

    popup.className = "seasonal-popup " +
      (team === "Christmas" ? "christmas-theme" : "november-theme");

    list.innerHTML = "";

    data.offers.forEach((offer, index) => {
      const key = team + "_" + index;
      const item = document.createElement("div");
      item.className = "seasonal-offer";

      const price = document.createElement("p");
      price.textContent = "Price: UGX " + offer.price.toLocaleString();

      const income = document.createElement("p");
      income.textContent = "Daily income: UGX " + offer.income.toLocaleString();

      const duration = document.createElement("p");
      duration.textContent = "Duration: " + offer.days + " days";

      const timer = document.createElement("p");
      timer.className = "seasonal-countdown";
      timer.id = "seasonalTimer_" + index;
      timer.textContent = formatTime(endTimes[key] - Date.now());

      item.append(price, income, duration, timer);
      list.appendChild(item);
    });
  }

  function updateTimers() {
    if (allExpired(team)) {
      team = team === "Christmas" ? "BlackNovember" : "Christmas";
      localStorage.setItem(teamKey, team);
      initializeTeam(team);
      render();
    }

    teams[team].offers.forEach((offer, index) => {
      const timer = document.getElementById("seasonalTimer_" + index);
      const key = team + "_" + index;

      if (timer) {
        timer.textContent = formatTime(endTimes[key] - Date.now());
      }
    });
  }

  initializeTeam(team);
  render();

  if (!sessionStorage.getItem("seasonalPopupClosed")) {
    popup.style.display = "flex";
  }

  close.addEventListener("click", function () {
    popup.style.display = "none";
    sessionStorage.setItem("seasonalPopupClosed", "1");
  });

  setInterval(updateTimers, 1000);
})();
