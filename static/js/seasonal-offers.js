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


  function createSeasonalPopup() {
    if (document.getElementById("seasonal-popup")) {
      return;
    }

    const popup = document.createElement("div");
    popup.id = "seasonal-popup";

    popup.innerHTML = `
      <div class="seasonal-popup-backdrop"></div>
      <section class="seasonal-popup-panel">
        <button class="seasonal-close"
          type="button">×</button>

        <h2>Seasonal Special Offers</h2>

        <p class="seasonal-intro">
          Limited offers with individual countdowns
        </p>

        <div class="seasonal-tabs">
          <button type="button"
            data-team="Christmas">Christmas</button>

          <button type="button"
            data-team="Black November">
            Black November
          </button>
        </div>

        <div class="seasonal-popup-cards"></div>
      </section>
    `;

    document.body.appendChild(popup);

    const cards = popup.querySelector(
      ".seasonal-popup-cards"
    );

    function showTeam(team) {
      cards.replaceChildren();

      offers
        .filter(offer => offer.team === team)
        .forEach(offer => {
          cards.appendChild(createOfferCard(offer));
        });

      popup.querySelectorAll(
        ".seasonal-tabs button"
      ).forEach(button => {
        button.classList.toggle(
          "selected",
          button.dataset.team === team
        );
      });
    }

    popup.querySelectorAll(
      ".seasonal-tabs button"
    ).forEach(button => {
      button.addEventListener("click", () => {
        showTeam(button.dataset.team);
      });
    });

    popup.querySelector(".seasonal-close")
      .addEventListener("click", () => popup.remove());

    popup.querySelector(".seasonal-popup-backdrop")
      .addEventListener("click", () => popup.remove());

    showTeam("Christmas");
  }


  document.addEventListener("DOMContentLoaded", function () {
    const path = window.location.pathname;

    if (path === "/" || path.endsWith("/home")) {
      createSeasonalPopup();
    }
  });


  function addSeasonalEquipmentCards() {
    const equipment = document.querySelector(
      ".products, .equipment, .plans, .product-grid"
    );

    if (!equipment) return;

    offers.forEach(function (offer) {
      const card = createOfferCard(offer);
      card.classList.add("seasonal-product-card");
      equipment.appendChild(card);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (window.location.pathname.includes("equipment")) {
      addSeasonalEquipmentCards();
    }
  });

