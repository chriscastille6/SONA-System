/**
 * EXT-AM4 goals-refs — UI aligned with Psychological Assessment Library instruments
 * (e.g. loss-assessment-inventory/index.html: horizontal .likert-scale, hidden radio + label).
 * POST /api/studies/<uuid>/submit/ uses X-CSRFToken (CSRF_COOKIE_HTTPONLY).
 */
/** @type {{ v: number, short: string }[]} */
const LIKERT_7_LIKELIHOOD = [
  { v: 1, short: "Extremely unlikely" },
  { v: 2, short: "Very unlikely" },
  { v: 3, short: "Unlikely" },
  { v: 4, short: "Neutral" },
  { v: 5, short: "Likely" },
  { v: 6, short: "Very likely" },
  { v: 7, short: "Extremely likely" },
];

function getCsrfToken() {
  const el = document.querySelector("[name=csrfmiddlewaretoken]");
  return el ? el.value : "";
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

class ExtAM4Assessment {
  constructor() {
    this.currentPhase = 1;
    this.totalPhases = 4;
    this.sessionId = this.makeSessionId();
    this.items = [
      { id: "extra_effort", label: "Put in extra effort on their own deliverables" },
      { id: "share_info", label: "Share information with teammates to improve joint outcomes" },
      { id: "errors_uncorrected", label: "Let errors go uncorrected when it suits them" },
      { id: "withhold_info", label: "Withhold useful information from peers" },
      { id: "spread_negative", label: "Spread negative information about a colleague to others" },
      {
        id: "sabotage",
        label:
          "Deliberately set traps or create situations so that a highly effective coworker would fail or look bad",
      },
      { id: "favorable_appraisal", label: "Receive a favorable performance appraisal from their supervisor" },
    ];
    this.vignettes = {
      low_abundance: {
        culture:
          "resources exist but are often hidden or underused and can be unlocked - and that the organization is committed to reallocating or sharing resources so that success depends on people cooperating and pooling effort",
        amoral:
          "direct and straightforward - someone who does not play politics, avoids flattering others or cutting corners to get ahead, and believes in being transparent about the real reasons for doing things",
      },
      high_abundance: {
        culture:
          "resources exist but are often hidden or underused and can be unlocked - and that the organization is committed to reallocating or sharing resources so that success depends on people cooperating and pooling effort",
        amoral:
          "someone who believes the best way to handle people is to tell them what they want to hear; Alex is willing to flatter others and cut corners when it helps get ahead, and does not think you need to reveal the real reason for doing something unless it is useful",
      },
      low_scarcity: {
        culture:
          "there are not enough resources to do the right thing, and that view is used to justify short-term or wasteful decisions; resources and rewards are limited (e.g., only one person can get the promotion, or the bonus pool is fixed so one person's gain is another's loss)",
        amoral:
          "direct and straightforward - someone who does not play politics, avoids flattering others or cutting corners to get ahead, and believes in being transparent about the real reasons for doing things",
      },
      high_scarcity: {
        culture:
          "there are not enough resources to do the right thing, and that view is used to justify short-term or wasteful decisions; resources and rewards are limited (e.g., only one person can get the promotion, or the bonus pool is fixed so one person's gain is another's loss)",
        amoral:
          "someone who believes the best way to handle people is to tell them what they want to hear; Alex is willing to flatter others and cut corners when it helps get ahead, and does not think you need to reveal the real reason for doing something unless it is useful",
      },
    };
    this.data = {
      session_id: this.sessionId,
      study_slug: typeof STUDY_SLUG !== "undefined" ? STUDY_SLUG : "goals-refs",
      started_at: new Date().toISOString(),
      demographics: {},
      condition: null,
      responses: {},
    };
  }

  init() {
    this.wireButtons();
    this.renderItems();
    this.updateProgress();
  }

  makeSessionId() {
    return `extam4_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
  }

  wireButtons() {
    document.getElementById("consent-continue").addEventListener("click", () => {
      this.showPhase(2);
    });

    document.getElementById("consent-decline").addEventListener("click", () => {
      alert("Thank you for your time. You can now close this page.");
      window.location.href = "/studies/";
    });

    document.getElementById("demographics-back").addEventListener("click", () => this.showPhase(1));
    document.getElementById("demographics-continue").addEventListener("click", () => {
      this.data.demographics = {
        age_range: document.getElementById("age-range").value || null,
        gender: document.getElementById("gender").value || null,
      };
      this.setConditionAndVignette();
      this.showPhase(3);
    });

    document.getElementById("vignette-back").addEventListener("click", () => this.showPhase(2));
    document.getElementById("ratings-form").addEventListener("submit", (event) => this.submit(event));

    document.getElementById("items-container").addEventListener("change", () => {
      this.updateSubmitEnabled();
    });
  }

  renderItems() {
    const container = document.getElementById("items-container");
    container.innerHTML = "";
    this.items.forEach((item, idx) => {
      const n = idx + 1;
      const rowId = `item-${item.id}`;
      const optionsHtml = LIKERT_7_LIKELIHOOD.map(({ v, short }) => {
        const inputId = `${rowId}-v${v}`;
        return `<div class="likert-option">
          <input type="radio" id="${inputId}" name="${item.id}" value="${v}" required>
          <label for="${inputId}">
            <div class="font-semibold">${v}</div>
            <div class="text-xs mt-1 text-gray-600 leading-tight">${escapeHtml(short)}</div>
          </label>
        </div>`;
      }).join("");

      const block = document.createElement("div");
      block.className = "border-b border-gray-200 pb-6 mb-6 last:border-b-0 last:mb-0";
      block.innerHTML = `
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-semibold text-sm mt-1" aria-hidden="true">${n}</div>
          <div class="flex-1 min-w-0">
            <label class="block text-gray-900 font-medium mb-3">${escapeHtml(item.label)} <span class="text-red-600" aria-hidden="true">*</span></label>
            <div class="likert-scale" role="group" aria-labelledby="${rowId}-legend">
              <span id="${rowId}-legend" class="sr-only">Likelihood 1 to 7 for item ${n}</span>
              ${optionsHtml}
            </div>
          </div>
        </div>
      `;
      container.appendChild(block);
    });
    this.updateSubmitEnabled();
  }

  allItemsAnswered() {
    return this.items.every((item) => {
      const el = document.querySelector(`input[name="${item.id}"]:checked`);
      return el != null;
    });
  }

  updateSubmitEnabled() {
    const btn = document.getElementById("ratings-submit");
    if (btn) btn.disabled = !this.allItemsAnswered();
  }

  setConditionAndVignette() {
    const params = new URLSearchParams(window.location.search);
    const amoral = (params.get("amoral") || "").toLowerCase();
    const culture = (params.get("culture") || "").toLowerCase();
    let key = null;
    if ((amoral === "low" || amoral === "high") && (culture === "abundance" || culture === "scarcity")) {
      key = `${amoral}_${culture}`;
    } else {
      const keys = Object.keys(this.vignettes);
      key = keys[Math.floor(Math.random() * keys.length)];
    }
    const vignette = this.vignettes[key];
    this.data.condition = key;
    document.getElementById("vignette-text").innerHTML =
      `Alex works in an organization whose culture is that <strong>${vignette.culture}</strong>. ` +
      `Colleagues describe Alex as <strong>${vignette.amoral}</strong>.`;
  }

  showPhase(phase) {
    const ids = ["consent-phase", "demographics-phase", "vignette-phase", "debrief-phase"];
    ids.forEach((id) => document.getElementById(id).classList.add("hidden"));
    document.getElementById(ids[phase - 1]).classList.remove("hidden");
    this.currentPhase = phase;
    this.updateProgress();
    window.scrollTo(0, 0);
  }

  updateProgress() {
    const pct = (this.currentPhase / this.totalPhases) * 100;
    document.getElementById("main-progress").style.width = `${pct}%`;
    document.getElementById("phase-indicator").textContent = `Step ${this.currentPhase} of ${this.totalPhases}`;
  }

  collectResponses() {
    this.items.forEach((item) => {
      const checked = document.querySelector(`input[name="${item.id}"]:checked`);
      this.data.responses[item.id] = checked ? Number.parseInt(checked.value, 10) : null;
    });
  }

  async submit(event) {
    event.preventDefault();
    if (!this.allItemsAnswered()) {
      alert("Please select a response for every item.");
      return;
    }
    this.collectResponses();
    this.data.completed_at = new Date().toISOString();
    this.data.user_agent = navigator.userAgent;

    const csrfToken = getCsrfToken();
    if (!csrfToken) {
      console.error("Missing CSRF token (csrfmiddlewaretoken). Reload the page and try again.");
      alert(
        "This page could not verify browser security (CSRF). Please reload the page and try again.",
      );
      return;
    }

    try {
      const response = await fetch(`/api/studies/${STUDY_ID}/submit/`, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(this.data),
      });

      const bodyText = await response.text();
      let result = null;
      try {
        result = bodyText ? JSON.parse(bodyText) : null;
      } catch {
        result = null;
      }

      if (!response.ok) {
        const msg = (result && result.error) || bodyText || response.statusText;
        console.error("Submission failed:", response.status, msg);
        throw new Error(`HTTP ${response.status}: ${msg}`);
      }

      this.data.response_id = result.response_id || null;
      this.showPhase(4);
    } catch (error) {
      console.error("Submission failed:", error);
      alert(
        "There was a problem submitting your responses. Please try again. If it continues, reload the page.",
      );
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const app = new ExtAM4Assessment();
  app.init();
});
