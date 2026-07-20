/**
 * Wave 1 survey engine: consent → CANDIDATE questions → items → finalize.
 *
 * Research payload contains:
 *   - candidate_id (16-char)
 *   - wave, timestamps, item responses
 * Explicitly excludes:
 *   - survey_code (SONA only)
 *   - raw security answers
 *   - email / name / student ID
 */
(function () {
  "use strict";

  /** Replace these before IRB fielding. */
  var STUDY = {
    title: "Longitudinal Study — Wave 1",
    irbProtocol: "IRB-XXXX-YYYY",
    wave: 1,
    formBUrl: "../form_b/index.html",
    sona: {
      baseCreditUrl:
        "https://YOUR-SCHOOL.sona-systems.com/redirect_credit.aspx",
      experimentId: "XXX",
      creditToken: "YYY",
    },
  };

  var state = {
    surveyCode: "",
    candidateId: "",
    consented: false,
    answers: {},
    startedAt: null,
    completedAt: null,
  };

  var $ = function (sel) {
    return document.querySelector(sel);
  };
  var $$ = function (sel) {
    return Array.prototype.slice.call(document.querySelectorAll(sel));
  };

  function showPanel(id) {
    $$(".panel").forEach(function (el) {
      el.hidden = el.id !== id;
    });
    window.scrollTo(0, 0);
  }

  function setStatus(msg, isError, which) {
    var id =
      which === "complete"
        ? "#status-line-complete"
        : which === "survey"
          ? "#status-line-survey"
          : "#status-line-candidate";
    var el = $(id);
    if (!el) return;
    el.textContent = msg || "";
    el.classList.toggle("error", !!isError);
  }

  function collectLikert() {
    var data = {};
    $$("[data-item]").forEach(function (fieldset) {
      var key = fieldset.getAttribute("data-item");
      var checked = fieldset.querySelector('input[type="radio"]:checked');
      if (checked) data[key] = Number(checked.value);
    });
    return data;
  }

  function allLikertAnswered() {
    return $$("[data-item]").every(function (fieldset) {
      return !!fieldset.querySelector('input[type="radio"]:checked');
    });
  }

  /**
   * Primary research record — no SONA code, no raw CANDIDATE answers.
   */
  function buildResearchRecord() {
    return {
      schema: "longitudinal-candidate/v1",
      study_irb: STUDY.irbProtocol,
      wave: STUDY.wave,
      candidate_id: state.candidateId,
      started_at: state.startedAt,
      completed_at: state.completedAt,
      responses: state.answers,
      // Intentional absences (documented for auditors):
      // survey_code: never
      // email: never
      // security_answers: never
    };
  }

  function downloadJson(record) {
    var blob = new Blob([JSON.stringify(record, null, 2)], {
      type: "application/json",
    });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download =
      "wave1_" + record.candidate_id + "_" + Date.now() + ".json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  }

  function init() {
    state.surveyCode = SonaPassthrough.captureSurveyCode();
    state.startedAt = new Date().toISOString();

    var badge = $("#sona-badge");
    if (badge) {
      if (state.surveyCode) {
        badge.textContent =
          "SONA credit code captured (held in session only — not stored with answers).";
        badge.classList.add("ok");
      } else {
        badge.textContent =
          "No survey_code in URL. Credit redirect will be skipped (preview / pilot mode).";
        badge.classList.add("warn");
      }
    }

    $("#btn-consent-yes").addEventListener("click", function () {
      state.consented = true;
      showPanel("panel-candidate");
    });

    $("#btn-consent-no").addEventListener("click", function () {
      showPanel("panel-declined");
    });

    $("#candidate-form").addEventListener("submit", function (evt) {
      evt.preventDefault();
      setStatus("");
      try {
        var answers = {
          motherMaidenInitials: $("#q-maiden").value,
          birthDayOfMonth: $("#q-birthday").value,
          childhoodStreetInitials: $("#q-street").value,
        };
        state.candidateId =
          CandidateProtocol.generateCandidateId(answers);
        // Wipe inputs so raw answers do not linger in the DOM after leave.
        $("#q-maiden").value = "";
        $("#q-birthday").value = "";
        $("#q-street").value = "";
        $("#candidate-preview").textContent =
          "Linking ID ready (16-char). It will be attached to your responses only.";
        showPanel("panel-survey");
      } catch (err) {
        setStatus(err.message || String(err), true);
      }
    });

    $("#survey-form").addEventListener("submit", function (evt) {
      evt.preventDefault();
      setStatus("");
      if (!allLikertAnswered()) {
        setStatus("Please answer every item before continuing.", true, "survey");
        return;
      }
      if (!CandidateProtocol.isValidCandidateId(state.candidateId)) {
        setStatus(
          "Missing CANDIDATE ID — return to security questions.",
          true,
          "survey"
        );
        return;
      }
      state.answers = collectLikert();
      state.completedAt = new Date().toISOString();
      finalize();
    });
  }

  function finalize() {
    var record = buildResearchRecord();

    // Local download for researcher pipelines that ingest browser exports,
    // OR post to university Qualtrics embedded data / campus endpoint.
    // Never include survey_code here.
    try {
      downloadJson(record);
    } catch (e) {
      console.warn("Download skipped:", e);
    }

    // Stash record for optional on-page confirmation (still no survey_code).
    try {
      sessionStorage.setItem(
        "wave1_research_record",
        JSON.stringify(record)
      );
    } catch (e) {
      /* ignore */
    }

    $("#final-candidate").textContent = state.candidateId;
    showPanel("panel-complete");

    // Automated SONA credit redirect (anonymous). After credit, participant
    // may optionally open unlinked Form B (separate origin / tool).
    var delayMs = 2500;
    var formB = STUDY.formBUrl;
    $("#btn-form-b").href = formB;

    if (state.surveyCode) {
      setStatus(
        "Awarding SONA credit anonymously… you will be redirected shortly.",
        false,
        "complete"
      );
      window.setTimeout(function () {
        try {
          SonaPassthrough.redirectToSonaCredit(state.surveyCode, STUDY.sona);
        } catch (err) {
          setStatus(
            "Credit redirect failed: " +
              err.message +
              ". Use Form B only if invited; contact the researcher for credit.",
            true,
            "complete"
          );
        }
      }, delayMs);
    } else {
      setStatus(
        "Preview mode: no SONA redirect. Open Form B if you wish to leave contact info separately.",
        false,
        "complete"
      );
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
