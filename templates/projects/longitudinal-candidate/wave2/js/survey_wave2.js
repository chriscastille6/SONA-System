/**
 * Wave 2 survey — same CANDIDATE questions, no SONA survey_code handling.
 * Linking across waves is performed offline by matching candidate_id only.
 */
(function () {
  "use strict";

  var STUDY = {
    title: "Longitudinal Study — Wave 2",
    irbProtocol: "IRB-XXXX-YYYY",
    wave: 2,
  };

  var state = {
    candidateId: "",
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

  function setStatus(msg, isError) {
    var el = $("#status-line");
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

  function buildResearchRecord() {
    return {
      schema: "longitudinal-candidate/v1",
      study_irb: STUDY.irbProtocol,
      wave: STUDY.wave,
      candidate_id: state.candidateId,
      started_at: state.startedAt,
      completed_at: state.completedAt,
      responses: state.answers,
    };
  }

  function downloadJson(record) {
    var blob = new Blob([JSON.stringify(record, null, 2)], {
      type: "application/json",
    });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download =
      "wave2_" + record.candidate_id + "_" + Date.now() + ".json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  }

  document.addEventListener("DOMContentLoaded", function () {
    state.startedAt = new Date().toISOString();

    $("#btn-consent-yes").addEventListener("click", function () {
      showPanel("panel-candidate");
    });
    $("#btn-consent-no").addEventListener("click", function () {
      showPanel("panel-declined");
    });

    $("#candidate-form").addEventListener("submit", function (evt) {
      evt.preventDefault();
      setStatus("");
      try {
        state.candidateId = CandidateProtocol.generateCandidateId({
          motherMaidenInitials: $("#q-maiden").value,
          birthDayOfMonth: $("#q-birthday").value,
          childhoodStreetInitials: $("#q-street").value,
        });
        $("#q-maiden").value = "";
        $("#q-birthday").value = "";
        $("#q-street").value = "";
        showPanel("panel-survey");
      } catch (err) {
        setStatus(err.message || String(err), true);
      }
    });

    $("#survey-form").addEventListener("submit", function (evt) {
      evt.preventDefault();
      if (!allLikertAnswered()) {
        setStatus("Please answer every item before continuing.", true);
        return;
      }
      state.answers = collectLikert();
      state.completedAt = new Date().toISOString();
      var record = buildResearchRecord();
      downloadJson(record);
      $("#final-candidate").textContent = state.candidateId;
      showPanel("panel-complete");
      setStatus("Wave 2 saved locally. Thank you.");
    });
  });
})();
