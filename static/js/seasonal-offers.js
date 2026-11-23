(function () {
  "use strict";

  const offers = [
    {
      id: 21,
      name: "Christmas Premium",
      price: 1000000,
      daily: 750000,
      days: 2,
      hours: 8,
      team: "Christmas",
      start: "2026-11-25T00:00:00+03:00",
      image: "/static/images/seasonal/christmas-tree.jpg"
    },
    {
      id: 22,
      name: "Christmas Mini",
      price: 1000,
      daily: 400,
      days: 4,
      hours: 4,
      team: "Christmas",
      start: "2026-11-25T00:00:00+03:00",
      image: "/static/images/seasonal/gift-boxes.jpg"
    },
    {
      id: 23,
      name: "Christmas Gift",
      price: 50000,
      daily: 25000,
      days: 4,
      hours: 0.5,
      team: "Christmas",
      start: "2026-11-25T00:00:00+03:00",
      image: "/static/images/seasonal/christmas-gifts.jpg"
    },
    {
      id: 24,
      name: "Christmas Box",
      price: 5000,
      daily: 3000,
      days: 3,
      hours: 24,
      team: "Christmas",
      start: "2026-11-25T00:00:00+03:00",
      image: "/static/images/seasonal/gift-boxes.jpg"
    },
    {
      id: 25,
      name: "Christmas Family",
      price: 20000,
      daily: 7500,
      days: 4,
      hours: 72,
      team: "Christmas",
      start: "2026-11-25T00:00:00+03:00",
      image: "/static/images/seasonal/christmas-tree.jpg"
    },
    {
      id: 26,
      name: "Black November Hen",
      price: 4000,
      daily: 3000,
      days: 2,
      hours: 7,
      team: "Black November",
      start: "2026-12-26T00:00:00+03:00",
      image: "/static/images/seasonal/hen.jpg"
    },
    {
      id: 27,
      name: "Black November Mini",
      price: 500,
      daily: 300,
      days: 4,
      hours: 4,
      team: "Black November",
      start: "2026-12-26T00:00:00+03:00",
      image: "/static/images/seasonal/hen.jpg"
    },
    {
      id: 28,
      name: "Black November Premium",
      price: 100000,
      daily: 70000,
      days: 10,
      hours: 24,
      team: "Black November",
      start: "2026-12-26T00:00:00+03:00",
      image: "/static/images/seasonal/hen.jpg"
    },
    {
      id: 29,
      name: "Black November Matooke",
      price: 49000,
      daily: 26000,
      days: 25,
      hours: 216,
      team: "Black November",
      start: "2026-12-26T00:00:00+03:00",
      image: "/static/images/seasonal/matooke.jpg"
    }
  ];

  window.SEASONAL_OFFERS = offers;
  console.log("Seasonal offers loaded:", offers.length);
})();

