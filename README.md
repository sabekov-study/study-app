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


## Getting Started

This assumes you have done all the basic Django setup like setup a database and
applied the migrations. Please check the Django documentation for that.

**Warning**: The Django settings in this repo are not safe for productive use.
Please check the Django documentation on production settings.

### Import Checklist

The each initial checklist has to imported from the command line.
After that you can update the checklist via the web interface.

To import a new checklist run

```
$ ./manage.py import_checklist path/to/checklist.json
```

The JSON file has to be provided in the _Checklist Data Format_ described below.

### Import Site Listing

The survey tool is designed to apply the question catalogue (checklist) to a list of websites.
Site listings have to be imported over a management command.

To import a new site listing run

```
./manage.py import_listing path/to/listing MYLISTING 2017-10-02
```

The date information can be used to track multiple issues of the same site listing.

The data format of the listing is a newline-separated file of site domain names. For instance

```
archive.org
example.com
wikipedia.org
```


### Setup Admin User

If not done already, setup an admin user with `./manage.py createsuperuser`.
You will use this user to create all non-admin users for your study via the
_Django admin_ interface (see top navigation after login).


## Checklist Data Format

The checklist format basically defines the catalogue of questions which are organised in subcatalogues (aka subcategories) of questions.
There are high-level subcatalogues that sequentially make up the checklist in the order defined in the `steps` lists
and there are lower-level subcatalogues are meant to contain questions that need to be answered repeatedly in various contexts.
These latter subcatalogues can therefore be included by other catalogues through the `reference` field explained later.

Additionally, the checklist may contain a `name` and a `version` information.

```json
{
   "name" : "my checklist",
   "steps" : [
      "ACCESS",
      ...
   ],
   "subcategories" : {
      "ACCESS" : [
         {
            "answer_type" : "selection",
            "answers" : [
               "yes",
               "_no_"
            ],
            "comment" : null,
            "label" : "ACCESS_DARK",
            "question" : "Does the site support dark mode?",
            "reference" : null
         },
         ...
      ]
   },
   "version" : "0.1.0"
}
```

### Question Format

The heart of the checklist are the questions.
Questions vary based on the answer type which defines how the testers can answer a question.

The following answer types are supported:

- `input`: Testers can input data in an input field
- `selection`: Answer is a (single) selected item from a given list of possible answers
- `multiselection`: Answer one or multiple selected item(s) from a given list of possible answers
- `null`: A special type only used when a question includes (refers to) a subcatalogue.
  Then the actual answer type is determined by the entry question of the referenced subcatalogue.

The basic question format looks like this:

```json
{
    "question" : "Does the site have an imprint?",
    "answer_type" : "selection",
    "answers" : [
        "yes",
        "_no_"
    ],
    "comment" : "Look at the bottom",
    "label" : "IMPRINT",
    "reference" : null
}
```

The following explains the meaning of each question object field:

- `question`: Arbitrary question text shown to the testers
- `answer_type`: One of the answer types named above
- `answers`: This is depending on `answer_type`:
  - `input`: TODO
  - `selection` or `multiselection`: List of strings with possible answers. Answers surrounded by underscores (e.g., `"_none_"`) are interpreted as _negative answer_ (TODO).
  - `null`: TODO
- `comment`: Arbitrary comment to instruct the testers
- `label`: Short textual identifier for the question. Labels are hierarchical with underscores (`_`) separating the hierarchical levels (e.g., `NAV_ACCESS` is a sub-question to `NAV`).
- `reference`: Label of a (sub-)catalogue that is included at this point

### Reference Questions

Reference questions are a special type of question that are used to include subcatalogues.
They use the `reference` field to point to a label of the referenced subcatalogue.
All other fields of the question can be `null` as they are taken from the entry question of the referred catalogue.

An entry question is the question of a subcatalogue that has the same label as the subcatalogue.
Entry questions are optional for a catalogue.
If none are given, then there will be no question with the label of the reference question.


### Shortcut Questions

Shortcut questions are another special type of questions which shortcut their hierarchical sub-questions if the are answered negatively.
They have to be selection questions where a subset of answer options are marked as negative by surrounding underscores.
If such questions are answered with a negative answer then their sub-questions are skipped.


### Complete Example


```json
{
   "name" : "my checklist",
   "steps" : [
      "HOME"
   ],
   "subcategories" : {
      "ACCESS" : [
         {
            "answer_type" : "selection",
            "answers" : [
               "yes",
               "_no_"
            ],
            "comment" : null,
            "label" : "ACCESS_RESIZE",
            "question" : "Is the content resizeable by Ctrl+Plus?",
            "reference" : null
         },
         {
            "answer_type" : "input",
            "answers" : "int",
            "comment" : null,
            "label" : "ACCESS_FONTSIZE",
            "question" : "What is the default font size?",
            "reference" : null
         }
      ],
      "HOME" : [
         {
            "answer_type" : "input",
            "answers" : "int foo",
            "comment" : null,
            "label" : "HOME_URL",
            "question" : "What is the home page URL?",
            "reference" : null
         },
         {
            "answer_type" : null,
            "answers" : null,
            "comment" : null,
            "label" : "HOME_ACCESS",
            "question" : null,
            "reference" : "ACCESS"
         },
         {
            "answer_type" : "selection",
            "answers" : [
               "yes",
               "_no_"
            ],
            "comment" : null,
            "label" : "HOME_NAV",
            "question" : "Does the site have visible nativgation?",
            "reference" : null
         },
         {
            "answer_type" : "multiselection",
            "answers" : [
               "top",
               "left",
               "right",
               "bottom"
            ],
            "comment" : "look careful",
            "label" : "HOME_NAV_POS",
            "question" : "Where is the main navigation?",
            "reference" : null
         },
         {
            "answer_type" : null,
            "answers" : null,
            "comment" : null,
            "label" : "HOME_NAV_ACCESS",
            "question" : null,
            "reference" : "ACCESS"
         }
      ]
   },
   "version" : "0.1.0"
}
```
