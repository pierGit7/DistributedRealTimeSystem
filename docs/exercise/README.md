# Exercise

## Update March 10th:

### Exercise Report Guidelines:

For the exercise report, please upload a PDF focusing on VSS and RTA implementation results and their comparison. Include discussion on how simulation results compare to theoretical analysis. There are no specific formatting or length requirements — just document your results.

In addition, submit the source code and the test cases with the results in a ZIP file with a clear README on how to run it.

**Solution examples:**
We will add by next Friday in the GitHub repo below a few example solutions for the RTA so you can check your analysis code. (The simulation will give different results depending on how long you run it and what assumptions you make, so it does not make sense to provide a solution for that.)

**Note:** A small mistake in the three small exercise test cases provided on DTU Learn has been fixed: the columns WCET and BCET were swapped compared to the test cases in the GitHub repo.

---

## Update March 7th:

You may use this tool to generate test cases for the exercise:

[Taskset Generator Exercise](https://github.com/Plyncesilva/Taskset-Generator-Exercise)

We have already shared three simple test cases. The TAs will generate extra test cases with the tool and share them via the GitHub repo above.

Please see the exercise description on Overleaf.

---

## If you have questions:

Start by asking Google Gemini as follows:

1. Login to [Google AI Studio](https://aistudio.google.com) (you will need a Google account).
2. At the bottom, click on "+" and then select "My Drive."
3. Add this Google Drive shared folder link (with materials about the exercise):  
   [Exercise Materials Folder](https://drive.google.com/drive/folders/1hcgpKI-Kizq82VjRzAQ5-0xyGE9hCMOB?usp=share_link)
4. Select "Gemini 2.0 Flash Thinking Experimental 01-21" in the panel to the right.
5. Ask your question and hit "Run."

The files in the Exerercise/Content tab are test cases are provided as a starting point for the 02225 DRTS exercise.

They are in CSV (Comma-Separated Values) format and contain the model parameters for periodic tasks:
  
  - Task: Task name
  - BCET: Best-case execution time
  - WCET: Worst-case execution time
  - Period: Task period
  - Deadline: Task deadline (equal to the period)
  - Priority: Task priority (assigned by Rate Monotonic scheduling, with lower period yielding higher priority)

These examples illustrate one possible format. Students may use a different format and create additional test cases.