const offers = window.SEASONAL_OFFERS;

  function getOfferStatus(offer) {
    const now = Date.now();
    const start = new Date(offer.start).getTime();
    const end = start + offer.hours * 3600000;

    if (now < start) {
      return {
        state: "coming",
        remaining: start - now
      };
    }

    if (now >= end) {
      return {
        state: "expired",
        remaining: 0
      };
    }

    return {
      state: "active",
      remaining: end - now
    };
  }

  function formatCountdown(milliseconds) {
    const seconds = Math.max(
      0,
      Math.floor(milliseconds / 1000)
    );

    const days = Math.floor(seconds / 86400);
    const hours = Math.floor(
      (seconds % 86400) / 3600
    );
    const minutes = Math.floor(
      (seconds % 3600) / 60
    );
    const secs = seconds % 60;

    const time = [hours, minutes, secs]
      .map(value => String(value).padStart(2, "0"))
      .join(":");

    return days > 0 ? days + "d " + time : time;
  }


  function createOfferCard(offer) {
    const card = document.createElement("article");
    card.className = "seasonal-offer-card";
    card.dataset.seasonalId = offer.id;

    const image = document.createElement("img");
    image.className = "seasonal-photo";
    image.src = offer.image;
    image.alt = offer.name;
    image.loading = "lazy";

    const info = document.createElement("div");
    info.className = "seasonal-offer-info";

    const title = document.createElement("h3");
    title.textContent = offer.name;

    const price = document.createElement("p");
    price.textContent = "Price: UGX " +
      offer.price.toLocaleString();

    const income = document.createElement("p");
    income.textContent = "Projected daily income: UGX " +
      offer.daily.toLocaleString();

    const duration = document.createElement("p");
    duration.textContent = "Duration: " +
      offer.days + " days";

    const status = document.createElement("p");
    status.className = "seasonal-status";

    const timer = document.createElement("div");
    timer.className = "seasonal-timer";

    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/purchase/" + offer.id;

    const button = document.createElement("button");
    button.type = "submit";
    button.className = "seasonal-buy";

    form.appendChild(button);

    info.append(
      title,
      price,
      income,
      duration,
      status,
      timer,
      form
    );

    card.append(image, info);

    function updateCard() {
      const result = getOfferStatus(offer);

      if (result.state === "coming") {
        status.textContent = "Coming on";
        timer.textContent =
          formatCountdown(result.remaining);
        button.textContent = "Coming soon";
        button.disabled = true;
      } else if (result.state === "expired") {
        status.textContent =
          "Expired. Please try again later.";
        timer.textContent = "";
        button.textContent = "Offer expired";
        button.disabled = true;
      } else {
        status.textContent = "Offer expires in";
        timer.textContent =
          formatCountdown(result.remaining);
        button.textContent = "Buy offer";
        button.disabled = false;
      }
    }

    updateCard();
    setInterval(updateCard, 1000);

    return card;
  }



  function addSeasonalEquipmentCards() {
    const equipment = document.querySelector(".pimco-plan-grid");
    if (!equipment) return;

    offers.forEach(function (offer) {
      let card = equipment.querySelector(
        '[data-product-id="' + offer.id + '"]'
      );

      if (!card) {
        card = createOfferCard(offer);
        card.classList.add("seasonal-product-card");
        equipment.appendChild(card);
        return;
      }

      card.dataset.seasonalId = offer.id;
      card.classList.add("seasonal-product-card");

      const image = card.querySelector("img");
      if (image) {
        image.src = offer.image;
        image.alt = offer.name;
      }

      const body = card.querySelector(".pimco-plan-body");
      if (!body) return;

      let status = card.querySelector(".seasonal-live-status");
      let timer = card.querySelector(".seasonal-live-timer");

      if (!status) {
        status = document.createElement("div");
        status.className = "seasonal-live-status";
        status.style.cssText =
          "font-size:11px;font-weight:800;color:#087f46;margin:8px 0 3px";
        const label = body.querySelector(".pimco-plan-label");
        if (label) label.insertAdjacentElement("afterend", status);
        else body.prepend(status);
      }

      if (!timer) {
        timer = document.createElement("div");
        timer.className = "seasonal-live-timer";
        timer.style.cssText =
          "font-size:17px;font-weight:900;color:#087f46;" +
          "background:#e7fff0;border:1px solid #55d98a;" +
          "border-radius:9px;padding:8px;margin:4px 0 9px";
        status.insertAdjacentElement("afterend", timer);
      }

      function updateLiveTimer() {
        const result = getOfferStatus(offer);
        const button = card.querySelector("form button");

        if (result.state === "coming") {
          status.textContent = "OFFER STARTS IN";
          timer.textContent = formatCountdown(result.remaining);
          if (button) button.disabled = true;
        } else if (result.state === "active") {
          status.textContent = "● LIVE — EXPIRES IN";
          timer.textContent = formatCountdown(result.remaining);
          if (button) button.disabled = false;
        } else {
          status.textContent = "OFFER ENDED";
          timer.textContent = "Expired. Please try again later.";
          timer.style.fontSize = "12px";
          if (button) button.disabled = true;
        }
      }

      updateLiveTimer();

      if (!card.dataset.timerStarted) {
        card.dataset.timerStarted = "yes";
        setInterval(updateLiveTimer, 1000);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (window.location.pathname.includes("equipment")) {
      addSeasonalEquipmentCards();
    }
  });

  function openSeasonalDetails(offer) {
    const old = document.getElementById("eastridge-countdown");
    if (old) old.remove();

    const modal = document.createElement("div");
    modal.id = "eastridge-countdown";
    modal.style.cssText =
      "position:fixed;inset:0;z-index:99999;background:#07152bdd;" +
      "display:flex;align-items:center;justify-content:center;padding:15px";

    const box = document.createElement("section");
    box.style.cssText =
      "background:white;border-radius:18px;padding:20px;" +
      "width:100%;max-width:360px;color:#123d76";

    const close = document.createElement("button");
    close.textContent = "Close";

    const heading = document.createElement("h2");
    heading.textContent = offer.name;

    const status = document.createElement("p");
    const timer = document.createElement("h2");
    timer.style.color = "#078e89";

    const note = document.createElement("p");
    note.textContent = "Projected income only; not guaranteed.";

    box.append(close, heading, status, timer, note);
    modal.appendChild(box);
    document.body.appendChild(modal);

    close.onclick = function () { modal.remove(); };
    modal.onclick = function (e) {
      if (e.target === modal) modal.remove();
    };

    function refresh() {
      if (!modal.isConnected) return;
      const result = getOfferStatus(offer);

      if (result.state === "coming") {
        status.textContent = "Offer starts in:";
        timer.textContent = formatCountdown(result.remaining);
      } else if (result.state === "expired") {
        status.textContent = "Expired. Please try again later.";
        timer.textContent = "";
      } else {
        status.textContent = "Offer expires in:";
        timer.textContent = formatCountdown(result.remaining);
      }
    }

    refresh();
    const clock = setInterval(function () {
      if (!modal.isConnected) {
        clearInterval(clock);
        return;
      }
      refresh();
    }, 1000);
  }

  document.addEventListener("click", function (event) {
    const card = event.target.closest("[data-seasonal-id]");
    if (!card || event.target.closest("form, button")) return;

    const offer = offers.find(function (item) {
      return String(item.id) === card.dataset.seasonalId;
    });

    if (offer) openSeasonalDetails(offer);
  });
