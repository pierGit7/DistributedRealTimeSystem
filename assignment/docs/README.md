# 02225 Distributed Real-Time Systems (DRTS) Project: Hierarchical Scheduling Analysis

## Overview

This project focuses on the modeling, simulation, and schedulability analysis of a real-time system (e.g., an Advanced Driver-Assistance System - ADAS) implemented on a multicore platform using a hierarchical scheduling framework. The system comprises tasks with different criticality levels (hard periodic, soft sporadic) assigned to components, which are in turn mapped to potentially heterogeneous cores.

The primary goal is to develop a simulator to observe the system's runtime behavior and an analysis tool to formally verify its schedulability using compositional techniques based on the Bounded Delay Resource (BDR) model.

## Core Objectives

1.  **Model the System:** Define the hardware platform (multicore with varying speeds), the application (tasks with periods, WCETs, deadlines), the hierarchical structure (task-to-component assignments), and component-to-core mappings.
2.  **Develop a Simulator:**
    *   Simulate the execution of tasks within the hierarchical scheduling framework on each core.
    *   Implement scheduling policies (EDF, FPS/RM) within components.
    *   Model resource supply between hierarchical levels using *initial* parameters (e.g., derived from `budgets.csv`).
    *   Report simulation results, including observed task response times (average, maximum) and resource utilization metrics.
3.  **Develop an Analysis Tool:**
    *   Implement compositional schedulability analysis based on the BDR model.
    *   **Calculate** the BDR interface parameters (`(alpha, delta)`) for each component based on its internal workload and scheduling policy, ensuring the Supply Bound Function (SBF) meets the Demand Bound Function (DBF).
    *   Use these calculated interfaces to check the schedulability of the overall hierarchical system.
    *   Report the schedulability analysis results for each task and component.
4.  **Compare Results:** Analyze and compare the results obtained from the simulator and the analysis tool.

## System Model Details

*   **Hardware:** Multicore platform. Cores can have different `speed_factor`s affecting task WCETs. (`architecture.csv`)
*   **Application:** Set of hard periodic tasks and soft sporadic tasks (represented by minimum inter-arrival times). Tasks have WCET, period/MIT, and deadline parameters. (`tasks.csv`)
*   **Scheduling:**
    *   Hierarchical scheduling framework per core.
    *   Components can use either **EDF** or **Fixed-Priority Preemptive Scheduling (FPS)** (using Rate Monotonic priority assignment). (`tasks.csv`, `budgets.csv`)
    *   Resource supply between parent and child components is modeled using the **Bounded Delay Resource (BDR)** model.
*   **Mapping:** Tasks are statically assigned to components, and components are statically assigned to cores. (`tasks.csv`, `budgets.csv`)

## Key Analysis Techniques (Based on "Hierarchical Scheduling" Chapter, Section 3.3)

The analysis tool should implement the following concepts from the provided handbook chapter:

1.  **Demand Bound Function (DBF):**
    *   `dbf_EDF(W, t)` for EDF-scheduled components (Eq. 2 or 3).
    *   `dbf_RM(W, t, i)` for RM-scheduled components (Eq. 4).
2.  **Supply Bound Function (SBF):**
    *   `sbf_BDR(R, t)` for the BDR model `R = (alpha, delta)` (Eq. 6).
3.  **Schedulability Check:** For each component, verify that its calculated DBF is less than or equal to the SBF provided by its BDR interface (`dbf(W, t) <= sbf_BDR(R, t)` for relevant `t`). The analysis tool needs to determine the appropriate BDR parameters `(alpha, delta)` for each component interface that satisfy this condition.
4.  **Hierarchical Composition:**
    *   Use **Theorem 1** to check if a set of child component BDR interfaces can be scheduled by a parent BDR interface.
    *   Use **Theorem 3 (Half-Half Algorithm)** to convert a calculated BDR interface `(alpha, delta)` into equivalent periodic resource supply task parameters (Budget `C_supply`, Period `T_supply`) if needed for simulation or analysis at the parent level. *Note: This theorem converts an interface to a task, it's not used to calculate the interface itself.*

## Input and Output

*   **Input:** The system model is defined via CSV files:
    *   `tasks.csv`: Defines tasks, their parameters, and component assignment.
    *   `architecture.csv`: Defines cores and their speed factors.
    *   `budgets.csv`: Defines initial component budgets/periods (primarily for the simulator setup) and component-to-core mapping.
*   **Output:** The tools should produce meaningful output. A suggested format is `solution.csv` (see provided `README.md` for details), reporting:
    *   Task schedulability (from analysis tool).
    *   Component schedulability (from analysis tool).
    *   Observed response times (avg/max, from simulator).

*Flexibility:* Students can adapt the input/output formats as needed, ensuring clear documentation.

## Optional Extensions

*   Worst-Case Response Time (WCRT) analysis within the hierarchical framework.
*   Exploration of other resource models (PRM, EDP).
*   Modeling and analysis of inter-task communication delays.
*   System optimization (core assignment, BDR parameter tuning).

## References

*   Main Reference: Chapter "Hierarchical Scheduling", Section 3 in *Handbook of Real-Time Computing*, 2022. (Available on DTU Learn)
*   General Concepts: Chapter "Periodic Task Scheduling" in *Hard Real-Time Computing Systems*. (Available on DTU Learn)
