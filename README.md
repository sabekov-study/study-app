# SABEKOV Study App

This Django Web App aims to allow study workers of a manual large-scale field
test to systematically process a catalogue of questions and tests on each study
target and document the results.


## Why this exists

Back in 2017, we wrote this tool for our intended [SABEKOV study](https://github.com/sabekov-study/sabekov-catalogue).
We needed an app that guided our study workers through the very extensive
[question and test catalogue](https://github.com/sabekov-study/sabekov-catalogue) in a smart way and quickly documented their findings.
We designed the study to crass-validate the findings by multiple testers,
therefore we wanted an app that handles and notifies about the agreement of testers.

In all the existing survey apps we could not find something that met our
demand.
Since our study was not strictly a survey at all, but the study workers
performed tasks on a set of field study targets – in our case websites – the
conventional survey data model did not fit at all.

Long story short: We did not find a tool to perform and document guided field
studies on websites, then we wrote this one.


## Status

Since our study in 2017 the tool has not been maintained.
We are happy to welcome interested contributors to revive the project.
