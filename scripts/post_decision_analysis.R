#!/usr/bin/env Rscript
# Post-decision R analysis: run automatically when BF threshold is reached.
# Args: data_path (CSV of responses), study_id (UUID).
# CSV columns: response_id, session_id, created_at, payload (JSON string).
# Replace this stub with your own analysis (e.g. BayesFactor, summaries, exports).

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("Usage: Rscript post_decision_analysis.R <data_path> <study_id>")
}
data_path <- args[1]
study_id   <- args[2]

if (!file.exists(data_path)) {
  stop("Data file not found: ", data_path)
}

data <- read.csv(data_path, stringsAsFactors = FALSE)
n    <- nrow(data)
message("Study ", study_id, ": N = ", n, " responses")

# Stub: add your analysis here (e.g. Bayesian models, vignette-level BFs, exports).
# Example: write a summary to a file, or run BayesFactor and save results.
# output_dir <- file.path(Sys.getenv("MEDIA_ROOT", "."), "post_decision", study_id)
# dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
# saveRDS(list(n = n, timestamp = Sys.time()), file.path(output_dir, "summary.rds"))

quit(status = 0)
