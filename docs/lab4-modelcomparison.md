# Lab 4 — Model comparison: gpt-4o-mini vs gpt-4o

**Cohort member:** _<Shyamal>_
**Date:** _<09/09/2026>_

## Numbers (filled in by `scripts/compare_models.py`)

```
Model            n    Total $     Avg $/q     Time
---------------------------------------------------
gpt-4o-mini     10     0.000765   0.000077     14.64s 
gpt-4o          10     0.015277   0.001528     21.78s 
```

> gpt-4o cost _20.0x more than gpt-4o-mini on the same questions.

## Two-paragraph eyeball reflection

### Paragraph 1 — where the gap mattered

Question file contained word "text" only as question. Below is the response both model provided
gpt-4o-mini-It seems you entered the word "text." Could you please clarify what specific information or question you have in mind? I'm here to help with any queries you may have!  
gpt-40-  "Text" generally refers to any block of written words, whether it be a book, article, message, or document. It is the primary method of conveying information in written language. Text can be used to 

gpt-4o-mini response is more meaning ful. 

### Paragraph 2 — your rough rule for when to reach for the bigger model

_Write 3–5 sentences. Based on what you saw, what kind of question would
make you switch to `gpt-4o`? What's the cost story you'd defend at Design
Review #1 if a stakeholder asked "why aren't you using the more capable
model for everything"?_

Decision to use bigger/costilier model depends on the business use case. 
If requirement is getting met with the smaller/cheaper models without much compromise on the
accuracy and performance should opt for those. 
After decision is made about certain model it is continous process to continue evaluate the choosen model 
with other models in order to take advantage of new changes. 

## Confidence calibration (optional)

The lab pipeline asks the model to return a `confidence` value in `[0, 1]`.
Skim the persisted rows in SQLite:

```bash
sqlite3 data/answers.db \
  "SELECT model, AVG(confidence), AVG(cost_usd) FROM answers GROUP BY model;"
```
 Model       |   Avg Confidence |    Avg Cost |
+=============+==================+=============+
| gpt-4o      |         0.930385 | 0.00154726  |
+-------------+------------------+-------------+
| gpt-4o-mini |         0.903509 | 7.64947e-05 

Note :GPT-4o-mini is actually much cheaper, Python displayed cost in scientific notation.

Do the two models report similar confidence on the same questions, or do
they disagree on what they know? One sentence is enough.
gpt-4o confidence is on higher side nominally but still obervation is that mini's explanation is more meaning full and concise. 