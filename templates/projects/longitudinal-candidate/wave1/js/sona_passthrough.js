/**
 * SONA Systems anonymous survey_code pass-through.
 *
 * Flow
 * ----
 * 1. Researcher configures the SONA study "Survey URL" as:
 *      https://your-host/.../wave1/index.html?survey_code=%SURVEY_CODE%
 *    SONA replaces %SURVEY_CODE% with the participant's anonymous credit code.
 *
 * 2. On load, this module captures `survey_code` from the query string and
 *    keeps it in an in-memory session object (and sessionStorage as a soft
 *    backup for mid-survey refresh). It is NEVER written into the research
 *    response payload / CSV / JSON download.
 *
 * 3. At completion, buildSonaCreditUrl() returns the official credit URL:
 *      .../redirect_credit.aspx?experiment_id=XXX&credit_token=YYY&survey_code=XXXX
 *
 * Privacy
 * -------
 * - survey_code is an opaque SONA credit token, not a name/email/student ID.
 * - It must not be co-stored with CANDIDATE IDs or survey answers in any
 *   researcher-controlled table (avoids a re-identification bridge).
 */
(function (global) {
  "use strict";

  var STORAGE_KEY = "sona_survey_code_session";

  /**
   * @typedef {Object} SonaConfig
   * @property {string} baseCreditUrl  e.g. https://nicholls.sona-systems.com/redirect_credit.aspx
   * @property {string} experimentId   SONA experiment / study ID
   * @property {string} creditToken    SONA credit completion token
   */

  /** Default placeholders — replace before fielding. */
  var DEFAULT_CONFIG = {
    baseCreditUrl: "https://YOUR-SCHOOL.sona-systems.com/redirect_credit.aspx",
    experimentId: "XXX",
    creditToken: "YYY",
  };

  function getQueryParam(name) {
    var params = new URLSearchParams(global.location.search);
    var value = params.get(name);
    return value == null ? "" : String(value).trim();
  }

  /**
   * Capture survey_code on load. Prefer live URL; fall back to sessionStorage
   * only within the same browser tab session (soft resume after refresh).
   */
  function captureSurveyCode() {
    var fromUrl = getQueryParam("survey_code");
    if (fromUrl) {
      try {
        sessionStorage.setItem(STORAGE_KEY, fromUrl);
      } catch (e) {
        /* private mode / blocked storage — in-memory only */
      }
      return fromUrl;
    }
    try {
      return sessionStorage.getItem(STORAGE_KEY) || "";
    } catch (e) {
      return "";
    }
  }

  function clearSurveyCode() {
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      /* ignore */
    }
  }

  /**
   * Build the SONA credit completion URL.
   * Official pattern (Sona Systems external survey integration):
   *   {base}/redirect_credit.aspx?experiment_id={id}&credit_token={token}&survey_code={code}
   */
  function buildSonaCreditUrl(surveyCode, config) {
    var cfg = Object.assign({}, DEFAULT_CONFIG, config || {});
    if (!surveyCode) {
      throw new Error(
        "Missing survey_code — cannot award SONA credit anonymously."
      );
    }
    var url = new URL(cfg.baseCreditUrl);
    url.searchParams.set("experiment_id", cfg.experimentId);
    url.searchParams.set("credit_token", cfg.creditToken);
    url.searchParams.set("survey_code", surveyCode);
    return url.toString();
  }

  /**
   * Immediate terminal redirect. Call only after research data is finalized
   * and exported / queued — survey_code is passed solely to SONA.
   */
  function redirectToSonaCredit(surveyCode, config) {
    var target = buildSonaCreditUrl(surveyCode, config);
    // Clear local soft copy so a later Form B visit cannot bind credit codes.
    clearSurveyCode();
    global.location.replace(target);
  }

  global.SonaPassthrough = {
    DEFAULT_CONFIG: DEFAULT_CONFIG,
    captureSurveyCode: captureSurveyCode,
    clearSurveyCode: clearSurveyCode,
    buildSonaCreditUrl: buildSonaCreditUrl,
    redirectToSonaCredit: redirectToSonaCredit,
    getQueryParam: getQueryParam,
  };
})(typeof window !== "undefined" ? window : globalThis);
